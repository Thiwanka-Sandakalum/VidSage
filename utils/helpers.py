#!/usr/bin/env python3
"""
Helper Utilities Module

This module provides utility functions for VidSage application.
"""

import os
import re
import sys
import time
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from URL
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID string
    """
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    raise ValueError(f"Could not extract video ID from URL: {url}")

def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_filesize(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_youtube_url(url: str) -> bool:
    """
    Check if a URL is a valid YouTube URL
    
    Args:
        url: URL to check
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    if not validate_url(url):
        return False
    
    # Check if domain is youtube.com or youtu.be
    domain = urllib.parse.urlparse(url).netloc.lower()
    return domain in ['youtube.com', 'www.youtube.com', 'youtu.be']

def ensure_dir(directory: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        directory: Directory path
        
    Returns:
        Path to the directory
    """
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def load_api_key(key_name: str = 'GOOGLE_API_KEY') -> Optional[str]:
    """
    Load API key from environment variable
    
    Args:
        key_name: Name of the environment variable
        
    Returns:
        API key if found, None otherwise
    """
    api_key = os.environ.get(key_name)
    
    if not api_key:
        logger.warning(f"{key_name} environment variable not found")
        return None
    
    return api_key

def format_transcript_for_display(transcript: str, max_line_length: int = 80) -> str:
    """
    Format transcript text for nice display
    
    Args:
        transcript: Transcript text
        max_line_length: Maximum line length
        
    Returns:
        Formatted transcript text
    """
    # Split transcript into paragraphs
    paragraphs = transcript.split('\n\n')
    
    formatted_text = ""
    for paragraph in paragraphs:
        # Wrap long lines
        lines = []
        current_line = ""
        
        # Split paragraph into words
        words = paragraph.split()
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_line_length:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word
        
        # Add the last line
        if current_line:
            lines.append(current_line)
        
        # Join lines with newline
        formatted_paragraph = '\n'.join(lines)
        
        # Add to formatted text
        formatted_text += formatted_paragraph + "\n\n"
    
    return formatted_text.strip()

def countdown(seconds: int) -> None:
    """
    Display a countdown timer
    
    Args:
        seconds: Number of seconds to count down
    """
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\rWaiting for {i} seconds...")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rDone!                \n")
