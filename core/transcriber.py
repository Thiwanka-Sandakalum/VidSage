import os
import whisper
from typing import Optional, Dict, Tuple

class Transcriber:
    """Transcribe audio files to text using OpenAI Whisper."""
    
    def __init__(self, storage_manager, model_name: str = "base"):
        """
        Initialize the Transcriber.
        
        Args:
            storage_manager: Instance of StorageManager for file operations
            model_name: Whisper model name ("tiny", "base", "small", "medium", "large")
        """
        self.storage_manager = storage_manager
        self.model_name = model_name
        self.model = None  # Lazy-loaded
    
    def _load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            print(f"Loading Whisper {self.model_name} model...")
            self.model = whisper.load_model(self.model_name)
            print("Model loaded successfully.")
    
    def transcribe(self, video_id: str) -> Tuple[bool, Optional[str]]:
        """
        Transcribe an audio file using Whisper.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Tuple containing (success status, transcript text or None)
        """
        audio_path = self.storage_manager.get_audio_path(video_id)
        transcript_path = self.storage_manager.get_transcript_path(video_id)
        
        # Check if audio file exists
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return False, None
        
        # Check if transcript already exists
        if os.path.exists(transcript_path):
            transcript = self.storage_manager.read_file(transcript_path)
            if transcript:
                print("Using existing transcript.")
                return True, transcript
        
        try:
            # Load model if not loaded
            self._load_model()
            
            # Transcribe audio
            print("Transcribing audio... This may take a while.")
            result = self.model.transcribe(audio_path)
            
            # Extract transcript text
            transcript = result["text"]
            
            # Save transcript to file
            self.storage_manager.save_file(transcript, transcript_path)
            
            return True, transcript
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return False, None