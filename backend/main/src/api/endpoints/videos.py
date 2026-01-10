"""Video processing and management endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends, Body, Path
from typing import Optional
import logging

from src.core.security import get_current_user_id
from src.core.exceptions import VideoNotFoundError, TranscriptError, ChunkingError, InvalidYouTubeURLError
from src.api.dependencies import get_mongodb_manager, get_generation_service_dep
from src.schemas import ProcessVideoRequest, ProcessVideoResponse, ErrorResponse, ListVideosResponse, VideoMetadata
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager
from src.services.generation_service import GenerationService
from src.services import transcript_service, chunk_service
from src.core import helpers

router = APIRouter(prefix="/videos", tags=["videos"])
logger = logging.getLogger(__name__)


@router.post(
    "/process",
    response_model=ProcessVideoResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a YouTube video",
    description="Extract transcript, create embeddings, and store in database",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def process_video(
    request: ProcessVideoRequest,
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager),
    generation_service: GenerationService = Depends(get_generation_service_dep)
):
    """
    Process a YouTube video: extract transcript, create chunks, generate embeddings.
    
    - **url**: YouTube video URL
    
    Returns video ID, status, and chunk count.
    """
    try:
        video_id = helpers.extract_video_id(request.url)
        
        # Check if already processed
        if mongodb_manager.video_exists(video_id):
            videos = mongodb_manager.list_videos(user_id=None, limit=1)
            video_info = next((v for v in videos if v.get("video_id") == video_id), None)
            if video_info:
                # Add user if not already added
                if user_id not in video_info.get("users", []):
                    mongodb_manager.videos_collection.update_one(
                        {"video_id": video_id},
                        {"$addToSet": {"users": user_id}}
                    )
                return ProcessVideoResponse(
                    video_id=video_id,
                    status="already_processed",
                    chunks_count=video_info["chunks_count"]
                )
        
        # Fetch transcript
        transcript_text = transcript_service.fetch_transcript(video_id)
        
        # Create chunks
        chunks = chunk_service.chunk_text(text=transcript_text, chunk_size=500, chunk_overlap=100)
        

        # Generate suggested questions
        logger.info(f"Generating suggested questions for video {video_id}")
        suggested_questions = []
        try:
            sample_chunks = [
                {"text": chunk, "chunk_id": f"chunk_{i+1}", "score": 1.0}
                for i, chunk in enumerate(chunks[:3])
            ]
            suggested_questions = generation_service.generate_suggested_questions(
                chunks=sample_chunks,
                video_title=f"Video {video_id}"
            )
            logger.info(f"Generated {len(suggested_questions)} questions")
        except Exception as e:
            logger.warning(f"Failed to generate questions: {e}. Continuing without questions.")

        # Generate full summary
        logger.info(f"Generating summary for video {video_id}")
        chunk_dicts = [
            {"text": chunk, "chunk_id": f"chunk_{i+1}", "score": 1.0}
            for i, chunk in enumerate(chunks)
        ]
        summary = generation_service.generate_summary(
            chunks=chunk_dicts,
            video_title=f"Video {video_id}"
        )
        logger.info(f"Summary generated for video {video_id}")

        # Store in database (pass summary)
        result = mongodb_manager.store_video(
            video_id=video_id,
            chunks=chunks,
            video_url=request.url,
            video_title=f"Video {video_id}",
            user_id=user_id,
            suggested_questions=suggested_questions,
            summary=summary
        )

        return ProcessVideoResponse(
            video_id=video_id,
            status="completed",
            chunks_count=result["chunks_count"]
        )
        
    except InvalidYouTubeURLError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except TranscriptError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Transcript error: {str(e)}")
    except ChunkingError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chunking error: {str(e)}")
    except Exception as e:
        logger.exception(f"Error processing video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing video"
        )


@router.get(
    "",
    response_model=ListVideosResponse,
    status_code=status.HTTP_200_OK,
    summary="List user's videos",
    description="Get all videos processed by the current user",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def list_videos(
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    """
    List all videos in the user's library.
    
    Returns list of videos with metadata.
    """
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
        logger.exception(f"Error listing videos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving videos"
        )


@router.post(
    "/save",
    status_code=status.HTTP_200_OK,
    summary="Save video to library",
    description="Add a video to user's library",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def save_video(
    video_id: str = Body(..., embed=True, description="YouTube video ID to save"),
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    """
    Save a video to user's library.
    
    - **video_id**: YouTube video ID
    
    Returns success status.
    """
    try:
        video_metadata = mongodb_manager.get_video_metadata(video_id)
        if not video_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found. Process it first using /process endpoint."
            )
        
        # Add user if not already present
        if user_id not in video_metadata.get("users", []):
            mongodb_manager.videos_collection.update_one(
                {"video_id": video_id},
                {"$addToSet": {"users": user_id}}
            )
        
        return {"status": "saved", "video_id": video_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error saving video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving video"
        )
@router.delete(
    "/{video_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a video and its chunks",
    description="Delete a video and all its chunks from the database for the current user.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)

async def delete_video(
    video_id: str = Path(..., description="YouTube video ID to delete"),
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    """
    Delete a video and all its chunks from the database for the current user.
    """
    try:
        # Check if video exists and user has access
        video_metadata = mongodb_manager.get_video_metadata(video_id)
        if not video_metadata or user_id not in video_metadata.get("users", []):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found for this user."
            )

        # Remove user from video users list
        mongodb_manager.videos_collection.update_one(
            {"video_id": video_id},
            {"$pull": {"users": user_id}}
        )

        # If no users remain, delete video and chunks
        updated_metadata = mongodb_manager.get_video_metadata(video_id)
        if not updated_metadata.get("users"):
            result = mongodb_manager.delete_video(video_id)
            return {"status": "deleted", **result}
        else:
            return {"status": "removed_from_user", "video_id": video_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting video"
        )