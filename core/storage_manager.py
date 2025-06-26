#!/usr/bin/env python3
"""
Storage Manager Module

This module handles file operations and data persistence for the VidSage application.
It manages saving and loading transcripts, summaries, embeddings, and other data.
"""

import os
import json
import pickle
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union, BinaryIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StorageManager:
    """Manages persistent storage of files and data for VidSage"""
    
    def __init__(self, base_dir: str = "data"):
        """
        Initialize the storage manager with a base directory
        
        Args:
            base_dir: Base directory for storing all data
        """
        # Create the base directory structure
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different data types
        self.audio_dir = self.base_dir / "audio"
        self.transcript_dir = self.base_dir / "transcripts"
        self.summary_dir = self.base_dir / "summaries"
        self.embedding_dir = self.base_dir / "embeddings"
        self.vectorstore_dir = self.base_dir / "vectorstores"
        
        # Make sure all directories exist
        for directory in [self.audio_dir, self.transcript_dir, self.summary_dir, 
                         self.embedding_dir, self.vectorstore_dir]:
            directory.mkdir(exist_ok=True)
        
        # Current video ID being processed
        self.current_video_id = None
        
        logger.info(f"Storage Manager initialized at {self.base_dir}")
    
    def set_current_video(self, video_id: str) -> None:
        """
        Set the current video ID for all operations
        
        Args:
            video_id: YouTube video ID
        """
        self.current_video_id = video_id
        logger.info(f"Current video set to: {video_id}")
    
    def get_video_path(self, video_id: Optional[str] = None) -> Path:
        """
        Get the path for a specific video's files
        
        Args:
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Path to the video directory
        """
        video_id = video_id or self.current_video_id
        if not video_id:
            raise ValueError("No video ID specified and no current video set")
        return self.base_dir / video_id
    
    def save_audio(self, audio_data: BinaryIO, video_id: Optional[str] = None, 
                  filename: Optional[str] = None) -> Path:
        """
        Save audio data for a video
        
        Args:
            audio_data: Audio data to save
            video_id: Optional video ID (uses current_video_id if None)
            filename: Optional filename (defaults to video_id.mp3)
            
        Returns:
            Path to the saved audio file
        """
        video_id = video_id or self.current_video_id
        if not filename:
            filename = f"{video_id}.mp3"
            
        # Create video-specific directory if it doesn't exist
        video_dir = self.audio_dir / video_id
        video_dir.mkdir(exist_ok=True)
        
        # Save the audio file
        file_path = video_dir / filename
        with open(file_path, 'wb') as f:
            f.write(audio_data.read())
            
        logger.info(f"Audio saved to {file_path}")
        return file_path
    
    def save_transcript(self, video_id: str, transcript_text: str, segments: Optional[list] = None) -> Path:
        """
        Save transcript text and optional segments for a video
        
        Args:
            video_id: YouTube video ID
            transcript_text: Transcript text to save
            segments: Optional list of transcript segments with timestamps
            
        Returns:
            Path to the saved transcript file
        """
        # Create video-specific directory if it doesn't exist
        video_dir = self.transcript_dir / video_id
        video_dir.mkdir(exist_ok=True)
        
        # Save the transcript
        file_path = video_dir / f"{video_id}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(transcript_text)
        
        # Save segments if provided
        if segments:
            segments_path = video_dir / f"{video_id}_segments.json"
            with open(segments_path, 'w', encoding='utf-8') as f:
                json.dump(segments, f, ensure_ascii=False, indent=2)
            logger.info(f"Transcript segments saved to {segments_path}")
            
        logger.info(f"Transcript saved to {file_path}")
        return file_path
    
    def save_summary(self, summary_text: str, summary_type: str = "default", 
                    video_id: Optional[str] = None) -> Path:
        """
        Save summary text for a video
        
        Args:
            summary_text: Summary text to save
            summary_type: Type of summary (concise, detailed, bullet, sections)
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Path to the saved summary file
        """
        video_id = video_id or self.current_video_id
        
        # Create video-specific directory if it doesn't exist
        video_dir = self.summary_dir / video_id
        video_dir.mkdir(exist_ok=True)
        
        # Save the summary
        file_path = video_dir / f"{video_id}_{summary_type}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        logger.info(f"{summary_type.capitalize()} summary saved to {file_path}")
        return file_path
    
    def save_video_info(self, video_info: Dict[str, Any], video_id: Optional[str] = None) -> Path:
        """
        Save video metadata information
        
        Args:
            video_info: Dictionary containing video metadata
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Path to the saved info file
        """
        video_id = video_id or self.current_video_id
        
        # Create video-specific directory if it doesn't exist
        video_dir = self.base_dir / video_id
        video_dir.mkdir(exist_ok=True)
        
        # Save the video info
        file_path = video_dir / f"{video_id}_info.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(video_info, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Video info saved to {file_path}")
        return file_path
    
    def save_vectorstore(self, vectorstore_obj: Any, video_id: Optional[str] = None) -> Path:
        """
        Save a vector store object for a video using Chroma's persistence
        
        Args:
            vectorstore_obj: Vector store object to save
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Path to the saved vector store directory
        """
        video_id = video_id or self.current_video_id
        
        # Create video-specific directory if it doesn't exist
        video_dir = self.vectorstore_dir / video_id
        video_dir.mkdir(exist_ok=True)
        
        # Use directory path for Chroma persistence
        persist_path = video_dir / "chroma_db"
        
        try:
            # ChromaDB vectorstores have a persist method or can be recreated with persistence
            if hasattr(vectorstore_obj, 'persist'):
                vectorstore_obj.persist()
            
            # Create a marker file to indicate vectorstore exists
            marker_file = video_dir / f"{video_id}_vectorstore.marker"
            with open(marker_file, 'w') as f:
                f.write(f"Vector store persisted at: {persist_path}")
            
            logger.info(f"Vector store saved to {persist_path}")
            return persist_path
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            # Fallback: create a simple marker indicating we need to recreate
            marker_file = video_dir / f"{video_id}_vectorstore.recreate"
            with open(marker_file, 'w') as f:
                f.write("Vector store needs recreation")
            logger.info(f"Vector store marker created at {marker_file}")
            return video_dir
    
    def load_transcript(self, video_id: Optional[str] = None) -> Optional[str]:
        """
        Load transcript text for a video
        
        Args:
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Transcript text if found, None otherwise
        """
        video_id = video_id or self.current_video_id
        file_path = self.transcript_dir / video_id / f"{video_id}.txt"
        
        if not file_path.exists():
            logger.warning(f"Transcript file not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
            
        logger.info(f"Transcript loaded from {file_path}")
        return transcript
    
    def load_summary(self, summary_type: str = "default", video_id: Optional[str] = None) -> Optional[str]:
        """
        Load summary text for a video
        
        Args:
            summary_type: Type of summary (concise, detailed, bullet, sections)
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Summary text if found, None otherwise
        """
        video_id = video_id or self.current_video_id
        file_path = self.summary_dir / video_id / f"{video_id}_{summary_type}.txt"
        
        if not file_path.exists():
            logger.warning(f"Summary file not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            summary = f.read()
            
        logger.info(f"{summary_type.capitalize()} summary loaded from {file_path}")
        return summary
    
    def load_video_info(self, video_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load video metadata information
        
        Args:
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Dictionary containing video metadata if found, None otherwise
        """
        video_id = video_id or self.current_video_id
        file_path = self.base_dir / video_id / f"{video_id}_info.json"
        
        if not file_path.exists():
            logger.warning(f"Video info file not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            video_info = json.load(f)
            
        logger.info(f"Video info loaded from {file_path}")
        return video_info
    
    def load_vectorstore(self, video_id: Optional[str] = None) -> Any:
        """
        Load a vector store object for a video
        
        Args:
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            Vector store object if found, None otherwise
        """
        video_id = video_id or self.current_video_id
        
        # Check for marker file first
        marker_file = self.vectorstore_dir / video_id / f"{video_id}_vectorstore.marker"
        recreate_file = self.vectorstore_dir / video_id / f"{video_id}_vectorstore.recreate"
        
        if marker_file.exists():
            logger.info(f"Vector store marker found for {video_id}")
            return "marker_exists"  # Signal that vectorstore was created but needs reconstruction
        elif recreate_file.exists():
            logger.info(f"Vector store needs recreation for {video_id}")
            return "needs_recreation"
        
        # Fallback: try to load from pickle (for backward compatibility)
        file_path = self.vectorstore_dir / video_id / f"{video_id}_vectorstore.pkl"
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    vectorstore = pickle.load(f)
                logger.info(f"Vector store loaded from {file_path}")
                return vectorstore
            except Exception as e:
                logger.warning(f"Could not load pickled vectorstore: {e}")
        
        logger.warning(f"Vector store file not found: {video_id}")
        return None
    
    def has_transcript(self, video_id: Optional[str] = None) -> bool:
        """
        Check if a transcript exists for the video
        
        Args:
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            True if transcript exists, False otherwise
        """
        video_id = video_id or self.current_video_id
        file_path = self.transcript_dir / video_id / f"{video_id}.txt"
        return file_path.exists()
    
    def has_summary(self, summary_type: str = "default", video_id: Optional[str] = None) -> bool:
        """
        Check if a summary exists for the video
        
        Args:
            summary_type: Type of summary (concise, detailed, bullet, sections)
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            True if summary exists, False otherwise
        """
        video_id = video_id or self.current_video_id
        file_path = self.summary_dir / video_id / f"{video_id}_{summary_type}.txt"
        return file_path.exists()
    
    def has_vectorstore(self, video_id: Optional[str] = None) -> bool:
        """
        Check if a vector store exists for the video
        
        Args:
            video_id: Optional video ID (uses current_video_id if None)
            
        Returns:
            True if vector store exists, False otherwise
        """
        video_id = video_id or self.current_video_id
        
        # Check for new marker files
        marker_file = self.vectorstore_dir / video_id / f"{video_id}_vectorstore.marker"
        recreate_file = self.vectorstore_dir / video_id / f"{video_id}_vectorstore.recreate"
        
        if marker_file.exists() or recreate_file.exists():
            return True
            
        # Check for old pickle file (backward compatibility)
        file_path = self.vectorstore_dir / video_id / f"{video_id}_vectorstore.pkl"
        return file_path.exists()
    
    def cleanup(self, video_id: Optional[str] = None) -> None:
        """
        Delete all files associated with a video
        
        Args:
            video_id: Optional video ID (uses current_video_id if None)
        """
        import shutil
        
        video_id = video_id or self.current_video_id
        
        # Directories that may contain files for this video
        dirs_to_check = [
            self.audio_dir / video_id,
            self.transcript_dir / video_id,
            self.summary_dir / video_id,
            self.embedding_dir / video_id,
            self.vectorstore_dir / video_id,
            self.base_dir / video_id
        ]
        
        # Remove directories if they exist
        for dir_path in dirs_to_check:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f"Removed directory: {dir_path}")
        
        logger.info(f"Cleanup completed for video: {video_id}")
