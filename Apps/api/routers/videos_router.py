from fastapi import APIRouter, HTTPException, status, Depends, Body
from typing import Optional
from services.mongodb_vector_store import MongoDBVectorStoreManager
from models import ListVideosResponse, ErrorResponse, VideoMetadata
from utils.auth import get_current_user_id

router = APIRouter()
mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager: MongoDBVectorStoreManager) -> None:
    global mongodb_manager
    mongodb_manager = manager

# Save video endpoint
@router.post(
    "/videos/save",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def save_video(
    video_id: str = Body(..., embed=True, description="YouTube video ID to save"),
    user_id: str = Depends(get_current_user_id)
):
    global mongodb_manager
    if mongodb_manager is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MongoDB manager not initialized."
        )
    try:
        video_metadata = mongodb_manager.get_video_metadata(video_id)
        if not video_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found. Process it first using /process endpoint."
            )
        # Add user to video users list if not already present
        if user_id not in video_metadata.get("users", []):
            mongodb_manager.videos_collection.update_one(
                {"video_id": video_id},
                {"$addToSet": {"users": user_id}}
            )
        return {"status": "saved", "video_id": video_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving video: {str(e)}"
        )

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from services.mongodb_vector_store import MongoDBVectorStoreManager
from models import ListVideosResponse, ErrorResponse, VideoMetadata
from utils.auth import get_current_user_id
from services.mongodb_vector_store import MongoDBVectorStoreManager

router = APIRouter()
mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager: MongoDBVectorStoreManager) -> None:
    global mongodb_manager
    mongodb_manager = manager

@router.get(
    "/videos",
    response_model=ListVideosResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def list_videos(user_id: str = Depends(get_current_user_id)):
    global mongodb_manager
    if mongodb_manager is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MongoDB manager not initialized."
        )
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
    if mongodb_manager is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MongoDB manager not initialized."
        )
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
