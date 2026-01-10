"""
Router for AI-generated suggestions (questions, topics, etc.)
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.mongodb_vector_store import MongoDBVectorStoreManager


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager: MongoDBVectorStoreManager):
    """Set the MongoDB manager for this router."""
    global mongodb_manager
    mongodb_manager = manager



class SuggestQuestionsRequest(BaseModel):
    """Request model for generating suggested questions."""
    video_id: str = Field(..., description="The YouTube video ID")
    count: int = Field(default=5, ge=1, le=10, description="Number of questions to generate")


class SuggestQuestionsResponse(BaseModel):
    """Response model for suggested questions."""
    video_id: str
    questions: List[str]
    count: int


@router.post("/questions", response_model=SuggestQuestionsResponse)
async def suggest_questions(request: SuggestQuestionsRequest):
    """
    Get pre-generated suggested questions for a video.
    
    Questions are generated once during video processing and stored
    in MongoDB, eliminating the need for real-time LLM calls.
    
    Args:
        request: Request containing video_id and optional count
        
    Returns:
        List of pre-generated questions about the video
        
    Raises:
        404: Video not found in database
        500: Error retrieving questions
    """
    global mongodb_manager
    try:
        logger.info(f"📝 Retrieving suggested questions for video: {request.video_id}")
        
        
        video_exists = mongodb_manager.video_exists(request.video_id)
        if not video_exists:
            logger.warning(f"❌ Video not found: {request.video_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video '{request.video_id}' not found in database"
            )
        
        
        questions = mongodb_manager.get_suggested_questions(request.video_id)
        
        if not questions:
            logger.warning(f"⚠️ No questions found for video: {request.video_id}")
            
            questions = [
                "What is this video about?",
                "What are the main points discussed?",
                "Can you summarize the key takeaways?",
                "What important topics are covered?",
                "What should I know from this video?"
            ]
        
        
        questions = questions[:request.count]
        
        logger.info(f"✅ Retrieved {len(questions)} questions for video: {request.video_id}")
        
        return SuggestQuestionsResponse(
            video_id=request.video_id,
            questions=questions,
            count=len(questions)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving suggestions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve suggestions: {str(e)}"
        )
