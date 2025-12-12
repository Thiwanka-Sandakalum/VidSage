
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProcessVideoRequest(BaseModel):
    url: str


class ChunkInfo(BaseModel):
    id: str
    text: str
    embedding: List[float]
    embedding_sample: Optional[List[float]] = None


class ProcessVideoResponse(BaseModel):
    video_id: str
    status: str
    chunks_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class EmbedQueryRequest(BaseModel):
    query: str


class EmbedQueryResponse(BaseModel):
    query: str
    embedding: List[float]
    dimensions: int
    model: str


class SearchRequest(BaseModel):
    video_id: str
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = {}


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



