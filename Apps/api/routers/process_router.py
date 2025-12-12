from fastapi import APIRouter, HTTPException, status, Depends
from models import ProcessVideoRequest, ProcessVideoResponse, ErrorResponse
from utils.auth import get_current_user_id
from services import fetch_transcript, TranscriptError, chunk_text, ChunkingError
from utils import extract_video_id, InvalidYouTubeURLError
from services.mongodb_vector_store import MongoDBVectorStoreManager
from services.generation_service import get_generation_service
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager):
    global mongodb_manager
    mongodb_manager = manager

@router.post(
    "/process",
    response_model=ProcessVideoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def process_video(request: ProcessVideoRequest, user_id: str = Depends(get_current_user_id)):
    global mongodb_manager
    try:
        video_id = extract_video_id(request.url)
        if mongodb_manager.video_exists(video_id):
            videos = mongodb_manager.list_videos(user_id=None, limit=1)
            video_info = next((v for v in videos if v.get("video_id") == video_id), None)
            if video_info:
                return ProcessVideoResponse(
                    video_id=video_id,
                    status="already_processed",
                    chunks_count=video_info["chunks_count"]
                )
        transcript_text = fetch_transcript(video_id)
        chunks = chunk_text(text=transcript_text, chunk_size=500, chunk_overlap=100)
        
        # Generate suggested questions from first few chunks
        logger.info(f"🔄 Generating suggested questions for video {video_id}...")
        generation_service = get_generation_service()
        suggested_questions = []
        try:
            # Use first 3 chunks for question generation
            sample_chunks = [{"text": chunk, "chunk_id": f"chunk_{i+1}", "score": 1.0} 
                           for i, chunk in enumerate(chunks[:3])]
            suggested_questions = generation_service.generate_suggested_questions(
                chunks=sample_chunks,
                video_title=f"Video {video_id}"
            )
            logger.info(f"✅ Generated {len(suggested_questions)} questions")
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate questions: {e}. Continuing without questions.")
        
        result = mongodb_manager.store_video(
            video_id=video_id,
            chunks=chunks,
            video_url=request.url,
            video_title=f"Video {video_id}",
            user_id=user_id,
            suggested_questions=suggested_questions
        )
        response = ProcessVideoResponse(
            video_id=video_id,
            status="completed",
            chunks_count=result["chunks_count"]
        )
        return response
    except InvalidYouTubeURLError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except TranscriptError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Transcript error: {str(e)}")
    except ChunkingError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chunking error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
