"""Answer generation endpoint using RAG."""

from fastapi import APIRouter, HTTPException, status, Depends
import logging

from src.core.security import get_current_user_id
from src.core.config import get_settings
from src.api.dependencies import get_mongodb_manager, get_generation_service_dep, get_cache_service_dep
from src.schemas import GenerateRequest, GenerateResponse, ErrorResponse, SourceChunk
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager
from src.services.generation_service import GenerationService
from src.services.cache_service import CacheService

router = APIRouter(prefix="/generate", tags=["generate"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI answer",
    description="Generate an AI-powered answer using RAG (Retrieval-Augmented Generation)",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def generate_answer(
    request: GenerateRequest,
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager),
    generation_service: GenerationService = Depends(get_generation_service_dep),
    cache_service: CacheService = Depends(get_cache_service_dep)
):
    """
    Generate an AI-powered answer to a question about video content.
    
    - **query**: Question to answer
    - **video_id**: YouTube video ID
    - **top_k**: Number of context chunks to use (1-10)
    - **stream**: Enable streaming response (future feature)
    
    Returns generated answer with source references.
    """
    try:
        settings = get_settings()
        
        # Check cache first
        cached_response = cache_service.get(request.video_id, request.query)
        if cached_response:
            logger.info(f"Cache hit for query: {request.query[:50]}...")
            return cached_response
        
        # Check if video exists
        if not mongodb_manager.video_exists(request.video_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {request.video_id} not found. Process it first using /process endpoint."
            )
        
        # Check if user has access
        if not mongodb_manager.user_has_video(user_id, request.video_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this video."
            )
        
        # Search for relevant chunks
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
        
        # Get video metadata
        video_metadata = mongodb_manager.get_video_metadata(request.video_id)
        video_title = video_metadata.get("title", "Unknown Video")
        
        # Generate answer
        answer = generation_service.generate_answer(
            query=request.query,
            chunks=search_results,
            video_title=video_title
        )
        
        # Prepare sources
        sources = generation_service.prepare_sources(search_results[:request.top_k])
        source_chunks = [
            SourceChunk(
                chunk_id=src["chunk_id"],
                relevance_score=src["relevance_score"],
                text_preview=src["text_preview"]
            )
            for src in sources
        ]
        
        response = GenerateResponse(
            answer=answer,
            sources=source_chunks,
            model=settings.LLM_MODEL
        )
        
        # Cache the response
        cache_service.set(request.video_id, request.query, response, ttl_minutes=30)
        logger.info(f"Cached response for query: {request.query[:50]}...")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating answer"
        )
