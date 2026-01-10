from fastapi import APIRouter, HTTPException, status, Depends
from models import GenerateRequest, GenerateResponse, ErrorResponse, SourceChunk
from services.mongodb_vector_store import MongoDBVectorStoreManager
from services.generation_service import get_generation_service
from services.cache_service import get_cache_service
from typing import Optional
from utils.auth import get_current_user_id
import logging
import config

logger = logging.getLogger(__name__)

router = APIRouter()
mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager):
    global mongodb_manager
    mongodb_manager = manager

@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def generate_answer(request: GenerateRequest, user_id: str = Depends(get_current_user_id)):
    global mongodb_manager
    if mongodb_manager is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MongoDB manager not initialized."
        )
    try:
        # Check cache first
        cache_service = get_cache_service()
        cached_response = cache_service.get(request.video_id, request.query)
        if cached_response:
            logger.info(f"✅ Returning cached response for: {request.query[:50]}...")
            return cached_response
        # Video existence check
        if not mongodb_manager.video_exists(request.video_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {request.video_id} not found. Process it first using /process endpoint."
            )
        
        # Check if user has access to this video
        if not mongodb_manager.user_has_video(user_id, request.video_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have access to this video."
            )
        # Search for relevant chunks (reduced to minimize API quota usage)
        search_results = mongodb_manager.search_video(
            video_id=request.video_id,
            query=request.query,
            top_k=request.top_k
        )
        if not search_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No relevant content found for query: '{request.query}'"
            )
        # Get video metadata
        video_metadata = mongodb_manager.get_video_metadata(request.video_id)
        video_title = video_metadata.get("title", "Unknown Video")
        # Generate answer
        generation_service = get_generation_service()
        answer = generation_service.generate_answer(
            query=request.query,
            chunks=search_results,
            video_title=video_title
        )
        # Prepare sources (only top requested results)
        sources = generation_service.prepare_sources(search_results[:request.top_k])
        source_chunks = [
            SourceChunk(
                chunk_id=src["chunk_id"],
                relevance_score=src["relevance_score"],
                text_preview=src["text_preview"]
            )
            for src in sources
        ]
        response = GenerateResponse(
            answer=answer,
            sources=source_chunks,
            model=config.LLM_MODEL
        )
        # Cache the response
        cache_service.set(request.video_id, request.query, response, ttl_minutes=30)
        logger.info(f"💾 Cached response for: {request.query[:50]}...")
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation error: {str(e)}"
        )
