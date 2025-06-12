import os
import json
from datetime import datetime
import shutil
from typing import Optional, Dict, Any, Union

class StorageManager:
    """Manages file I/O operations and temporary storage for the application."""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the Storage Manager.
        
        Args:
            base_dir: Base directory for storing files. If None, uses 'data' in current directory.
        """
        if base_dir is None:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_dir = os.path.join(current_dir, "data")
        else:
            self.base_dir = base_dir
            
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.base_dir,
            os.path.join(self.base_dir, "audio"),
            os.path.join(self.base_dir, "transcripts"),
            os.path.join(self.base_dir, "summaries"),
            os.path.join(self.base_dir, "embeddings"),
            os.path.join(self.base_dir, "tts")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def generate_filename(self, video_id: str, prefix: str = "", extension: str = "") -> str:
        """
        Generate a filename based on video ID and current timestamp.
        
        Args:
            video_id: YouTube video ID
            prefix: Optional prefix for the filename
            extension: File extension (without dot)
            
        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        
        return f"{prefix}_{video_id}_{timestamp}{extension}"
    
    def get_audio_path(self, video_id: str) -> str:
        """Get path for storing audio files."""
        return os.path.join(self.base_dir, "audio", f"{video_id}.mp3")
    
    def get_transcript_path(self, video_id: str) -> str:
        """Get path for storing transcript files."""
        return os.path.join(self.base_dir, "transcripts", f"{video_id}.txt")
    
    def get_summary_path(self, video_id: str) -> str:
        """Get path for storing summary files."""
        return os.path.join(self.base_dir, "summaries", f"{video_id}.txt")
    
    def get_embeddings_path(self, video_id: str) -> str:
        """Get path for storing embeddings."""
        return os.path.join(self.base_dir, "embeddings", video_id)
    
    def get_tts_path(self, video_id: str) -> str:
        """Get path for storing text-to-speech audio files."""
        return os.path.join(self.base_dir, "tts", f"{video_id}.mp3")
    
    def save_file(self, content: Union[str, bytes], filepath: str) -> bool:
        """
        Save content to a file.
        
        Args:
            content: Content to save (string or bytes)
            filepath: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            mode = "w" if isinstance(content, str) else "wb"
            with open(filepath, mode) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving file {filepath}: {e}")
            return False
    
    def read_file(self, filepath: str, binary: bool = False) -> Optional[Union[str, bytes]]:
        """
        Read content from a file.
        
        Args:
            filepath: Path to the file
            binary: Whether to read in binary mode
            
        Returns:
            File content or None if file doesn't exist or error occurs
        """
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return None
        
        try:
            mode = "rb" if binary else "r"
            with open(filepath, mode) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None
    
    def save_metadata(self, video_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Save metadata for a video.
        
        Args:
            video_id: YouTube video ID
            metadata: Dictionary of metadata to save
            
        Returns:
            True if successful, False otherwise
        """
        metadata_file = os.path.join(self.base_dir, f"{video_id}_metadata.json")
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return False
    
    def read_metadata(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Read metadata for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary of metadata or None if file doesn't exist or error occurs
        """
        metadata_file = os.path.join(self.base_dir, f"{video_id}_metadata.json")
        if not os.path.exists(metadata_file):
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading metadata: {e}")
            return None
    
    def cleanup(self, video_id: str) -> bool:
        """
        Clean up all files associated with a video ID.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # List of files to remove
            files_to_remove = [
                self.get_audio_path(video_id),
                self.get_transcript_path(video_id),
                self.get_summary_path(video_id),
                self.get_tts_path(video_id),
                os.path.join(self.base_dir, f"{video_id}_metadata.json")
            ]
            
            # Remove files if they exist
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Remove embeddings directory if it exists
            embeddings_dir = self.get_embeddings_path(video_id)
            if os.path.exists(embeddings_dir):
                shutil.rmtree(embeddings_dir)
                
            return True
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False