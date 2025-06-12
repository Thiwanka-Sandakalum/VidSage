import os
from typing import Tuple, Optional

class TTSGenerator:
    """Convert text to speech using pyttsx3."""
    
    def __init__(self, storage_manager, voice_id: int = 0, rate: int = 150, volume: float = 1.0):
        """
        Initialize the TTS Generator.
        
        Args:
            storage_manager: Instance of StorageManager for file operations
            voice_id: Voice ID to use (0 for default)
            rate: Speech rate (words per minute)
            volume: Volume (0.0 to 1.0)
        """
        self.storage_manager = storage_manager
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        self.engine = None
        
        # Try to import pyttsx3, with graceful fallback
        try:
            import pyttsx3
            self.pyttsx3 = pyttsx3
        except ImportError:
            print("Warning: pyttsx3 module not found. Text-to-speech will not be available.")
            self.pyttsx3 = None
    
    def _initialize_engine(self) -> bool:
        """Initialize the TTS engine."""
        if self.pyttsx3 is None:
            return False
        
        if self.engine is None:
            try:
                self.engine = self.pyttsx3.init()
                
                # Set properties
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
                
                # Set voice
                voices = self.engine.getProperty('voices')
                if voices and self.voice_id < len(voices):
                    self.engine.setProperty('voice', voices[self.voice_id].id)
                
                return True
            except Exception as e:
                print(f"Error initializing TTS engine: {e}")
                return False
        
        return True
    
    def generate_audio(self, video_id: str, text: str = None) -> Tuple[bool, Optional[str]]:
        """
        Generate audio from text.
        
        Args:
            video_id: YouTube video ID
            text: Text to convert to speech. If None, use summary.
            
        Returns:
            Tuple containing (success status, audio file path or None)
        """
        if self.pyttsx3 is None:
            print("Text-to-speech not available: pyttsx3 module not found.")
            return False, None
        
        # If no text provided, try to use summary
        if text is None:
            summary_path = self.storage_manager.get_summary_path(video_id)
            
            # Check if summary exists
            if not os.path.exists(summary_path):
                print(f"Summary not found: {summary_path}")
                return False, None
            
            # Read summary
            text = self.storage_manager.read_file(summary_path)
            if not text:
                return False, None
        
        # Get output path
        output_path = self.storage_manager.get_tts_path(video_id)
        
        # Check if TTS already exists
        if os.path.exists(output_path):
            print("Using existing TTS audio.")
            return True, output_path
        
        # Initialize engine
        if not self._initialize_engine():
            return False, None
        
        try:
            print("Generating audio... This may take a moment.")
            
            # Save to file
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            return True, output_path
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return False, None