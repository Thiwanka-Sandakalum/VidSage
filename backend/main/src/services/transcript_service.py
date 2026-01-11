
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class TranscriptError(Exception):
    """Custom exception for transcript-related errors."""
    pass

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript

def fetch_transcript(video_id: str, lang: str = 'en') -> str:
    """
    Fetch transcript for a YouTube video using youtube-transcript-api.
    Args:
        video_id: YouTube video ID
        lang: Language code (default 'en')
    Returns:
        Transcript text
    Raises:
        TranscriptError: If transcript cannot be fetched
    """
    try:
        api = YouTubeTranscriptApi()
        try:
            transcript_list = api.list(video_id)
            transcript = transcript_list.find_transcript([lang])
        except NoTranscriptFound:
            # Fallback: try to fetch in any available language
            transcript = transcript_list.find_transcript(transcript_list._manually_created_transcripts.keys() or transcript_list._generated_transcripts.keys())
        except (TranscriptsDisabled, CouldNotRetrieveTranscript) as e:
            logger.error(f"Transcript not available: {str(e)}")
            raise TranscriptError(f"Transcript not available: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching transcript: {str(e)}")
            raise TranscriptError(f"Failed to fetch transcript for {video_id}: {str(e)}")

        # Fetch the transcript data (list of dicts with 'text')
        transcript_data = transcript.fetch()
        transcript_text = ' '.join([snippet.text for snippet in transcript_data])
        if not transcript_text.strip():
            raise TranscriptError("Transcript is empty after extraction")
        return transcript_text.strip()
    except Exception as e:
        logger.error(f"Error fetching transcript: {str(e)}")
        raise TranscriptError(f"Failed to fetch transcript for {video_id}: {str(e)}")

def fetch_available_transcripts(video_id: str) -> List[Dict]:
    """
    Get list of available transcripts for a video using youtube-transcript-api.
    Args:
        video_id: YouTube video ID
    Returns:
        List of available transcripts with language codes and names
    Raises:
        TranscriptError: If transcripts cannot be listed
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        available = []
        for transcript in transcript_list:
            available.append({
                "language_code": transcript.language_code,
                "language": transcript.language,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable
            })
        return available
    except Exception as e:
        logger.error(f"Error listing transcripts: {str(e)}")
        raise TranscriptError(f"Failed to list available transcripts: {str(e)}")
