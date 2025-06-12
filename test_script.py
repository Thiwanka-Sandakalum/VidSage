#!/usr/bin/env python3
"""Test script for YouTube Insight ChatBot"""

import os
import sys
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yt_insight_chatbot.core.storage_manager import StorageManager
from yt_insight_chatbot.core.youtube_processor import YouTubeProcessor
from yt_insight_chatbot.core.transcriber import Transcriber
from yt_insight_chatbot.core.summarizer import Summarizer
from yt_insight_chatbot.core.embedder import Embedder
from yt_insight_chatbot.core.tts_generator import TTSGenerator
from yt_insight_chatbot.utils.helpers import check_dependencies

def test_end_to_end(youtube_url):
    """Run an end-to-end test with a YouTube URL."""
    
    print("\n======== TESTING YOUTUBE INSIGHT CHATBOT ========\n")
    
    # Step 1: Check dependencies
    print("Step 1: Checking dependencies...")
    deps = check_dependencies()
    missing = [dep for dep, installed in deps.items() if not installed]
    
    if missing:
        print("\nWarning: Some dependencies are missing:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nSome features may not be available.")
    
    # Step 2: Initialize components
    print("\nStep 2: Initializing components...")
    storage_manager = StorageManager()
    youtube_processor = YouTubeProcessor(storage_manager)
    transcriber = Transcriber(storage_manager, model_name="base")
    summarizer = Summarizer(storage_manager)
    embedder = Embedder(storage_manager)
    tts_generator = TTSGenerator(storage_manager)
    
    # Step 3: Process YouTube URL
    print(f"\nStep 3: Processing YouTube URL: {youtube_url}")
    success, video_id, metadata = youtube_processor.process_video(youtube_url)
    
    if not success or not video_id:
        print("Failed to process video.")
        return
    
    print(f"Video processed successfully!")
    print(f"Title: {metadata.get('title', 'Unknown')}")
    print(f"Author: {metadata.get('author', 'Unknown')}")
    print(f"Duration: {metadata.get('length_seconds', 0)} seconds")
    
    # Step 4: Transcribe video
    print("\nStep 4: Transcribing video...")
    start_time = time.time()
    success, transcript = transcriber.transcribe(video_id)
    elapsed_time = time.time() - start_time
    
    if not success or not transcript:
        print("Failed to transcribe video.")
        return
    
    print(f"Transcription successful! (Time: {elapsed_time:.2f} seconds)")
    print(f"Transcript length: {len(transcript)} characters")
    print("\nTranscript preview:")
    print("=" * 40)
    print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
    print("=" * 40)
    
    # Step 5: Generate summary
    print("\nStep 5: Generating summary...")
    start_time = time.time()
    success, summary = summarizer.summarize(video_id)
    elapsed_time = time.time() - start_time
    
    if not success or not summary:
        print("Failed to generate summary.")
    else:
        print(f"Summary generation successful! (Time: {elapsed_time:.2f} seconds)")
        print("\nSummary:")
        print("=" * 40)
        print(summary)
        print("=" * 40)
    
    # Step 6: Generate embeddings (optional)
    if 'chromadb' in deps and deps['chromadb'] and 'sentence_transformers' in deps and deps['sentence_transformers']:
        print("\nStep 6: Generating embeddings...")
        start_time = time.time()
        success, embeddings_path = embedder.generate_embeddings(video_id)
        elapsed_time = time.time() - start_time
        
        if not success:
            print("Failed to generate embeddings.")
        else:
            print(f"Embeddings generation successful! (Time: {elapsed_time:.2f} seconds)")
            print(f"Embeddings stored in: {embeddings_path}")
    else:
        print("\nStep 6: Skipping embeddings generation (dependencies missing)")
    
    # Step 7: Generate TTS (optional)
    if 'pyttsx3' in deps and deps['pyttsx3']:
        print("\nStep 7: Generating TTS audio...")
        start_time = time.time()
        success, audio_path = tts_generator.generate_audio(video_id)
        elapsed_time = time.time() - start_time
        
        if not success:
            print("Failed to generate TTS audio.")
        else:
            print(f"TTS generation successful! (Time: {elapsed_time:.2f} seconds)")
            print(f"Audio file: {audio_path}")
    else:
        print("\nStep 7: Skipping TTS generation (dependencies missing)")
    
    print("\n======== TEST COMPLETED SUCCESSFULLY! ========\n")
    print(f"All files are stored in: {storage_manager.base_dir}")
    print("You can now use the CLI tool to interact with this video.")
    
    return video_id

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_script.py <youtube_url>")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    test_end_to_end(youtube_url)
