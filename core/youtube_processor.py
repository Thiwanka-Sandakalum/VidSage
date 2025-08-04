#!/usr/bin/env python3
"""
YouTube Processor Module

This module handles downloading YouTube videos, extracting audio content,
subtitles, and provides comprehensive metadata handling.
"""

import os
import re
import json
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, BinaryIO, Union
import logging
from io import BytesIO

# YouTube downloading libraries
import yt_dlp
from pytube import YouTube

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeProcessor:
    """Handles downloading and processing YouTube videos with additional capabilities"""
    
    def __init__(self, 
                data_dir: Optional[str] = None, 
                default_lang: str = 'en',
                audio_quality: str = '192'):
        """
        Initialize the YouTube processor
        
        Args:
            data_dir: Directory to store downloaded files (default: current directory)
            default_lang: Default language for subtitles (default: 'en')
            audio_quality: Audio quality in kbps (default: '192')
        """
        # Always use 'data' directory at project root
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / 'data'
        self.default_lang = default_lang
        self.audio_quality = audio_quality
        
        # Create data directories if they don't exist
        self._initialize_directories()
        
        logger.info("YouTube Processor initialized with data directory: %s", self.data_dir)
    
    def _initialize_directories(self):
        """Create necessary directories for storing data"""
        # Create main data directory
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        # Create subdirectories
        subdirs = ['audio', 'video', 'subtitles', 'thumbnails', 'info']
        for subdir in subdirs:
            Path(self.data_dir / subdir).mkdir(parents=True, exist_ok=True)
        logger.debug("Directory structure initialized")
    
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
            # Standard watch URLs
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            # Short URLs
            r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
            # Live URLs
            r'youtube\.com\/live\/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_video_info(self, url: str, save_info: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive metadata about a YouTube video
        
        Args:
            url: YouTube video URL
            save_info: Whether to save info as JSON file (default: False)
            
        Returns:
            Dictionary with video metadata
        """
        try:
            # Use yt-dlp to get info (more reliable than pytube)
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'format': 'best',
                'socket_timeout': 15,  # Timeout in seconds
                'verbose': False,  # Set to True for debugging if needed
                'extract_flat': False,  # Get full info, not just the playlist
                'ignoreerrors': True,  # Continue on error
            }
            
            # Get video info using yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_data = ydl.extract_info(url, download=False)
                
                if not video_data:
                    raise ValueError(f"Failed to retrieve video data from URL: {url}")
            
            # Get the video ID
            video_id = video_data.get('id', self.extract_video_id(url))
            
            # Gather video information
            info = {
                "id": video_id,
                "title": video_data.get('title', 'Unknown Title'),
                "description": video_data.get('description', ''),
                "length": video_data.get('duration', 0),
                "author": video_data.get('uploader', 'Unknown Author'),
                "channel_id": video_data.get('channel_id', ''),
                "channel_url": video_data.get('channel_url', ''),
                "publish_date": str(video_data.get('upload_date', '')),
                "views": video_data.get('view_count', 0),
                "like_count": video_data.get('like_count', 0),
                "comment_count": video_data.get('comment_count', 0),
                "thumbnail_url": video_data.get('thumbnail', ''),
                "categories": video_data.get('categories', []),
                "tags": video_data.get('tags', []),
                "availability": video_data.get('availability', 'Unknown'),
                "is_live": video_data.get('is_live', False),
                "was_live": video_data.get('was_live', False),
                "language": video_data.get('language', 'Unknown'),
                "formats": self._summarize_formats(video_data.get('formats', [])),
                "subtitles": self._check_subtitles_availability(video_data),
            }
            
            # Save info as JSON if requested
            if save_info:
                self._save_info_json(info)
            
            logger.info(f"Video info retrieved for: {info['title']} (ID: {video_id})")
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise
    
    def _summarize_formats(self, formats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize available format information"""
        if not formats:
            return []
            
        summary = []
        for fmt in formats:
            if not isinstance(fmt, dict):
                continue
                
            summary.append({
                "format_id": fmt.get('format_id', ''),
                "ext": fmt.get('ext', ''),
                "resolution": fmt.get('resolution', ''),
                "fps": fmt.get('fps', None),
                "filesize": fmt.get('filesize', None),
                "tbr": fmt.get('tbr', None),  # Total bitrate
                "acodec": fmt.get('acodec', ''),
                "vcodec": fmt.get('vcodec', '')
            })
        return summary
        
    def _check_subtitles_availability(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check and summarize available subtitles"""
        subtitles = video_data.get('subtitles', {})
        automatic_captions = video_data.get('automatic_captions', {})
        
        result = {
            "manual": {},
            "automatic": {},
            "languages": {
                "manual": list(subtitles.keys()),
                "automatic": list(automatic_captions.keys())
            }
        }
        
        # Add detailed info for manual subtitles
        for lang, subs in subtitles.items():
            if subs:
                result["manual"][lang] = [
                    {"ext": s.get('ext', ''), "url": s.get('url', '')} 
                    for s in subs if isinstance(s, dict)
                ]
                
        # Add detailed info for automatic subtitles
        for lang, subs in automatic_captions.items():
            if subs:
                result["automatic"][lang] = [
                    {"ext": s.get('ext', ''), "url": s.get('url', '')} 
                    for s in subs if isinstance(s, dict)
                ]
        
        return result
        
    def _save_info_json(self, info: Dict[str, Any]) -> str:
        """Save video information as JSON file"""
        video_id = info["id"]
        # Create subdirectory for video under info directory
        video_info_dir = self.data_dir / "/info" / video_id
        video_info_dir.mkdir(parents=True, exist_ok=True)

        file_path = video_info_dir / f"{video_id}_info.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=4)
            
        logger.info(f"Video info saved to: {file_path}")
        return str(file_path)
    
    def download_audio(self, url: str, output_path: Optional[Union[str, Path]] = None, 
                   audio_format: str = 'mp3', audio_quality: Optional[str] = None) -> Tuple[Union[BinaryIO, str], str]:
        """
        Download audio from a YouTube video with improved reliability
        
        Args:
            url: YouTube video URL
            output_path: Optional path to save the audio file
            audio_format: Format of audio file (default: mp3)
            audio_quality: Quality of audio (default: uses instance setting)
            
        Returns:
            Tuple of (audio data as file-like object or file path, video_id)
        """
        try:
            video_id = self.extract_video_id(url)
            audio_quality = audio_quality or self.audio_quality
            
            # Create output directory if needed
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_path = self.data_dir / "audio" / f"{video_id}.{audio_format}"
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use temp directory for initial download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = Path(temp_dir) / f"{video_id}.{audio_format}"
                
                # Configure yt-dlp options
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': audio_quality,
                    }],
                    'outtmpl': str(temp_file).replace(f".{audio_format}", ""),  # yt-dlp will add extension
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': False,
                    'socket_timeout': 30,
                    'retries': 10,  # Retry on network errors
                    'fragment_retries': 10,
                }
                
                # Progress callback for logging
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        percent = d.get('_percent_str', 'N/A')
                        logger.debug(f"Downloading audio: {percent}")
                    elif d['status'] == 'finished':
                        logger.info(f"Download finished, now post-processing...")
                
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Download using yt-dlp
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    download_result = ydl.download([url])
                    
                    if download_result:
                        logger.warning(f"yt-dlp reported issues with download (result: {download_result})")
                
                # Find the downloaded file
                matching_files = list(Path(temp_dir).glob(f"*.{audio_format}"))
                if not matching_files:
                    raise FileNotFoundError(f"Could not find downloaded {audio_format} file in {temp_dir}")
                
                downloaded_file = matching_files[0]
                
                # Copy to destination if needed
                if isinstance(output_path, Path):
                    shutil.copy2(downloaded_file, output_path)
                    logger.info(f"Audio saved to: {output_path}")
                
                # Return as BytesIO or path
                if isinstance(output_path, Path):
                    return str(output_path), video_id
                else:
                    # Return as BytesIO
                    audio_data = BytesIO()
                    with open(downloaded_file, 'rb') as f:
                        audio_data.write(f.read())
                    audio_data.seek(0)
                    logger.info(f"Audio loaded into memory for video ID: {video_id}")
                    return audio_data, video_id
            
        except Exception as e:
            logger.error(f"Error downloading audio: {str(e)}")
            # Retry once with different options on failure
            if "ERROR:" in str(e):
                logger.info("Retrying download with different options...")
                try:
                    return self._retry_audio_download(url, output_path, audio_format, audio_quality)
                except Exception as retry_err:
                    logger.error(f"Retry also failed: {str(retry_err)}")
            raise
    
    def _retry_audio_download(self, url: str, output_path: Optional[Union[str, Path]], 
                             audio_format: str, audio_quality: str) -> Tuple[Union[BinaryIO, str], str]:
        """Fallback method for audio download with different options"""
        video_id = self.extract_video_id(url)
        
        # Prepare output path
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = self.data_dir / "audio" / f"{video_id}.{audio_format}"
        
        # Use simpler options with pytube as fallback
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                raise ValueError("No audio stream found")
                
            temp_file = audio_stream.download(output_path=tempfile.gettempdir(), 
                                             filename=f"{video_id}_temp")
            
            # Convert to desired format using ffmpeg through yt-dlp
            ydl_opts = {
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': audio_quality,
                }],
                'outtmpl': str(output_path).replace(f".{audio_format}", ""),
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.process_video_result({'filepath': temp_file})
            
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
                
            if isinstance(output_path, Path):
                return str(output_path), video_id
            else:
                # Return as BytesIO
                audio_data = BytesIO()
                with open(output_path, 'rb') as f:
                    audio_data.write(f.read())
                audio_data.seek(0)
                return audio_data, video_id
                
        except Exception as e:
            logger.error(f"Retry download failed: {str(e)}")
            raise
    
    def download_subtitles(self, url: str, output_dir: Optional[Union[str, Path]] = None, 
                       langs: List[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Download subtitles from a YouTube video
        
        Args:
            url: YouTube video URL
            output_dir: Directory to save subtitles (default: subtitles directory)
            langs: List of language codes to download (default: ['en', 'en-US'])
            
        Returns:
            Tuple of (success, video_id, subtitle_path or None)
        """
        try:
            # Get video ID
            video_id = self.extract_video_id(url)
            
            # Setup output directory
            if output_dir is None:
                output_dir = self.data_dir / "subtitles"
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Default language list
            if langs is None:
                langs = ['en', 'en-US']
                
            # Set up options to extract available subtitles
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': langs,
                'quiet': True,
                'no_warnings': True,
            }
            
            # First, extract video info and available subtitles
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_id = info_dict.get('id', video_id)
                title = info_dict.get('title', 'Unknown Title')
                
                logger.info(f"Checking subtitles for: {title}")
                
                # Check for available subtitles
                subtitles = info_dict.get('subtitles', {})
                automatic_captions = info_dict.get('automatic_captions', {})
                
                # Check for subtitles in requested languages
                has_manual_subtitles = False
                has_auto_subtitles = False
                
                for lang in langs:
                    if lang in subtitles and subtitles[lang]:
                        has_manual_subtitles = True
                    if lang in automatic_captions and automatic_captions[lang]:
                        has_auto_subtitles = True
                
                logger.info(f"Manual subtitles available: {has_manual_subtitles}")
                logger.info(f"Automatic captions available: {has_auto_subtitles}")
                
                if not (has_manual_subtitles or has_auto_subtitles):
                    logger.warning(f"No subtitles available in languages: {langs}")
                    return False, video_id, None
            
            # Download subtitles if available
            subtitle_opts = {
                'skip_download': True,
                'writesubtitles': has_manual_subtitles,
                'writeautomaticsub': has_auto_subtitles and not has_manual_subtitles,
                'subtitleslangs': langs,
                'subtitlesformat': 'srt',  # SRT format is more readable
                'outtmpl': str(output_dir / video_id),
                'quiet': True,
                'no_warnings': True,
            }
            
            try:
                with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                    ydl.download([url])
            except Exception as download_error:
                logger.error(f"yt-dlp download error: {str(download_error)}")
                # Try with different options
                logger.info("Retrying with fallback options...")
                try:
                    fallback_opts = {
                        'skip_download': True,
                        'writeautomaticsub': True,
                        'subtitleslangs': langs,
                        'outtmpl': str(output_dir / video_id),
                        'quiet': False,  # Enable output for debugging
                    }
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                        ydl.download([url])
                except Exception as fallback_error:
                    logger.error(f"Fallback download also failed: {str(fallback_error)}")
                    return False, video_id, None
            
            # Find the subtitle file - check for all language variants and possible naming patterns
            subtitle_path = None
            potential_paths = []
            
            # First check what files were actually created
            created_files = list(output_dir.glob(f"{video_id}*.srt"))
            logger.info(f"Created subtitle files: {created_files}")
            
            # Also check if any .srt files exist in the directory
            all_srt_files = list(output_dir.glob("*.srt"))
            logger.info(f"All SRT files in directory: {all_srt_files}")
            
            if has_manual_subtitles:
                for lang in langs:
                    potential_paths.extend([
                        output_dir / f"{video_id}.{lang}.srt",
                        output_dir / f"{video_id}.{lang}.en.srt"
                    ])
            elif has_auto_subtitles:
                for lang in langs:
                    potential_paths.extend([
                        output_dir / f"{video_id}.{lang}.auto.srt",
                        output_dir / f"{video_id}.{lang}.srt",
                        output_dir / f"{video_id}.en.srt",
                        output_dir / f"{video_id}.en-US.srt"
                    ])
            
            # Also add any files that were actually created
            potential_paths.extend(created_files)
            
            logger.info(f"Checking potential subtitle paths: {potential_paths}")
            
            # Use the first subtitle file that exists
            for path in potential_paths:
                logger.info(f"Checking if path exists: {path}")
                if path.exists():
                    subtitle_path = path
                    logger.info(f"Found subtitle file: {subtitle_path}")
                    break
            
            if subtitle_path and subtitle_path.exists():
                logger.info(f"Subtitles saved to: {subtitle_path}")
                
                # Save subtitle content to a simpler text file
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    subtitle_content = f.read()
                    
                # Process subtitle content to extract just the text
                text_content = self.extract_subtitle_text(subtitle_content)
                text_file_path = output_dir / f"{video_id}_subtitles.txt"
                
                with open(text_file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                logger.info(f"Subtitle text extracted to: {text_file_path}")
                return True, video_id, str(text_file_path)
            else:
                logger.warning(f"Failed to download subtitles. Checked paths: {potential_paths}")
                logger.warning(f"Files in subtitle directory: {list(output_dir.glob('*'))}")
                return False, video_id, None
                
        except Exception as e:
            logger.error(f"Error downloading subtitles: {str(e)}")
            return False, "unknown", None
    
    def extract_subtitle_text(self, subtitle_content: str) -> str:
        """
        Extract plain text from SRT subtitle format, removing timestamps and counters
        
        Args:
            subtitle_content: The SRT subtitle content
            
        Returns:
            Clean text content
        """
        import re
        
        # Remove counters and timestamps (lines with --> in them)
        lines = subtitle_content.split('\n')
        text_lines = []
        i = 0
        
        while i < len(lines):
            # Skip counter lines (just numbers)
            if lines[i].strip().isdigit():
                i += 1
                continue
            
            # Skip timestamp lines
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
    
    def download_video(self, url: str, output_path: Optional[Union[str, Path]] = None,
                      resolution: str = '720p', with_audio: bool = True) -> Tuple[str, str]:
        """
        Download a YouTube video
        
        Args:
            url: YouTube video URL
            output_path: Path to save the video (default: videos directory)
            resolution: Preferred video resolution (default: 720p)
            with_audio: Whether to include audio (default: True)
            
        Returns:
            Tuple of (file path, video_id)
        """
        try:
            video_id = self.extract_video_id(url)
            
            # Prepare output path
            if output_path is None:
                output_path = self.data_dir / "video" / f"{video_id}.mp4"
            else:
                output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Configure format selection based on resolution and audio preference
            format_selector = f'bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]' if with_audio else f'bestvideo[height<={resolution[:-1]}]'
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': format_selector,
                'outtmpl': str(output_path),
                'quiet': True,
                'no_warnings': False,
                'ignoreerrors': False,
            }
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if output_path.exists():
                logger.info(f"Video downloaded to: {output_path}")
                return str(output_path), video_id
            else:
                raise FileNotFoundError(f"Expected output file not found: {output_path}")
                
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
    
    def download_thumbnail(self, url: str, output_path: Optional[Union[str, Path]] = None) -> Tuple[str, str]:
        """
        Download the thumbnail image for a YouTube video
        
        Args:
            url: YouTube video URL
            output_path: Path to save the thumbnail (default: thumbnails directory)
            
        Returns:
            Tuple of (thumbnail path, video_id)
        """
        import requests
        from PIL import Image
        
        try:
            # Get video info to extract thumbnail URL
            video_info = self.get_video_info(url)
            video_id = video_info['id']
            thumbnail_url = video_info['thumbnail_url']
            
            if not thumbnail_url:
                raise ValueError(f"No thumbnail URL found for video: {url}")
            
            # Prepare output path
            if output_path is None:
                output_path = self.data_dir / "thumbnails" / f"{video_id}.jpg"
            else:
                output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the thumbnail
            response = requests.get(thumbnail_url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Thumbnail downloaded to: {output_path}")
            return str(output_path), video_id
            
        except Exception as e:
            logger.error(f"Error downloading thumbnail: {str(e)}")
            raise
    
    def process_playlist(self, playlist_url: str, download_type: str = 'audio', 
                        output_dir: Optional[Union[str, Path]] = None, 
                        limit: int = 0) -> List[Dict[str, Any]]:
        """
        Process videos from a YouTube playlist
        
        Args:
            playlist_url: YouTube playlist URL
            download_type: What to download ('audio', 'video', 'subtitles', 'info', 'all')
            output_dir: Directory to save files (default: data_dir)
            limit: Maximum number of videos to process (0 for all)
            
        Returns:
            List of dictionaries with processed video information
        """
        try:
            # Configure output directory
            if output_dir is None:
                output_dir = self.data_dir
            else:
                output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get playlist information
            ydl_opts = {
                'extract_flat': True,  # Only extract video info without downloading
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True  # Skip unavailable videos
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if not playlist_info:
                    raise ValueError(f"Could not extract playlist info from: {playlist_url}")
                    
                # Extract playlist details
                playlist_title = playlist_info.get('title', 'Unknown Playlist')
                
                # Get videos in playlist
                entries = list(playlist_info.get('entries', []))
                
                if not entries:
                    logger.warning(f"No videos found in playlist: {playlist_title}")
                    return []
                    
                total_videos = len(entries)
                logger.info(f"Found {total_videos} videos in playlist: {playlist_title}")
                
                # Apply limit if specified
                if limit > 0:
                    entries = entries[:limit]
                    logger.info(f"Processing first {len(entries)} videos (limit: {limit})")
            
            # Process each video
            results = []
            for i, entry in enumerate(entries):
                try:
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    video_title = entry.get('title', f"Video {i+1}")
                    
                    logger.info(f"Processing video {i+1}/{len(entries)}: {video_title}")
                    result = {"title": video_title, "id": entry['id'], "url": video_url, "downloads": {}}
                    
                    # Process according to download type
                    if download_type in ('all', 'info'):
                        video_info = self.get_video_info(video_url, save_info=True)
                        result['info'] = video_info
                        result['downloads']['info'] = self._save_info_json(video_info)
                    
                    if download_type in ('all', 'audio'):
                        audio_path, _ = self.download_audio(video_url, 
                                                          output_path=output_dir / "audio" / f"{entry['id']}.mp3")
                        result['downloads']['audio'] = audio_path
                    
                    if download_type in ('all', 'video'):
                        video_path, _ = self.download_video(video_url, 
                                                          output_path=output_dir / "video" / f"{entry['id']}.mp4")
                        result['downloads']['video'] = video_path
                    
                    if download_type in ('all', 'subtitles'):
                        _, _, subtitle_path = self.download_subtitles(video_url, 
                                                                   output_dir=output_dir / "subtitles")
                        if subtitle_path:
                            result['downloads']['subtitles'] = subtitle_path
                    
                    if download_type in ('all', 'thumbnail'):
                        thumbnail_path, _ = self.download_thumbnail(video_url, 
                                                                 output_path=output_dir / "thumbnails" / f"{entry['id']}.jpg")
                        result['downloads']['thumbnail'] = thumbnail_path
                        
                    results.append(result)
                    
                    # Small delay between downloads
                    time.sleep(1.5)
                    
                except Exception as e:
                    logger.error(f"Error processing video {entry['id']}: {str(e)}")
                    # Continue with next video
            
            logger.info(f"Playlist processing complete. Processed {len(results)} videos.")
            return results
            
        except Exception as e:
            logger.error(f"Error processing playlist: {str(e)}")
            raise
    
    def get_transcript_from_subtitles(self, url: str, langs: List[str] = ['en', 'en-US']) -> Optional[str]:
        """
        Get transcript text from video subtitles
        
        Args:
            url: YouTube video URL
            langs: List of language codes to try (default: ['en', 'en-US'])
            
        Returns:
            Transcript text or None if no subtitles found
        """
        try:
            video_id = self.extract_video_id(url)
            
            # First check if subtitle text already exists
            subtitle_dir = self.data_dir / "subtitles"
            text_file_path = subtitle_dir / f"{video_id}_subtitles.txt"
            
            if text_file_path.exists():
                logger.info(f"Found existing subtitle text file: {text_file_path}")
                with open(text_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Check if any .srt files exist for this video
            existing_srt_files = list(subtitle_dir.glob(f"{video_id}*.srt"))
            if existing_srt_files:
                logger.info(f"Found existing SRT file(s): {existing_srt_files}")
                # Use the first available SRT file
                srt_file = existing_srt_files[0]
                with open(srt_file, 'r', encoding='utf-8') as f:
                    subtitle_content = f.read()
                
                # Extract text and save as text file
                text_content = self.extract_subtitle_text(subtitle_content)
                with open(text_file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                logger.info(f"Extracted subtitle text to: {text_file_path}")
                return text_content
            
            # If no existing files, try to download
            success, video_id, subtitle_path = self.download_subtitles(url, langs=langs)
            
            if success and subtitle_path:
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"No subtitles found for video: {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting transcript: {str(e)}")
            return None
    
    def search_video(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos matching a query
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: 5)
            
        Returns:
            List of video information dictionaries
        """
        from youtubesearchpython import VideosSearch
        
        try:
            videos_search = VideosSearch(query, limit=max_results)
            results = videos_search.result().get('result', [])
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.get('id', ''),
                    "title": result.get('title', ''),
                    "url": result.get('link', ''),
                    "duration": result.get('duration', ''),
                    "views": result.get('viewCount', {}).get('text', 'Unknown'),
                    "thumbnail": result.get('thumbnails', [{}])[0].get('url', '') if result.get('thumbnails') else '',
                    "channel_name": result.get('channel', {}).get('name', ''),
                    "channel_url": result.get('channel', {}).get('link', ''),
                    "published_time": result.get('publishedTime', '')
                })
            
            logger.info(f"Found {len(formatted_results)} videos matching query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching videos: {str(e)}")
            return []
        
    def extract_subtitles_from_info(self, video_info: Union[str, Dict[str, Any]], 
                              output_dir: Optional[Union[str, Path]] = None, 
                              langs: List[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Extract subtitles from a video info dictionary or JSON file
        
        Args:
            video_info: Video info dictionary or path to JSON file
            output_dir: Directory to save subtitles (default: subtitles directory)
            langs: List of language codes to extract (default: ['en', 'en-US'])
            
        Returns:
            Tuple of (success, video_id, subtitle_path or None)
        """
        try:
            # Load video info if it's a file path
            if isinstance(video_info, str):
                with open(video_info, 'r', encoding='utf-8') as f:
                    video_info = json.load(f)
            
            video_id = video_info.get('id', 'unknown')
            
            # Setup output directory
            if output_dir is None:
                output_dir = self.data_dir / "subtitles"
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Default language list
            if langs is None:
                langs = ['en', 'en-US']
            
            # Get subtitles information
            subtitles_info = video_info.get('subtitles', {})
            
            # Check for manual subtitles first
            manual_subs = subtitles_info.get('manual', {})
            auto_subs = subtitles_info.get('automatic', {})
            
            # Try to find subtitles in preferred languages
            subtitle_url = None
            subtitle_ext = None
            is_manual = False
            
            # First try manual subtitles
            for lang in langs:
                if lang in manual_subs and manual_subs[lang]:
                    # Prefer certain formats: srt > vtt > json3 > others
                    formats_priority = ['srt', 'vtt', 'json3', 'srv1', 'srv2', 'srv3', 'ttml']
                    
                    # Find the best format available
                    available_formats = manual_subs[lang]
                    selected_format = None
                    
                    for fmt in formats_priority:
                        for format_info in available_formats:
                            if format_info.get('ext') == fmt:
                                subtitle_url = format_info.get('url')
                                subtitle_ext = fmt
                                selected_format = format_info
                                is_manual = True
                                break
                        
                        if selected_format:
                            break
                    
                    if selected_format:
                        logger.info(f"Found manual subtitles in {lang} format: {subtitle_ext}")
                        break
            
            # If no manual subtitles, try automatic ones
            if not subtitle_url:
                for lang in langs:
                    if lang in auto_subs and auto_subs[lang]:
                        # Prefer certain formats: srt > vtt > json3 > others
                        formats_priority = ['vtt', 'srt', 'json3', 'srv1']
                        
                        # Find the best format available
                        available_formats = auto_subs[lang]
                        selected_format = None
                        
                        for fmt in formats_priority:
                            for format_info in available_formats:
                                if format_info.get('ext') == fmt:
                                    subtitle_url = format_info.get('url')
                                    subtitle_ext = fmt
                                    selected_format = format_info
                                    break
                            
                            if selected_format:
                                break
                        
                        if selected_format:
                            logger.info(f"Found automatic subtitles in {lang} format: {subtitle_ext}")
                            break
            
            if not subtitle_url:
                logger.warning(f"No subtitles found in languages: {langs}")
                return False, video_id, None
            
            # Download and save the subtitle file
            import requests
            
            try:
                response = requests.get(subtitle_url, timeout=10)
                response.raise_for_status()
                
                # Construct the output file name
                subtitle_type = "manual" if is_manual else "auto"
                subtitle_path = output_dir / f"{video_id}.{langs[0]}.{subtitle_type}.{subtitle_ext}"
                
                with open(subtitle_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Subtitles saved to: {subtitle_path}")
                
                # Convert to plain text if it's not already
                if subtitle_ext in ['srt', 'vtt', 'ttml', 'json3']:
                    text_content = self._convert_subtitle_to_text(subtitle_path)
                    text_file_path = output_dir / f"{video_id}_subtitles.txt"
                    
                    with open(text_file_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    
                    logger.info(f"Subtitle text extracted to: {text_file_path}")
                    return True, video_id, str(text_file_path)
                
                return True, video_id, str(subtitle_path)
                
            except Exception as e:
                logger.error(f"Error downloading subtitles from URL: {str(e)}")
                return False, video_id, None
                
        except Exception as e:
            logger.error(f"Error extracting subtitles from info: {str(e)}")
            return False, "unknown", None
    
    def _convert_subtitle_to_text(self, subtitle_path: Union[str, Path]) -> str:
        """
        Convert subtitle file to plain text, handling different formats
        
        Args:
            subtitle_path: Path to the subtitle file
            
        Returns:
            Plain text content
        """
        subtitle_path = Path(subtitle_path)
        subtitle_ext = subtitle_path.suffix.lower()
        
        with open(subtitle_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        if subtitle_ext == '.srt':
            return self.extract_subtitle_text(content)
        elif subtitle_ext == '.vtt':
            # Remove WebVTT header and convert like SRT
            if content.startswith('WEBVTT'):
                content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
            return self.extract_subtitle_text(content)
        elif subtitle_ext == '.json3':
            # Parse JSON3 format
            try:
                data = json.loads(content)
                events = data.get('events', [])
                text_parts = []
                
                for event in events:
                    if 'segs' in event:
                        for seg in event['segs']:
                            if 'utf8' in seg:
                                text_parts.append(seg['utf8'])
                
                return ' '.join(text_parts)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON3 subtitle format")
                return content
        else:
            # For unknown formats, try to extract text with the SRT method
            return self.extract_subtitle_text(content)
