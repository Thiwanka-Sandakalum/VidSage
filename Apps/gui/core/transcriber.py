#!/usr/bin/env python3
"""
Transcriber Module

This module handles the conversion of speech to text using Whisper API.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Union, BinaryIO
import logging
import whisper
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Transcriber:
    """Converts audio to text using Whisper"""
    
    def __init__(self, model_name: str = "base", device: str = "cpu"):
        """
        Initialize the transcriber with a specific whisper model
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
            device: Device to use for inference (cpu or cuda)
        """
        self.model_name = model_name
        self.device = device
        
        # Load the model lazily when needed
        self._model = None
        
        logger.info(f"Transcriber initialized with model: {model_name} on {device}")
    
    @property
    def model(self):
        """Lazy load the model when needed"""
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self._model = whisper.load_model(self.model_name, device=self.device)
        return self._model
    
    def transcribe_file(self, audio_file: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """
        Transcribe audio from a file or file-like object
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Handle file-like objects
            if hasattr(audio_file, 'read'):
                # Create a temporary file to pass to whisper
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_file.write(audio_file.read())
                    temp_path = temp_file.name
                
                # Process the temporary file
                result = self.model.transcribe(temp_path)
                
                # Clean up
                os.unlink(temp_path)
                
            else:
                # Process a file path directly
                result = self.model.transcribe(str(audio_file))
            
            logger.info(f"Transcription completed, {len(result['text'])} characters")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    def transcribe_with_timestamps(self, audio_file: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """
        Transcribe audio with word-level timestamps
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dictionary with transcription results including word timestamps
        """
        try:
            # Process with word timestamps enabled
            if hasattr(audio_file, 'read'):
                # Create a temporary file to pass to whisper
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_file.write(audio_file.read())
                    temp_path = temp_file.name
                
                # Process with word timestamps
                result = self.model.transcribe(temp_path, word_timestamps=True)
                
                # Clean up
                os.unlink(temp_path)
                
            else:
                # Process a file path directly
                result = self.model.transcribe(str(audio_file), word_timestamps=True)
            
            logger.info(f"Timestamped transcription completed")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio with timestamps: {str(e)}")
            raise
    
    def transcribe_with_segments(self, audio_file: Union[str, Path, BinaryIO], 
                               segment_length_ms: int = 30000) -> Dict[str, Any]:
        """
        Transcribe a long audio file by breaking it into segments
        
        Args:
            audio_file: Path to audio file or file-like object
            segment_length_ms: Length of each segment in milliseconds
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Convert the audio file to a pydub AudioSegment
            if hasattr(audio_file, 'read'):
                # Create a temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_file.write(audio_file.read())
                    temp_path = temp_file.name
                
                # Load audio with pydub
                audio = AudioSegment.from_file(temp_path)
                
                # Clean up
                os.unlink(temp_path)
            else:
                # Load from file path
                audio = AudioSegment.from_file(str(audio_file))
            
            # Break the audio into segments
            duration = len(audio)
            segments = []
            segment_results = []
            
            for start in range(0, duration, segment_length_ms):
                end = min(start + segment_length_ms, duration)
                segment = audio[start:end]
                
                # Save segment to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    segment.export(temp_file.name, format="mp3")
                    segment_path = temp_file.name
                
                # Transcribe the segment
                logger.info(f"Transcribing segment {start/1000:.1f}s - {end/1000:.1f}s")
                result = self.model.transcribe(segment_path)
                
                # Add segment time information
                for s in result["segments"]:
                    s["start"] += start / 1000  # Convert to seconds
                    s["end"] += start / 1000
                
                segments.extend(result["segments"])
                segment_results.append(result["text"])
                
                # Clean up
                os.unlink(segment_path)
            
            # Combine the results
            combined_result = {
                "text": " ".join(segment_results),
                "segments": segments
            }
            
            logger.info(f"Segmented transcription completed, {len(combined_result['text'])} characters")
            return combined_result
            
        except Exception as e:
            logger.error(f"Error transcribing with segments: {str(e)}")
            raise
    
    def format_transcript(self, result: Dict[str, Any], include_timestamps: bool = False) -> str:
        """
        Format transcription results as plain text
        
        Args:
            result: Transcription result dictionary
            include_timestamps: Whether to include segment timestamps
            
        Returns:
            Formatted transcript text
        """
        if not include_timestamps:
            return result.get("text", "")
        
        # Format with timestamps
        formatted_text = ""
        for segment in result.get("segments", []):
            start_time = segment["start"]
            text = segment["text"]
            
            # Format timestamp as [MM:SS]
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            
            formatted_text += f"{timestamp} {text.strip()}\n\n"
        
        return formatted_text
