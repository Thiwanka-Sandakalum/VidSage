#!/usr/bin/env python3
"""
Text-to-Speech Generator Module

This module handles converting text to speech using gTTS.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Union, BinaryIO
import logging

# TTS library
from gtts import gTTS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TTSGenerator:
    """Converts text to speech using gTTS"""
    
    def __init__(self, language: str = "en", slow: bool = False):
        """
        Initialize the TTS generator
        
        Args:
            language: Language code for TTS
            slow: Whether to speak slowly
        """
        self.language = language
        self.slow = slow
        
        logger.info(f"TTS Generator initialized with language: {language}")
    
    def generate_audio(self, text: str, output_path: Optional[Path] = None) -> Union[Path, BinaryIO]:
        """
        Generate audio from text
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save the audio file
            
        Returns:
            Path to saved audio file or file-like object
        """
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            
            if output_path:
                # Save to file
                tts.save(str(output_path))
                logger.info(f"Audio saved to {output_path}")
                return output_path
            else:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                tts.save(temp_file.name)
                temp_file.close()
                
                # Open the file in binary mode and return
                file_obj = open(temp_file.name, 'rb')
                
                # Schedule file for deletion after it's closed
                # This is a workaround since we can't use delete=True with the file object
                def cleanup_temp_file():
                    try:
                        file_obj.close()
                        os.unlink(temp_file.name)
                    except:
                        pass
                
                import atexit
                atexit.register(cleanup_temp_file)
                
                logger.info(f"Audio generated to memory (temp file: {temp_file.name})")
                return file_obj
                
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise
    
    def generate_audio_segments(self, text: str, max_chars: int = 1000,
                             output_dir: Optional[Path] = None) -> list[Path]:
        """
        Generate audio in segments for long text
        
        Args:
            text: Text to convert to speech
            max_chars: Maximum characters per segment
            output_dir: Optional directory to save audio files
            
        Returns:
            List of paths to saved audio files
        """
        # Split text into segments
        segments = []
        current_segment = ""
        
        # Split by sentences (roughly)
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            # Add period back except for the last sentence
            if i < len(sentences) - 1:
                sentence += '.'
                
            # Check if adding this sentence would exceed max_chars
            if len(current_segment) + len(sentence) + 1 > max_chars and current_segment:
                segments.append(current_segment)
                current_segment = sentence
            else:
                if current_segment:
                    current_segment += ' ' + sentence
                else:
                    current_segment = sentence
        
        # Add the last segment if not empty
        if current_segment:
            segments.append(current_segment)
            
        logger.info(f"Split text into {len(segments)} segments")
        
        # Generate audio for each segment
        audio_files = []
        for i, segment in enumerate(segments):
            try:
                if output_dir:
                    output_file = output_dir / f"segment_{i+1}.mp3"
                    self.generate_audio(segment, output_file)
                    audio_files.append(output_file)
                else:
                    # Create temporary directory if needed
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir) / f"segment_{i+1}.mp3"
                        self.generate_audio(segment, temp_path)
                        audio_files.append(temp_path)
                        
            except Exception as e:
                logger.error(f"Error generating audio for segment {i+1}: {str(e)}")
                continue
                
        return audio_files
    
    def combine_audio_files(self, audio_files: list[Path], output_path: Path) -> Path:
        """
        Combine multiple audio files into one
        
        Args:
            audio_files: List of audio file paths
            output_path: Path to save the combined audio
            
        Returns:
            Path to the combined audio file
        """
        try:
            from pydub import AudioSegment
            
            # Check if there are files to combine
            if not audio_files:
                raise ValueError("No audio files provided")
                
            # Combine audio segments
            combined = AudioSegment.empty()
            for file_path in audio_files:
                segment = AudioSegment.from_mp3(str(file_path))
                combined += segment
                
            # Export combined audio
            combined.export(str(output_path), format="mp3")
            
            logger.info(f"Combined audio saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error combining audio files: {str(e)}")
            raise
