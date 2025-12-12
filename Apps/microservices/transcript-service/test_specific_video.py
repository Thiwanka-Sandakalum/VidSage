#!/usr/bin/env python3
"""Test transcript download for specific video."""

import sys
import os

# Add parent directory for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import extract_video_id
from worker import download_transcript_direct

def test_video_transcript(video_url):
    """Test transcript download for a specific video."""
    print(f"📹 Testing video: {video_url}")
    
    try:
        # Extract video ID
        video_id = extract_video_id(video_url)
        print(f"🆔 Extracted Video ID: {video_id}")
        print()
        
        # Test direct transcript download
        print("🔄 Testing transcript download...")
        result = download_transcript_direct(video_url, video_id)
        
        print("✅ Download successful!")
        print(f"📊 Video ID: {result['video_id']}")
        print(f"📝 Transcript length: {len(result['transcript'])} characters")
        print(f"📋 Metadata:")
        for key, value in result['metadata'].items():
            print(f"   {key}: {value}")
        print()
        
        # Show first part of transcript
        transcript = result['transcript']
        if len(transcript) > 300:
            print("📄 First 300 characters of transcript:")
            print(transcript[:300] + "...")
        else:
            print("📄 Complete transcript:")
            print(transcript)
            
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\nPossible reasons:")
        print("- Video has no transcript/captions available")
        print("- Video is private, unlisted, or unavailable") 
        print("- YouTube API rate limiting (429 error)")
        print("- Transcripts are disabled for this video")
        print("- Geographic restrictions")
        return False

if __name__ == "__main__":
    # Test the specific video
    video_url = "https://www.youtube.com/watch?v=Za7aG-ooGLQ"
    test_video_transcript(video_url)