"""Statistics endpoint."""

from fastapi import APIRouter, HTTPException, status, Depends
import logging

from src.api.dependencies import get_mongodb_manager
from src.schemas import ErrorResponse
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager

router = APIRouter(prefix="/stats", tags=["stats"])
logger = logging.getLogger(__name__)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get system statistics",
    description="Get statistics about processed videos and embeddings",
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def get_stats(
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    """
    Get system-wide statistics.
    
    Returns:
        - total_videos: Total number of processed videos
        - total_chunks: Total number of chunks across all videos
        - total_users: Total number of unique users
    """
    try:
        stats = mongodb_manager.get_stats()
        return stats
    except Exception as e:
        logger.exception(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )
