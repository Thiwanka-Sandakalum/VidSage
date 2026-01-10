import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

# Import new refactored modules
from src.core.config import get_settings
from src.core.exceptions import VidSageException
from src.infrastructure.database.mongodb import init_mongodb, close_mongodb
from src.api.middleware.error_handler import (
    vidsage_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from src.api.router import api_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown logic.
    """
    settings = get_settings()
    
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    try:
        # Initialize MongoDB
        init_mongodb(settings)
        logger.info("MongoDB initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
    yield  # Application runs
    
    # Shutdown
    logger.info("Shutting down application...")
    close_mongodb()
    logger.info("Shutdown complete")


# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## VidSage - AI-Powered YouTube Video Analysis
    
    A comprehensive RAG (Retrieval-Augmented Generation) pipeline API for processing YouTube videos, 
    extracting transcripts, performing semantic search, and generating AI-powered answers.
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    contact={
        "name": "VidSage API Support",
        "email": "support@vidsage.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and system status"
        },
        {
            "name": "videos",
            "description": "Video processing and management"
        },
        {
            "name": "search",
            "description": "Semantic search within video content"
        },
        {
            "name": "generate",
            "description": "AI-powered answer generation"
        },
        {
            "name": "stats",
            "description": "System statistics"
        },
        {
            "name": "suggestions",
            "description": "AI-generated question suggestions"
        },
        {
            "name": "integrations",
            "description": "External tool integrations (Google OAuth)"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Register exception handlers
app.add_exception_handler(VidSageException, vidsage_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API router
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    # Check if running in debug mode
    is_debugging = sys.gettrace() is not None
    
    if is_debugging:
        logger.info("Running in DEBUG mode (breakpoints enabled)")
        uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=False)
    else:
        logger.info("Running in DEVELOPMENT mode (auto-reload enabled)")
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.RELOAD
        )
