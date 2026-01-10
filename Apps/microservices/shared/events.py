"""Event schemas for microservices communication."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class BaseEvent(BaseModel):
    """Base event model for all events."""
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str  # Track entire workflow (job_id)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_123",
                "event_type": "base.event",
                "timestamp": "2025-12-06T10:00:00Z",
                "correlation_id": "job_abc"
            }
        }


class VideoSubmittedEvent(BaseEvent):
    """Event published when a video is submitted for processing."""
    
    event_type: str = "video.submitted"
    video_url: str
    user_id: Optional[str] = None
    job_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "video.submitted",
                "video_url": "https://www.youtube.com/watch?v=abc123",
                "user_id": "user_123",
                "job_id": "job_456",
                "correlation_id": "job_456"
            }
        }


class TranscriptDownloadedEvent(BaseEvent):
    """Event published when transcript download is complete."""
    
    event_type: str = "transcript.downloaded"
    job_id: str
    video_id: str
    transcript: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "transcript.downloaded",
                "job_id": "job_456",
                "video_id": "abc123",
                "transcript": "This is the full transcript...",
                "metadata": {
                    "title": "How to Build Muscle",
                    "duration": 600
                },
                "correlation_id": "job_456"
            }
        }


class EmbeddingCompletedEvent(BaseEvent):
    """Event published when embedding generation is complete."""
    
    event_type: str = "embedding.completed"
    job_id: str
    video_id: str
    chunk_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "embedding.completed",
                "job_id": "job_456",
                "video_id": "abc123",
                "chunk_count": 50,
                "correlation_id": "job_456"
            }
        }


class ProcessingFailedEvent(BaseEvent):
    """Event published when any processing step fails."""
    
    event_type: str = "processing.failed"
    job_id: str
    service: str
    error: str
    step: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "processing.failed",
                "job_id": "job_456",
                "service": "transcript-service",
                "error": "Video not found",
                "step": "transcript_download",
                "correlation_id": "job_456"
            }
        }
