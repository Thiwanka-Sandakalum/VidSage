"""FastAPI dependencies for the API."""

from fastapi import Depends
from pymongo.database import Database

from src.core.config import Settings, get_settings
from src.core.security import get_current_user_id
from src.infrastructure.database.mongodb import get_mongodb
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager
from src.repositories.video_repository import VideoRepository
from src.repositories.embedding_repository import EmbeddingRepository
from src.repositories.vector_repository import VectorRepository
from src.services.generation_service import GenerationService, get_generation_service
from src.services.cache_service import CacheService, get_cache_service


# Configuration dependency
async def get_config(
    settings: Settings = Depends(get_settings)
) -> Settings:
    """Get application settings."""
    return settings


# Repository dependencies
def get_video_repository(
    db: Database = Depends(get_mongodb)
) -> VideoRepository:
    """Get video repository instance."""
    settings = get_settings()
    return VideoRepository(db, settings.MONGODB_VIDEOS_COLLECTION)


def get_embedding_repository(
    db: Database = Depends(get_mongodb)
) -> EmbeddingRepository:
    """Get embedding repository instance."""
    settings = get_settings()
    return EmbeddingRepository(db, settings.MONGODB_EMBEDDINGS_COLLECTION)


def get_vector_repository() -> VectorRepository:
    """
    Get vector repository instance.
    This wraps the infrastructure layer for clean architecture.
    """
    settings = get_settings()
    vector_store = MongoDBVectorStoreManager(
        api_key=settings.GOOGLE_API_KEY,
        mongodb_uri=settings.MONGODB_URI
    )
    return VectorRepository(vector_store)


# MongoDB Vector Store Manager (deprecated - use vector_repository instead)
def get_mongodb_manager() -> MongoDBVectorStoreManager:
    """
    Get MongoDB vector store manager.
    DEPRECATED: Use get_vector_repository() instead for clean architecture.
    """
    settings = get_settings()
    return MongoDBVectorStoreManager(
        api_key=settings.GOOGLE_API_KEY,
        mongodb_uri=settings.MONGODB_URI
    )


# Service dependencies
def get_generation_service_dep(
    vector_repo: VectorRepository = Depends(get_vector_repository),
    embedding_repo: EmbeddingRepository = Depends(get_embedding_repository),
    video_repo: VideoRepository = Depends(get_video_repository),
) -> GenerationService:
    """Get generation service with repository injection."""
    return GenerationService(vector_repo, embedding_repo, video_repo)


def get_cache_service_dep() -> CacheService:
    """Get cache service."""
    return get_cache_service()
