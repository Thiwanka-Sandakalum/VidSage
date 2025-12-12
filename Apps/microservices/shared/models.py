"""Shared Pydantic models for API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessVideoRequest(BaseModel):
    """Request model for processing a YouTube video."""
    
    url: str = Field(
        ..., 
        description="YouTube video URL",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    )
    user_id: Optional[str] = Field(None, description="User identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "user_id": "user_123"
            }
        }


class ProcessVideoResponse(BaseModel):
    """Response model for video processing submission."""
    
    job_id: str = Field(..., description="Job identifier for tracking")
    video_id: str = Field(..., description="YouTube video ID")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "video_id": "dQw4w9WgXcQ",
                "status": "pending",
                "message": "Video submitted for processing"
            }
        }


class JobStatusResponse(BaseModel):
    """Response model for job status query."""
    
    job_id: str
    video_id: str
    status: JobStatus
    current_step: Optional[str] = None
    chunk_count: Optional[int] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "video_id": "dQw4w9WgXcQ",
                "status": "completed",
                "current_step": "completed",
                "chunk_count": 50,
                "error": None,
                "created_at": "2025-12-06T10:00:00Z",
                "updated_at": "2025-12-06T10:05:00Z"
            }
        }


class SourceChunk(BaseModel):
    """Source chunk reference in generated answer."""
    
    chunk_id: str = Field(..., description="Referenced chunk ID")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    text_preview: str = Field(..., description="Preview of chunk text")


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
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How to grow bigger muscles?",
                "video_id": "XLr2RKoD-oY",
                "top_k": 5
            }
        }


class GenerateResponse(BaseModel):
    """Response model for generated answers."""
    
    answer: str = Field(..., description="Generated answer to the query")
    sources: List[SourceChunk] = Field(..., description="Source chunks used for answer")
    model: str = Field(..., description="LLM model used for generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To grow bigger muscles, focus on progressive overload...",
                "sources": [
                    {
                        "chunk_id": "chunk_12",
                        "relevance_score": 0.92,
                        "text_preview": "Progressive overload is key to muscle growth..."
                    }
                ],
                "model": "gemini-2.0-flash-lite"
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
