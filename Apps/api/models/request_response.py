
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProcessVideoRequest(BaseModel):
    """Request model for processing a YouTube video."""
    
    url: str = Field(
        ..., 
        description="YouTube video URL",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }


class ChunkInfo(BaseModel):
    """Information about a single text chunk."""
    
    id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    embedding: List[float] = Field(
        ..., 
        description="Full embedding vector (768 dimensions)"
    )
    embedding_sample: Optional[List[float]] = Field(
        default=None,
        description="Preview: First 5 dimensions of embedding (for debugging)"
    )


class ProcessVideoResponse(BaseModel):
    """Response model for video processing results."""
    
    video_id: str = Field(..., description="YouTube video ID")
    status: str = Field(..., description="Processing status")
    chunks_count: int = Field(..., description="Total number of chunks created")

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "status": "completed",
                "chunks_count": 115
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid YouTube URL",
                "detail": "The provided URL is not a valid YouTube video URL"
            }
        }


class EmbedQueryRequest(BaseModel):
    """Request model for embedding a search query."""
    
    query: str = Field(
        ...,
        description="Text query to embed",
        min_length=1,
        max_length=2048,
        examples=["What is machine learning?"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?"
            }
        }


class EmbedQueryResponse(BaseModel):
    """Response model for query embedding."""
    
    query: str = Field(..., description="Original query text")
    embedding: List[float] = Field(..., description="Full embedding vector")
    dimensions: int = Field(..., description="Embedding dimensions")
    model: str = Field(..., description="Model used for embedding")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "embedding": [0.123, -0.456, 0.789],  # Truncated for example
                "dimensions": 768,
                "model": "models/text-embedding-004"
            }
        }


class SearchRequest(BaseModel):
    """Request model for searching a video."""
    
    video_id: str = Field(
        ...,
        description="YouTube video ID to search in",
        min_length=11,
        max_length=11,
        examples=["ggyxn9dphLU"]
    )
    query: str = Field(
        ...,
        description="Search query text",
        min_length=1,
        max_length=2048,
        examples=["money advice"]
    )
    top_k: int = Field(
        default=5,
        description="Number of results to return",
        ge=1,
        le=20
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "ggyxn9dphLU",
                "query": "money advice",
                "top_k": 5
            }
        }


class SearchResult(BaseModel):
    """Single search result."""
    
    chunk_id: str = Field(..., description="Chunk identifier")
    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Similarity score (higher = more similar)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """Response model for video search."""
    
    results: List[SearchResult] = Field(..., description="Search results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "chunk_id": "chunk_3",
                        "text": "Sample chunk text about money...",
                        "score": 0.89,
                        "metadata": {"chunk_index": 3}
                    }
                ]
            }
        }


class VideoMetadata(BaseModel):
    """Video metadata model."""
    
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    chunks_count: int = Field(..., description="Number of chunks")
    status: str = Field(..., description="Processing status")


class ListVideosResponse(BaseModel):
    """Response model for listing videos."""
    
    videos: List[VideoMetadata] = Field(..., description="List of videos")


# ============================================
# RAG Generation Models
# ============================================

class GenerateRequest(BaseModel):
    """Request model for RAG-based answer generation."""
    
    query: str = Field(
        ...,
        description="User question to answer",
        min_length=1,
        max_length=2048,
        examples=["How to grow bigger muscles?"]
    )
    video_id: str = Field(
        ...,
        description="YouTube video ID to search in",
        min_length=11,
        max_length=11,
        examples=["XLr2RKoD-oY"]
    )
    top_k: int = Field(
        default=5,
        description="Number of context chunks to retrieve",
        ge=1,
        le=10
    )
    stream: bool = Field(
        default=False,
        description="Enable streaming responses"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How to grow bigger muscles?",
                "video_id": "XLr2RKoD-oY",
                "top_k": 5,
                "stream": False
            }
        }


class SourceChunk(BaseModel):
    """Source chunk reference in generated answer."""
    
    chunk_id: str = Field(..., description="Referenced chunk ID")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    text_preview: str = Field(..., description="Preview of chunk text (first 100 chars)")


class GenerateResponse(BaseModel):
    """Response model for generated answers."""
    
    answer: str = Field(..., description="Generated answer to the query")
    sources: List[SourceChunk] = Field(..., description="Source chunks used for answer")
    model: str = Field(..., description="LLM model used for generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To grow bigger muscles, focus on progressive overload, proper nutrition with adequate protein intake, and sufficient rest between workouts...",
                "sources": [
                    {
                        "chunk_id": "chunk_12",
                        "relevance_score": 0.92,
                        "text_preview": "Progressive overload is key to muscle growth. You need to gradually increase..."
                    }
                ],
                "model": "gemini-1.5-flash"
            }
        }



