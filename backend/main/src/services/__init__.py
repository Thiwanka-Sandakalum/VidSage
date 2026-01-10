"""Services package initialization."""

from .transcript_service import (
    fetch_transcript,
    fetch_available_transcripts,
    TranscriptError
)
from .chunk_service import (
    chunk_text,
    get_chunk_metadata,
    ChunkingError
)


__all__ = [
    # Transcript service
    "fetch_transcript",
    "fetch_available_transcripts",
    "TranscriptError",
    # Chunking service
    "chunk_text",
    "get_chunk_metadata",
    "ChunkingError",
    # Embedding service
]
