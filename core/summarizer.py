import os
from typing import Tuple, Optional, Dict, Any

class Summarizer:
    """Generate summaries of transcripts using Ollama."""
    
    def __init__(self, storage_manager, model_name: str = "llama3"):
        """
        Initialize the Summarizer.
        
        Args:
            storage_manager: Instance of StorageManager for file operations
            model_name: Ollama model name
        """
        self.storage_manager = storage_manager
        self.model_name = model_name
        
        # Attempt to import ollama module, with graceful fallback
        try:
            import ollama
            self.ollama = ollama
        except ImportError:
            print("Warning: ollama module not found. Summarization will not be available.")
            self.ollama = None
    
    def summarize(self, video_id: str, max_tokens: int = 300) -> Tuple[bool, Optional[str]]:
        """
        Summarize a video transcript.
        
        Args:
            video_id: YouTube video ID
            max_tokens: Maximum number of tokens for the summary
            
        Returns:
            Tuple containing (success status, summary text or None)
        """
        transcript_path = self.storage_manager.get_transcript_path(video_id)
        summary_path = self.storage_manager.get_summary_path(video_id)
        
        # Check if transcript exists
        if not os.path.exists(transcript_path):
            print(f"Transcript not found: {transcript_path}")
            return False, None
        
        # Check if summary already exists
        if os.path.exists(summary_path):
            summary = self.storage_manager.read_file(summary_path)
            if summary:
                print("Using existing summary.")
                return True, summary
        
        # Check if ollama is available
        if self.ollama is None:
            print("Summarization not available: ollama module not found.")
            return False, None
        
        # Read transcript
        transcript = self.storage_manager.read_file(transcript_path)
        if not transcript:
            return False, None
        
        # Get video metadata
        metadata = self.storage_manager.read_metadata(video_id)
        title = metadata.get("title", "Unknown") if metadata else "Unknown"
        
        try:
            # Create prompt for summarization
            prompt = f"""
            Please provide a concise and informative summary of the following transcript from a YouTube video titled "{title}".
            Focus on the main topics, key points, and conclusions.
            
            TRANSCRIPT:
            {transcript[:9000]}  # Limit transcript length to avoid token limits
            
            SUMMARY:
            """
            
            print("Generating summary... This may take a moment.")
            
            # Generate summary using Ollama
            response = self.ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            
            # Extract summary text
            summary = response['message']['content'].strip()
            
            # Save summary to file
            self.storage_manager.save_file(summary, summary_path)
            
            return True, summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return False, None