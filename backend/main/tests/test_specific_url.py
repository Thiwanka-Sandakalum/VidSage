"""
Test script for fetching transcript from a specific YouTube URL.
URL: https://youtu.be/Rni7Fz7208c?si=Sj_zkiFy_BjOBna1
"""

import sys
from pathlib import Path

# Add the api directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from services.transcript_service import fetch_transcript, fetch_available_transcripts, TranscriptError
from src.core.helpers import extract_video_id

def test_specific_video():
    """Test fetching transcript from the specific YouTube video."""
    
    url = "https://youtu.be/Rni7Fz7208c?si=Sj_zkiFy_BjOBna1"
    
    print("=" * 80)
    print(f"Testing YouTube URL: {url}")
    print("=" * 80)
    
    try:
        # Step 1: Extract video ID
        print("\n[Step 1] Extracting video ID...")
        video_id = extract_video_id(url)
        print(f"✓ Video ID: {video_id}")
        
        # Step 2: Check available transcripts
        print("\n[Step 2] Checking available transcripts...")
        try:
            available = fetch_available_transcripts(video_id)
            print(f"✓ Found {len(available)} available transcript(s):")
            for transcript in available:
                print(f"  - Language: {transcript['language_code']}")
                print(f"    Generated: {transcript['is_generated']}")
                print(f"    Translatable: {transcript['is_translatable']}")
        except Exception as e:
            print(f"⚠ Could not list transcripts: {e}")
        
        # Step 3: Fetch the transcript
        print("\n[Step 3] Fetching transcript...")
        transcript_text = fetch_transcript(video_id)
        
        # Display results
        print(f"✓ Successfully fetched transcript!")
        print(f"\nTranscript Length: {len(transcript_text)} characters")
        print(f"Word Count: {len(transcript_text.split())} words")
        
        # Show first 500 characters
        print("\n" + "-" * 80)
        print("First 500 characters of transcript:")
        print("-" * 80)
        print(transcript_text[:500])
        if len(transcript_text) > 500:
            print("...")
        
        # Show last 200 characters
        if len(transcript_text) > 500:
            print("\n" + "-" * 80)
            print("Last 200 characters of transcript:")
            print("-" * 80)
            print("..." + transcript_text[-200:])
        
        print("\n" + "=" * 80)
        print("✓ TEST PASSED - Transcript fetched successfully!")
        print("=" * 80)
        
        return True
        
    except TranscriptError as e:
        print("\n" + "=" * 80)
        print(f"✗ TRANSCRIPT ERROR: {e}")
        print("=" * 80)
        return False
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ UNEXPECTED ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specific_video()
    sys.exit(0 if success else 1)
