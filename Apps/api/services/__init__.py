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
from .embed_service import (
    VectorStoreManager,
    create_embeddings,
    EmbeddingError
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
    "VectorStoreManager",
    "create_embeddings",
    "EmbeddingError"
]
