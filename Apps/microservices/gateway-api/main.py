"""Gateway API - Main API that orchestrates microservices."""

import os
import sys
import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.config import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    GENERATION_SERVICE_URL
)
from shared.models import (
    ProcessVideoRequest,
    ProcessVideoResponse,
    JobStatus,
    JobStatusResponse,
    GenerateRequest,
    GenerateResponse,
    ErrorResponse
)
from shared.utils import extract_video_id, InvalidYouTubeURLError
from shared.rabbitmq_utils import publish_event


# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway-api")

app = FastAPI(
    title="VidSage Gateway API",
    description="API Gateway for VidSage microservices architecture",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code} for {request.method} {request.url}")
    return response

# MongoDB client (lazy initialization)
mongodb_client = None


def get_mongodb_client():
    """Get or create MongoDB client."""
    global mongodb_client
    if mongodb_client is None:
        logger.debug(f"Creating new MongoDB client connection to: {MONGODB_URI}")
        mongodb_client = MongoClient(MONGODB_URI)
        logger.info("MongoDB client created successfully")
    return mongodb_client


def get_jobs_collection():
    """Get jobs collection from MongoDB."""
    logger.debug("Accessing jobs collection from MongoDB")
    client = get_mongodb_client()
    db = client[MONGODB_DB_NAME]
    return db["jobs"]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    logger.info("Root endpoint accessed.")
    return {
        "message": "VidSage Gateway API - Microservices Architecture",
        "version": "2.0.0",
        "architecture": "Microservices with Queue + API Communication",
        "services": {
            "transcript": "queue-worker-only",
            "embedding": "queue-worker-only", 
            "generation": GENERATION_SERVICE_URL
        },
        "endpoints": {
            "/api/v1/videos/process": "POST - Process YouTube video (async)",
            "/api/v1/videos/{job_id}/status": "GET - Check processing status",
            "/api/v1/chat/generate": "POST - Generate AI answers using RAG",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint accessed.")
    # Check MongoDB
    try:
        client = get_mongodb_client()
        client.admin.command('ping')
        mongodb_status = "connected"
        logger.debug("MongoDB connection successful.")
    except Exception as e:
        mongodb_status = "disconnected"
        logger.error(f"MongoDB connection failed: {e}")
    # Check microservices (only generation service has API)
    services_status = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Only check generation service since transcript and embedding are queue-only workers
        try:
            response = await client.get(f"{GENERATION_SERVICE_URL}/health")
            services_status["generation"] = "healthy" if response.status_code == 200 else "unhealthy"
            logger.debug(f"generation health: {services_status['generation']}")
        except Exception as e:
            services_status["generation"] = "unreachable"
            logger.error(f"generation health check failed: {e}")
            
        # Note: transcript and embedding services are queue-only workers (no REST API)
        services_status["transcript"] = "queue-worker-only"
        services_status["embedding"] = "queue-worker-only"
    return {
        "status": "healthy",
        "gateway": "operational",
        "mongodb": mongodb_status,
        "services": services_status
    }


@app.post(
    "/api/v1/videos/process",
    response_model=ProcessVideoResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def process_video(request: ProcessVideoRequest):
    """
    Process a YouTube video (Step 1: Synchronous REST).
    """
    logger.info(f"/api/v1/videos/process called for user_id={request.user_id}, url={request.url}")
    try:
        # Extract video ID
        try:
            video_id = extract_video_id(request.url)
            logger.debug(f"Extracted video_id: {video_id}")
        except InvalidYouTubeURLError as e:
            logger.error(f"Invalid YouTube URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        # Check if video already exists
        logger.debug(f"Checking if video {video_id} already exists in database")
        jobs = get_jobs_collection()
        existing_job = jobs.find_one({
            "video_id": video_id,
            "status": JobStatus.COMPLETED
        })
        if existing_job:
            logger.info(f"Video already processed: {video_id} (job_id: {existing_job['_id']})")
            return ProcessVideoResponse(
                job_id=existing_job["_id"],
                video_id=video_id,
                status=JobStatus.COMPLETED,
                message="Video already processed"
            )
        logger.debug(f"Video {video_id} not found in database, proceeding with new job creation")
        # Create job
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job_doc = {
            "_id": job_id,
            "user_id": request.user_id,
            "video_url": request.url,
            "video_id": video_id,
            "status": JobStatus.PENDING,
            "current_step": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "error": None
        }
        jobs.insert_one(job_doc)
        logger.debug(f"Job created: {job_id}")
        # Asynchronous flow: publish a video.submitted event to Redis stream
        try:
            logger.debug(f"Updating job {job_id} status to TRANSCRIBING")
            jobs.update_one(
                {"_id": job_id},
                {"$set": {
                    "status": JobStatus.TRANSCRIBING,
                    "current_step": "submitted",
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            logger.debug("Job status updated successfully")
            
            # Publish event for downstream workers (transcript -> embedding)
            event_payload = {
                "job_id": job_id,
                "video_id": video_id,
                "video_url": request.url,
                "user_id": request.user_id
            }
            logger.debug(f"Publishing video.submitted event with payload: {event_payload}")
            publish_event("video.submitted", event_payload)
            logger.info(f"✅ Successfully published video.submitted event for job_id={job_id}")
            
            return ProcessVideoResponse(
                job_id=job_id,
                video_id=video_id,
                status=JobStatus.PENDING,
                message="Video submitted for asynchronous processing"
            )
        except Exception as e:
            jobs.update_one(
                {"_id": job_id},
                {"$set": {
                    "status": JobStatus.FAILED,
                    "current_step": "failed_submit",
                    "error": str(e),
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            logger.error(f"Failed to submit job for processing: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to submit job for processing: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /api/v1/videos/process: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@app.get(
    "/api/v1/videos/{job_id}/status",
    response_model=JobStatusResponse
)
async def get_job_status(job_id: str):
    """
    Get processing status for a job.
    """
    logger.info(f"/api/v1/videos/{job_id}/status called.")
    try:
        jobs = get_jobs_collection()
        job = jobs.find_one({"_id": job_id})
        if not job:
            logger.warning(f"Job {job_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        logger.debug(f"Job status: {job['status']} for job_id={job_id}")
        return JobStatusResponse(
            job_id=job["_id"],
            video_id=job["video_id"],
            status=job["status"],
            current_step=job.get("current_step"),
            chunk_count=job.get("chunk_count"),
            error=job.get("error"),
            created_at=job["created_at"],
            updated_at=job["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job status: {str(e)}"
        )


@app.post(
    "/api/v1/chat/generate",
    response_model=GenerateResponse
)
async def generate_answer(request: GenerateRequest):
    """
    Generate an answer using RAG (call Generation Service).
    """
    logger.info(f"/api/v1/chat/generate called for video_id={request.video_id}, query='{request.query}'")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GENERATION_SERVICE_URL}/generate",
                json=request.dict()
            )
            if response.status_code != 200:
                error_detail = response.json().get("detail", "Unknown error")
                logger.error(f"Generation service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
            logger.info("Generation service returned answer successfully.")
            return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation service error: {str(e)}"
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Service shutting down. Closing MongoDB client.")
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.debug("MongoDB client closed.")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Gateway API Service...")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
