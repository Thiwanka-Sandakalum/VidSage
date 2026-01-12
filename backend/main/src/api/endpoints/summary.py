from fastapi import APIRouter, HTTPException, status, Depends
from src.core.security import get_current_user_id
from src.api.dependencies import get_mongodb_manager
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager
from src.schemas import ErrorResponse

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get(
    "/{video_id}/summary",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get video summary",
    description="Retrieve the pre-generated summary for a processed video.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def get_video_summary(
    video_id: str,
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    """
    Retrieve the pre-generated summary for a processed video.
    """
    video_metadata = mongodb_manager.get_video_metadata(video_id)
    if not video_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
    # if user_id not in video_metadata.get("users", []):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this video.")
    summary = video_metadata.get("summary", "No summary available.")
    return {"video_id": video_id, "summary": summary}
