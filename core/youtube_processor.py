#!/usr/bin/env python3
"""
YouTube Processor Module

This module handles downloading YouTube videos and extracting audio content.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, BinaryIO, Union
import logging
from io import BytesIO

# YouTube downloading libraries
import yt_dlp
from pytube import YouTube

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeProcessor:
    """Handles downloading and processing YouTube videos"""
    
    def __init__(self):
        """Initialize the YouTube processor"""
        logger.info("YouTube Processor initialized")
        
    @staticmethod
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
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get metadata about a YouTube video
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video metadata
        """
        try:
            # Use YouTube API to get basic info
            yt = YouTube(url)
            
            # Gather video information
            info = {
                "id": yt.video_id,
                "title": yt.title,
                "description": yt.description,
                "length": yt.length,
                "author": yt.author,
                "publish_date": str(yt.publish_date) if yt.publish_date else None,
                "views": yt.views,
                "thumbnail_url": yt.thumbnail_url
            }
            
            logger.info(f"Video info retrieved for: {yt.title}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise
    
    def download_audio(self, url: str, output_path: Optional[Path] = None) -> Tuple[BinaryIO, str]:
        """
        Download audio from a YouTube video
        
        Args:
            url: YouTube video URL
            output_path: Optional path to save the audio file
            
        Returns:
            Tuple of (audio data as file-like object, video_id)
        """
        try:
            video_id = self.extract_video_id(url)
            
            # Create a BytesIO object to store the audio
            audio_data = BytesIO()
            
            # Use yt-dlp to download audio (more reliable than pytube)
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': '-',  # Output to stdout
                'quiet': True,
                'logtostderr': True,
            }
            
            if output_path:
                # If output path is specified, download to file
                file_path = output_path / f"{video_id}.mp3"
                ydl_opts['outtmpl'] = str(file_path)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Open the file and read into BytesIO
                with open(file_path, 'rb') as f:
                    audio_data.write(f.read())
                
                audio_data.seek(0)
                logger.info(f"Audio downloaded to file: {file_path}")
                
            else:
                # Download directly to memory
                # Note: This is more complex with yt-dlp; simplified version shown
                temp_file = f"/tmp/{video_id}.mp3"
                ydl_opts['outtmpl'] = temp_file
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Read file into BytesIO then delete
                with open(temp_file, 'rb') as f:
                    audio_data.write(f.read())
                    
                os.remove(temp_file)
                audio_data.seek(0)
                logger.info(f"Audio downloaded to memory for video ID: {video_id}")
            
            return audio_data, video_id
            
        except Exception as e:
            logger.error(f"Error downloading audio: {str(e)}")
            raise
