
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs


class InvalidYouTubeURLError(Exception):
    """Custom exception for invalid YouTube URLs."""
    pass


def extract_video_id(url: str) -> str:
    """
    Extract video ID from a YouTube URL.
    
    Supports various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID string
        
    Raises:
        InvalidYouTubeURLError: If URL is invalid or video ID cannot be extracted
    """
    if not url or not isinstance(url, str):
        raise InvalidYouTubeURLError("URL must be a non-empty string")
    
    # Pattern 1: youtube.com/watch?v=VIDEO_ID
    pattern1 = r'(?:youtube\.com\/watch\?v=)([\w-]+)'
    
    # Pattern 2: youtu.be/VIDEO_ID
    pattern2 = r'(?:youtu\.be\/)([\w-]+)'
    
    # Pattern 3: youtube.com/embed/VIDEO_ID
    pattern3 = r'(?:youtube\.com\/embed\/)([\w-]+)'
    
    # Pattern 4: youtube.com/v/VIDEO_ID
    pattern4 = r'(?:youtube\.com\/v\/)([\w-]+)'
    
    patterns = [pattern1, pattern2, pattern3, pattern4]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Try parsing as URL with query parameters
    try:
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                video_id = query_params['v'][0]
                if video_id and re.match(r'^[\w-]+$', video_id):
                    return video_id
    except Exception:
        pass
    
    raise InvalidYouTubeURLError(
        f"Could not extract video ID from URL: {url}. "
        "Please provide a valid YouTube URL."
    )


def validate_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format.
    
    YouTube video IDs are typically 11 characters long and contain
    alphanumeric characters, hyphens, and underscores.
    
    Args:
        video_id: Video ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not video_id or not isinstance(video_id, str):
        return False
    
    # YouTube video IDs are typically 11 characters
    # but we'll be flexible with length
    if len(video_id) < 5 or len(video_id) > 20:
        return False
    
    # Must contain only alphanumeric, hyphen, and underscore
    return bool(re.match(r'^[\w-]+$', video_id))


def format_error_message(error: Exception, context: str = "") -> dict:
    """
    Format an exception into a standardized error response.
    
    Args:
        error: Exception to format
        context: Additional context about where the error occurred
        
    Returns:
        Dictionary with error and detail fields
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    if context:
        detail = f"{context}: {error_message}"
    else:
        detail = error_message
    
    return {
        "error": error_type,
        "detail": detail
    }
