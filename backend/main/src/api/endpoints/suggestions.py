"""Suggestions endpoint for AI-generated questions."""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List
import logging

from src.api.dependencies import get_mongodb_manager
from src.schemas import ErrorResponse
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager

router = APIRouter(prefix="/suggestions", tags=["suggestions"])
logger = logging.getLogger(__name__)


class SuggestionsResponse(BaseModel):
    """Response model for suggested questions."""
    video_id: str = Field(..., description="YouTube video ID")
    questions: List[str] = Field(..., description="List of suggested questions")


@router.get(
    "/{video_id}",
    response_model=SuggestionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get suggested questions",
    description="Get AI-generated questions about a video",
    responses={
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def get_suggestions(
    video_id: str,
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    """
    Get AI-generated suggested questions for a video.
    
    - **video_id**: YouTube video ID
    
    Returns list of suggested questions to ask about the video.
    """
    try:
        # Check if video exists
        if not mongodb_manager.video_exists(video_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found. Process it first using /process endpoint."
            )
        
        # Get suggested questions
        suggestions = mongodb_manager.get_suggested_questions(video_id)
        
        return SuggestionsResponse(
            video_id=video_id,
            questions=suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving suggestions"
        )
