
import re
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
import yt_dlp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptError(Exception):
    """Custom exception for transcript-related errors."""
    pass


def fetch_transcript(video_id: str, languages: Optional[List[str]] = None) -> str:
    """
    Fetch the transcript for a YouTube video using yt-dlp.
    
    Args:
        video_id: YouTube video ID
        languages: Preferred languages for transcript (default: ['en'])
        
    Returns:
        Full transcript text as a single string
        
    Raises:
        TranscriptError: If transcript cannot be fetched
    """
    if languages is None:
        languages = ['en', 'en-US']
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # Create temporary directory for subtitle files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Configure yt-dlp to download subtitles
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': languages,
                'subtitlesformat': 'srt',
                'outtmpl': str(temp_path / video_id),
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['default']
                    }
                }
            }
            
            # Get video info and download subtitles
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                
                if not info_dict:
                    raise TranscriptError(f"Could not retrieve video info for: {video_id}")
                
                # Check for available subtitles
                subtitles = info_dict.get('subtitles', {})
                automatic_captions = info_dict.get('automatic_captions', {})
                
                has_manual = any(lang in subtitles for lang in languages)
                has_auto = any(lang in automatic_captions for lang in languages)
                
                if not (has_manual or has_auto):
                    available_langs = list(subtitles.keys()) + list(automatic_captions.keys())
                    raise TranscriptError(
                        f"No subtitles available in {languages}. Available: {available_langs}"
                    )
                
                logger.info(f"Downloading subtitles (manual: {has_manual}, auto: {has_auto})")
                
                # Download the subtitles
                ydl.download([url])
            
            # Find and read the subtitle file
            subtitle_files = list(temp_path.glob(f"{video_id}*.srt"))
            
            if not subtitle_files:
                raise TranscriptError(f"Subtitle file not found after download for: {video_id}")
            
            # Use the first available subtitle file
            subtitle_path = subtitle_files[0]
            logger.info(f"Reading subtitle file: {subtitle_path.name}")
            
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                subtitle_content = f.read()
            
            # Extract plain text from SRT format
            transcript_text = extract_subtitle_text(subtitle_content)
            
            if not transcript_text or transcript_text.strip() == "":
                raise TranscriptError("Transcript is empty after extraction")
            
            return transcript_text.strip()
            
    except TranscriptError:
        raise
    except Exception as e:
        logger.error(f"Error fetching transcript: {str(e)}")
        raise TranscriptError(f"Failed to fetch transcript for {video_id}: {str(e)}")


def extract_subtitle_text(subtitle_content: str) -> str:
    """
    Extract plain text from SRT subtitle format, removing timestamps and counters.
    
    Args:
        subtitle_content: The SRT subtitle content
        
    Returns:
        Clean text content
    """
    # Remove counters and timestamps
    lines = subtitle_content.split('\n')
    text_lines = []
    i = 0
    
    while i < len(lines):
        # Skip counter lines (just numbers)
        if lines[i].strip().isdigit():
            i += 1
            continue
        
        # Skip timestamp lines (contains -->)
        if '-->' in lines[i]:
            i += 1
            continue
        
        # Add text lines
        if lines[i].strip():
            text_lines.append(lines[i].strip())
        
        i += 1
    
    # Join text lines with space
    text = ' '.join(text_lines)
    
    # Clean up text: remove HTML tags and multiple spaces
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'\s+', ' ', text)     # Replace multiple spaces with single space
    
    return text.strip()


def fetch_available_transcripts(video_id: str) -> List[Dict[str, str]]:
    """
    Get list of available transcripts for a video.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of available transcripts with language codes and names
        
    Raises:
        TranscriptError: If transcripts cannot be listed
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['default']
                }
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            if not info_dict:
                raise TranscriptError(f"Could not retrieve video info for: {video_id}")
            
            subtitles = info_dict.get('subtitles', {})
            automatic_captions = info_dict.get('automatic_captions', {})
            
            available = []
            
            # Add manual subtitles
            for lang_code, subs in subtitles.items():
                if subs:
                    available.append({
                        "language_code": lang_code,
                        "language": lang_code,  # yt-dlp doesn't provide full language names
                        "is_generated": False,
                        "is_translatable": False
                    })
            
            # Add automatic captions
            for lang_code, caps in automatic_captions.items():
                # Avoid duplicates
                if not any(a['language_code'] == lang_code for a in available):
                    if caps:
                        available.append({
                            "language_code": lang_code,
                            "language": lang_code,
                            "is_generated": True,
                            "is_translatable": True
                        })
            
            return available
            
    except Exception as e:
        logger.error(f"Error listing transcripts: {str(e)}")
        raise TranscriptError(f"Failed to list available transcripts: {str(e)}")
