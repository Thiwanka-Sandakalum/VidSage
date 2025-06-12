#!/usr/bin/env python3
"""YouTube Insight ChatBot CLI"""

import os
import sys
import argparse
import cmd
from typing import List, Optional, Dict, Any
import time

# Add parent directory to sys.path to allow importing project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
try:
    from core.storage_manager import StorageManager
    from core.youtube_processor import YouTubeProcessor
    from core.transcriber import Transcriber
    from core.summarizer import Summarizer
    from core.embedder import Embedder
    from core.tts_generator import TTSGenerator
    from utils.helpers import (
        validate_youtube_url, 
        format_time, 
        format_number,
        clear_screen,
        truncate_text,
        get_file_size,
        check_dependencies
    )
except ImportError as e:
    print(f"Error importing project modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


class YTInsightCLI(cmd.Cmd):
    """Command Line Interface for YouTube Insight ChatBot."""
    
    intro = """
    ╭───────────────────────────────────────────────╮
    │                                               │
    │        YouTube Insight ChatBot - CLI          │
    │                                               │
    │           Analyze YouTube Videos              │
    │   with Transcription, Summarization, and      │
    │             Audio Processing                  │
    │                                               │
    │     Type 'help' to see available commands     │
    │                                               │
    ╰───────────────────────────────────────────────╯
    """
    prompt = 'YTInsight> '
    
    def __init__(self):
        """Initialize the CLI interface and components."""
        super().__init__()
        
        # Initialize components
        self.storage_manager = StorageManager()
        self.youtube_processor = YouTubeProcessor(self.storage_manager)
        self.transcriber = Transcriber(self.storage_manager, model_name="base")
        self.summarizer = Summarizer(self.storage_manager)
        self.embedder = Embedder(self.storage_manager)
        self.tts_generator = TTSGenerator(self.storage_manager)
        
        # Current video state
        self.current_video_id = None
        self.current_video_metadata = None
        
        # Check dependencies on startup
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        print("Checking dependencies...")
        deps = check_dependencies()
        
        missing = [dep for dep, installed in deps.items() if not installed]
        if missing:
            print("\nWarning: Some dependencies are missing:")
            for dep in missing:
                print(f"  - {dep}")
            print("\nSome features may not be available.")
            print("Install missing dependencies with: pip install -r requirements.txt")
        print("Dependency check complete.\n")
    
    def do_process(self, arg: str) -> None:
        """
        Process a YouTube video URL.
        
        Usage: process <youtube_url>
        """
        url = arg.strip()
        
        if not url:
            print("Please provide a YouTube URL.")
            print("Usage: process <youtube_url>")
            return
        
        if not validate_youtube_url(url):
            print("Invalid YouTube URL.")
            return
        
        print(f"Processing YouTube URL: {url}")
        print("Downloading video and extracting audio...")
        
        # Process the video
        success, video_id, metadata = self.youtube_processor.process_video(url)
        
        if not success or not video_id:
            print("Failed to process video.")
            return
        
        # Update current video state
        self.current_video_id = video_id
        self.current_video_metadata = metadata
        
        print(f"Video processed successfully: {metadata.get('title')}")
        
        # Display video information
        self._display_video_info()
    
    def do_transcribe(self, arg: str) -> None:
        """
        Transcribe the current video.
        
        Usage: transcribe
        """
        if not self.current_video_id:
            print("No video is currently loaded. Use 'process <youtube_url>' first.")
            return
        
        print("Transcribing video...")
        start_time = time.time()
        
        # Transcribe the video
        success, transcript = self.transcriber.transcribe(self.current_video_id)
        
        if not success or not transcript:
            print("Failed to transcribe video.")
            return
        
        elapsed_time = time.time() - start_time
        
        print(f"Transcription successful! (Time: {elapsed_time:.2f} seconds)")
        print(f"Transcript length: {len(transcript)} characters")
        
        # Display first few lines of transcript
        lines = transcript.split('\n')
        preview_lines = min(10, len(lines))
        
        print("\nTranscript preview:")
        print("=" * 40)
        for i in range(preview_lines):
            print(lines[i])
        
        if len(lines) > preview_lines:
            print("...")
        
        print("=" * 40)
        print("Use 'show transcript' to see the full transcript.")
    
    def do_summarize(self, arg: str) -> None:
        """
        Summarize the current video's transcript.
        
        Usage: summarize
        """
        if not self.current_video_id:
            print("No video is currently loaded. Use 'process <youtube_url>' first.")
            return
        
        transcript_path = self.storage_manager.get_transcript_path(self.current_video_id)
        if not os.path.exists(transcript_path):
            print("No transcript found. Use 'transcribe' first.")
            return
        
        print("Generating summary...")
        start_time = time.time()
        
        # Generate summary
        success, summary = self.summarizer.summarize(self.current_video_id)
        
        if not success or not summary:
            print("Failed to generate summary.")
            return
        
        elapsed_time = time.time() - start_time
        
        print(f"Summary generated successfully! (Time: {elapsed_time:.2f} seconds)")
        
        # Display summary
        print("\nSummary:")
        print("=" * 40)
        print(summary)
        print("=" * 40)
    
    def do_embed(self, arg: str) -> None:
        """
        Generate embeddings for the current video's transcript.
        
        Usage: embed
        """
        if not self.current_video_id:
            print("No video is currently loaded. Use 'process <youtube_url>' first.")
            return
        
        transcript_path = self.storage_manager.get_transcript_path(self.current_video_id)
        if not os.path.exists(transcript_path):
            print("No transcript found. Use 'transcribe' first.")
            return
        
        print("Generating embeddings...")
        start_time = time.time()
        
        # Generate embeddings
        success, embeddings_path = self.embedder.generate_embeddings(self.current_video_id)
        
        if not success:
            print("Failed to generate embeddings.")
            return
        
        elapsed_time = time.time() - start_time
        
        print(f"Embeddings generated successfully! (Time: {elapsed_time:.2f} seconds)")
        print(f"Embeddings stored in: {embeddings_path}")
    
    def do_tts(self, arg: str) -> None:
        """
        Generate text-to-speech audio for the current video's summary.
        
        Usage: tts
        """
        if not self.current_video_id:
            print("No video is currently loaded. Use 'process <youtube_url>' first.")
            return
        
        summary_path = self.storage_manager.get_summary_path(self.current_video_id)
        if not os.path.exists(summary_path):
            print("No summary found. Use 'summarize' first.")
            return
        
        print("Generating audio...")
        start_time = time.time()
        
        # Generate TTS
        success, audio_path = self.tts_generator.generate_audio(self.current_video_id)
        
        if not success:
            print("Failed to generate audio.")
            return
        
        elapsed_time = time.time() - start_time
        
        print(f"Audio generated successfully! (Time: {elapsed_time:.2f} seconds)")
        print(f"Audio file: {audio_path}")
        
        if os.path.exists(audio_path):
            file_size = get_file_size(audio_path)
            print(f"File size: {file_size}")
            print("Use your media player to play the audio file.")
    
    def do_show(self, arg: str) -> None:
        """
        Show information about the current video.
        
        Usage: show [transcript|summary|info]
        """
        if not self.current_video_id:
            print("No video is currently loaded. Use 'process <youtube_url>' first.")
            return
        
        arg = arg.strip().lower()
        
        if arg == "transcript":
            # Show transcript
            transcript_path = self.storage_manager.get_transcript_path(self.current_video_id)
            if not os.path.exists(transcript_path):
                print("No transcript found. Use 'transcribe' first.")
                return
            
            transcript = self.storage_manager.read_file(transcript_path)
            if transcript:
                print("\nFull Transcript:")
                print("=" * 40)
                print(transcript)
                print("=" * 40)
            else:
                print("Failed to read transcript.")
        
        elif arg == "summary":
            # Show summary
            summary_path = self.storage_manager.get_summary_path(self.current_video_id)
            if not os.path.exists(summary_path):
                print("No summary found. Use 'summarize' first.")
                return
            
            summary = self.storage_manager.read_file(summary_path)
            if summary:
                print("\nSummary:")
                print("=" * 40)
                print(summary)
                print("=" * 40)
            else:
                print("Failed to read summary.")
        
        elif arg == "info" or not arg:
            # Show video information
            self._display_video_info()
            
        else:
            print(f"Unknown option: {arg}")
            print("Usage: show [transcript|summary|info]")
    
    def _display_video_info(self) -> None:
        """Display information about the current video."""
        if not self.current_video_id or not self.current_video_metadata:
            print("No video information available.")
            return
        
        metadata = self.current_video_metadata
        
        print("\nVideo Information:")
        print("=" * 40)
        print(f"Title: {metadata.get('title', 'Unknown')}")
        print(f"Author: {metadata.get('author', 'Unknown')}")
        print(f"Duration: {format_time(metadata.get('length_seconds', 0))}")
        print(f"Views: {format_number(metadata.get('views', 0))}")
        print(f"Published: {metadata.get('publish_date', 'Unknown')}")
        print(f"URL: {metadata.get('url', 'Unknown')}")
        print(f"Video ID: {metadata.get('video_id', 'Unknown')}")
        print("=" * 40)
        
        # Check what's available
        print("\nAvailable data:")
        
        audio_path = self.storage_manager.get_audio_path(self.current_video_id)
        if os.path.exists(audio_path):
            print(f"✓ Audio file ({get_file_size(audio_path)})")
        else:
            print("✗ Audio file (not extracted)")
        
        transcript_path = self.storage_manager.get_transcript_path(self.current_video_id)
        if os.path.exists(transcript_path):
            print(f"✓ Transcript ({get_file_size(transcript_path)})")
        else:
            print("✗ Transcript (not generated)")
        
        summary_path = self.storage_manager.get_summary_path(self.current_video_id)
        if os.path.exists(summary_path):
            print(f"✓ Summary ({get_file_size(summary_path)})")
        else:
            print("✗ Summary (not generated)")
        
        embeddings_path = self.storage_manager.get_embeddings_path(self.current_video_id)
        if os.path.exists(embeddings_path):
            print(f"✓ Embeddings (directory)")
        else:
            print("✗ Embeddings (not generated)")
        
        tts_path = self.storage_manager.get_tts_path(self.current_video_id)
        if os.path.exists(tts_path):
            print(f"✓ TTS Audio ({get_file_size(tts_path)})")
        else:
            print("✗ TTS Audio (not generated)")
    
    def do_clear(self, arg: str) -> None:
        """
        Clear the screen.
        
        Usage: clear
        """
        clear_screen()
        print(self.intro)
    
    def do_exit(self, arg: str) -> bool:
        """
        Exit the application.
        
        Usage: exit
        """
        print("Exiting YouTube Insight ChatBot. Goodbye!")
        return True
    
    def do_quit(self, arg: str) -> bool:
        """
        Exit the application.
        
        Usage: quit
        """
        return self.do_exit(arg)
    
    def do_cleanup(self, arg: str) -> None:
        """
        Clean up files for the current video.
        
        Usage: cleanup
        """
        if not self.current_video_id:
            print("No video is currently loaded. Use 'process <youtube_url>' first.")
            return
        
        confirm = input(f"Are you sure you want to delete all files for video {self.current_video_id}? (y/n): ")
        if confirm.lower() != 'y':
            print("Cleanup cancelled.")
            return
        
        print(f"Cleaning up files for video {self.current_video_id}...")
        success = self.storage_manager.cleanup(self.current_video_id)
        
        if success:
            print("Cleanup successful.")
            self.current_video_id = None
            self.current_video_metadata = None
        else:
            print("Cleanup failed.")
    
    def do_help(self, arg: str) -> None:
        """
        Show help for commands.
        
        Usage: help [command]
        """
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            # Show general help
            print("\nYouTube Insight ChatBot - Available Commands:")
            print("=" * 40)
            print("process <url>     - Process a YouTube video URL")
            print("transcribe        - Transcribe the current video")
            print("summarize         - Summarize the video transcript")
            print("embed             - Generate embeddings for the transcript")
            print("tts               - Generate text-to-speech for the summary")
            print("show <option>     - Show transcript, summary, or video info")
            print("cleanup           - Delete all files for the current video")
            print("clear             - Clear the screen")
            print("exit/quit         - Exit the application")
            print("help [command]    - Show help for a specific command")
            print("=" * 40)
            print("Workflow: process URL → transcribe → summarize → embed → tts")


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(description='YouTube Insight ChatBot')
    parser.add_argument('--url', type=str, help='YouTube URL to process on startup')
    
    args = parser.parse_args()
    
    cli = YTInsightCLI()
    
    # If URL provided as argument, process it
    if args.url:
        cli.do_process(args.url)
    
    # Start the CLI
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting YouTube Insight ChatBot. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()