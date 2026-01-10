"""Shared modules for VidSage microservices."""

from .events import (
    BaseEvent,
    VideoSubmittedEvent,
    TranscriptDownloadedEvent,
    EmbeddingCompletedEvent,
    ProcessingFailedEvent,
)
from .models import (
    JobStatus,
    ProcessVideoRequest,
    ProcessVideoResponse,
    GenerateRequest,
    GenerateResponse,
    SourceChunk,
)

__all__ = [
    # Events
    "BaseEvent",
    "VideoSubmittedEvent",
    "TranscriptDownloadedEvent",
    "EmbeddingCompletedEvent",
    "ProcessingFailedEvent",
    # Models
    "JobStatus",
    "ProcessVideoRequest",
    "ProcessVideoResponse",
    "GenerateRequest",
    "GenerateResponse",
    "SourceChunk",
]
