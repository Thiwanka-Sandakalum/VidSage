
from fastapi import APIRouter, HTTPException, status, Depends
from models import SearchRequest, SearchResponse, ErrorResponse, SearchResult
from services.mongodb_vector_store import MongoDBVectorStoreManager
from typing import Optional
from utils.auth import get_current_user_id

router = APIRouter()
mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager):
    global mongodb_manager
    mongodb_manager = manager

@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def search_video(request: SearchRequest, user_id: str = Depends(get_current_user_id)):
    global mongodb_manager
    if mongodb_manager is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MongoDB manager not initialized."
        )
    try:
        if not mongodb_manager.video_exists(request.video_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {request.video_id} not found. Process it first using /process endpoint."
            )
        search_results = mongodb_manager.search_video(
            video_id=request.video_id,
            query=request.query,
            top_k=request.top_k,
            user_id=user_id
        )
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )
