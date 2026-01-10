"""Search endpoint for semantic search."""

from fastapi import APIRouter, HTTPException, status, Depends
import logging

from src.core.security import get_current_user_id
from src.api.dependencies import get_mongodb_manager
from src.schemas import SearchRequest, SearchResponse, ErrorResponse, SearchResult
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search video content",
    description="Perform semantic search within a video's transcript",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def search_video(
    request: SearchRequest,
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    """
    Search for relevant content within a video using semantic search.
    
    - **video_id**: YouTube video ID to search in
    - **query**: Search query
    - **top_k**: Number of results to return (1-10)
    
    Returns ranked search results with relevance scores.
    """
    try:
        # Check if video exists
        if not mongodb_manager.video_exists(request.video_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {request.video_id} not found. Process it first using /process endpoint."
            )
        
        # Perform search
        search_results = mongodb_manager.search_video(
            video_id=request.video_id,
            query=request.query,
            top_k=request.top_k,
            user_id=user_id
        )
        
        # Format results
        formatted_results = [
            SearchResult(
                chunk_id=result["chunk_id"],
                text=result["text"],
                score=result["score"],
                metadata=result.get("metadata", {})
            )
            for result in search_results
        ]
        
        return SearchResponse(results=formatted_results)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error searching video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing search"
        )
