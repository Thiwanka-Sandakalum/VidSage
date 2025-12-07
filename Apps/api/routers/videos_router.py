
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from models import ListVideosResponse, ErrorResponse, VideoMetadata
from services.mongodb_vector_store import MongoDBVectorStoreManager

router = APIRouter()
mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager):
    global mongodb_manager
    mongodb_manager = manager

@router.get(
    "/videos",
    response_model=ListVideosResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def list_videos(user_id: Optional[str] = None):
    global mongodb_manager
    try:
        videos_data = mongodb_manager.list_videos(user_id=user_id)
        videos = [
            VideoMetadata(
                video_id=v["video_id"],
                title=v.get("title", ""),
                chunks_count=v["chunks_count"],
                status=v.get("status", "completed")
            )
            for v in videos_data
        ]
        return ListVideosResponse(videos=videos)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing videos: {str(e)}"
        )

@router.delete(
    "/videos/{video_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def delete_video(video_id: str):
    global mongodb_manager
    try:
        if not mongodb_manager.video_exists(video_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        mongodb_manager.delete_video(video_id)
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting video: {str(e)}"
        )
