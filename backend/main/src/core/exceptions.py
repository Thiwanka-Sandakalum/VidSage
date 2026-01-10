"""Custom exceptions for the application."""

from typing import Any, Dict, Optional


class VidSageException(Exception):
    """Base exception for VidSage application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class VideoNotFoundError(VidSageException):
    """Video not found in database."""
    
    def __init__(self, message: str = "Video not found", video_id: str = None):
        details = {"video_id": video_id} if video_id else {}
        super().__init__(message, status_code=404, details=details)


class VideoAlreadyProcessedError(VidSageException):
    """Video has already been processed."""
    
    def __init__(self, message: str = "Video already processed", video_id: str = None):
        details = {"video_id": video_id} if video_id else {}
        super().__init__(message, status_code=409, details=details)


class TranscriptError(VidSageException):
    """Error fetching video transcript."""
    
    def __init__(self, message: str = "Could not fetch transcript", video_id: str = None):
        details = {"video_id": video_id} if video_id else {}
        super().__init__(message, status_code=400, details=details)


class ChunkingError(VidSageException):
    """Error chunking text."""
    
    def __init__(self, message: str = "Error chunking text"):
        super().__init__(message, status_code=500)


class EmbeddingError(VidSageException):
    """Error generating embeddings."""
    
    def __init__(self, message: str = "Error generating embeddings"):
        super().__init__(message, status_code=500)


class AuthenticationError(VidSageException):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(VidSageException):
    """User not authorized."""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)


class RateLimitError(VidSageException):
    """Rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class InvalidYouTubeURLError(VidSageException):
    """Invalid YouTube URL."""
    
    def __init__(self, message: str = "Invalid YouTube URL"):
        super().__init__(message, status_code=400)
