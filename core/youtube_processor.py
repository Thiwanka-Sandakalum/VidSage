import re
import os
from typing import Tuple, Optional, Dict
from pytube import YouTube
from moviepy.editor import AudioFileClip

class YouTubeProcessor:
    """Process YouTube videos by downloading and extracting audio."""
    
    def __init__(self, storage_manager):
        """
        Initialize the YouTube Processor.
        
        Args:
            storage_manager: Instance of StorageManager for file operations
        """
        self.storage_manager = storage_manager
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None if not a valid YouTube URL
        """
        # Regular expression patterns for YouTube URLs
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Standard YouTube URL
            r"(?:embed\/)([0-9A-Za-z_-]{11})",  # Embedded YouTube URL
            r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})"  # Short YouTube URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def download_video(self, url: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Download a YouTube video and extract its metadata.
        
        Args:
            url: YouTube URL
            
        Returns:
            Tuple containing (success status, video_id, metadata)
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            print("Invalid YouTube URL")
            return False, None, None
        
        try:
            # Initialize YouTube object
            yt = YouTube(url)
            
            # Extract metadata
            metadata = {
                "title": yt.title,
                "author": yt.author,
                "length_seconds": yt.length,
                "views": yt.views,
                "publish_date": str(yt.publish_date) if yt.publish_date else None,
                "url": url,
                "video_id": video_id
            }
            
            # Save metadata
            self.storage_manager.save_metadata(video_id, metadata)
            
            # Download audio stream
            audio_stream = yt.streams.filter(only_audio=True).first()
            temp_output_path = audio_stream.download(output_path=os.path.dirname(self.storage_manager.get_audio_path(video_id)), 
                                               filename=f"{video_id}_temp")
            
            return True, video_id, metadata
        
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False, video_id if video_id else None, None
    
    def extract_audio(self, video_id: str) -> bool:
        """
        Extract audio from the downloaded video file and convert to mp3.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if successful, False otherwise
        """
        temp_file = os.path.join(os.path.dirname(self.storage_manager.get_audio_path(video_id)), f"{video_id}_temp")
        output_path = self.storage_manager.get_audio_path(video_id)
        
        if not os.path.exists(temp_file):
            print(f"Temporary file not found: {temp_file}")
            return False
        
        try:
            # Convert to mp3 using moviepy
            audio_clip = AudioFileClip(temp_file)
            audio_clip.write_audiofile(output_path, verbose=False, logger=None)
            audio_clip.close()
            
            # Remove temporary file
            os.remove(temp_file)
            
            return True
        except Exception as e:
            print(f"Error extracting audio: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False
    
    def process_video(self, url: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Process a YouTube video by downloading and extracting audio.
        
        Args:
            url: YouTube URL
            
        Returns:
            Tuple containing (success status, video_id, metadata)
        """
        success, video_id, metadata = self.download_video(url)
        if not success or not video_id:
            return False, None, None
        
        # Extract audio from the downloaded video
        audio_success = self.extract_audio(video_id)
        if not audio_success:
            return False, video_id, metadata
        
        return True, video_id, metadata