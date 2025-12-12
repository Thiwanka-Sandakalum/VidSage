"""Shared utility functions for microservices."""

import re
from typing import Optional


class InvalidYouTubeURLError(Exception):
    """Exception raised for invalid YouTube URLs."""
    pass


def extract_video_id(url: str) -> str:
    """
    Extract video ID from various YouTube URL formats.
    
    Args:
        url: YouTube URL (various formats supported)
        
    Returns:
        Video ID (11 characters)
        
    Raises:
        InvalidYouTubeURLError: If URL is invalid or video ID cannot be extracted
    """
    # Pattern 1: Standard watch URL
    # https://www.youtube.com/watch?v=VIDEO_ID
    # https://youtube.com/watch?v=VIDEO_ID
    match = re.search(r'(?:youtube\.com/watch\?v=)([\w-]{11})', url)
    if match:
        return match.group(1)
    
    # Pattern 2: Short URL
    # https://youtu.be/VIDEO_ID
    match = re.search(r'(?:youtu\.be/)([\w-]{11})', url)
    if match:
        return match.group(1)
    
    # Pattern 3: Embed URL
    # https://www.youtube.com/embed/VIDEO_ID
    match = re.search(r'(?:youtube\.com/embed/)([\w-]{11})', url)
    if match:
        return match.group(1)
    
    # Pattern 4: Mobile URL
    # https://m.youtube.com/watch?v=VIDEO_ID
    match = re.search(r'(?:m\.youtube\.com/watch\?v=)([\w-]{11})', url)
    if match:
        return match.group(1)
    
    # If no pattern matched, raise error
    raise InvalidYouTubeURLError(
        f"Invalid YouTube URL: {url}. "
        "Supported formats: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID"
    )


def format_error_message(error: Exception, context: str = "") -> dict:
    """
    Format exception into a standardized error response.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        Dict with error and detail fields
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    return {
        "error": f"{context}: {error_type}" if context else error_type,
        "detail": error_msg
    }
