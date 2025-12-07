from fastapi import APIRouter, HTTPException, status
from models import GenerateRequest, GenerateResponse, ErrorResponse, SourceChunk
from services.mongodb_vector_store import MongoDBVectorStoreManager
from services.generation_service import get_generation_service
from typing import Optional
import config

router = APIRouter()
mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager):
    global mongodb_manager
    mongodb_manager = manager

@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def generate_answer(request: GenerateRequest):
    global mongodb_manager
    try:
        if not mongodb_manager.video_exists(request.video_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {request.video_id} not found. Process it first using /process endpoint."
            )
        search_results = mongodb_manager.search_video(
            video_id=request.video_id,
            query=request.query,
            top_k=request.top_k
        )
        if not search_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No relevant content found for query: '{request.query}'"
            )
        video_metadata = mongodb_manager.get_video_metadata(request.video_id)
        video_title = video_metadata.get("title", "Unknown Video")
        generation_service = get_generation_service()
        answer = generation_service.generate_answer(
            query=request.query,
            chunks=search_results,
            video_title=video_title
        )
        sources = generation_service.prepare_sources(search_results)
        source_chunks = [
            SourceChunk(
                chunk_id=src["chunk_id"],
                relevance_score=src["relevance_score"],
                text_preview=src["text_preview"]
            )
            for src in sources
        ]
        return GenerateResponse(
            answer=answer,
            sources=source_chunks,
            model=config.LLM_MODEL
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation error: {str(e)}"
        )
