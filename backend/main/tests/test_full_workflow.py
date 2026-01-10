"""
Integration test for processing the specific YouTube video through the full workflow.
URL: https://youtu.be/Rni7Fz7208c?si=Sj_zkiFy_BjOBna1
"""

import sys
from pathlib import Path

# Add the api directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from services.transcript_service import fetch_transcript, TranscriptError
from services.chunk_service import chunk_text, ChunkingError
from src.core.helpers import extract_video_id

def test_full_workflow():
    """Test the complete workflow: URL -> Video ID -> Transcript -> Chunks."""
    
    url = "https://youtu.be/Rni7Fz7208c?si=Sj_zkiFy_BjOBna1"
    
    print("=" * 80)
    print("FULL VIDEO PROCESSING WORKFLOW TEST")
    print("=" * 80)
    print(f"URL: {url}\n")
    
    try:
        # Step 1: Extract video ID
        print("[1/3] Extracting video ID...")
        video_id = extract_video_id(url)
        print(f"✓ Video ID: {video_id}\n")
        
        # Step 2: Fetch transcript
        print("[2/3] Fetching transcript...")
        transcript_text = fetch_transcript(video_id)
        print(f"✓ Transcript fetched successfully!")
        print(f"  - Length: {len(transcript_text):,} characters")
        print(f"  - Words: {len(transcript_text.split()):,}\n")
        
        # Step 3: Chunk the transcript
        print("[3/3] Chunking transcript...")
        chunks = chunk_text(
            text=transcript_text,
            chunk_size=500,
            chunk_overlap=100
        )
        print(f"✓ Chunking completed successfully!")
        print(f"  - Total chunks: {len(chunks)}")
        print(f"  - Chunk size: 500 characters")
        print(f"  - Overlap: 100 characters\n")
        
        # Display chunk statistics
        print("-" * 80)
        print("CHUNK STATISTICS")
        print("-" * 80)
        
        chunk_lengths = [len(chunk) for chunk in chunks]
        print(f"Average chunk length: {sum(chunk_lengths) / len(chunk_lengths):.1f} characters")
        print(f"Minimum chunk length: {min(chunk_lengths)} characters")
        print(f"Maximum chunk length: {max(chunk_lengths)} characters")
        
        # Show sample chunks
        print("\n" + "-" * 80)
        print("SAMPLE CHUNKS (first 3)")
        print("-" * 80)
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\nChunk #{i} ({len(chunk)} chars):")
            print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
        
        print("\n" + "-" * 80)
        print("SAMPLE CHUNKS (last 3)")
        print("-" * 80)
        for i, chunk in enumerate(chunks[-3:], len(chunks) - 2):
            print(f"\nChunk #{i} ({len(chunk)} chars):")
            print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
        
        # Summary
        print("\n" + "=" * 80)
        print("✓ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"Video ID: {video_id}")
        print(f"Transcript: {len(transcript_text):,} characters, {len(transcript_text.split()):,} words")
        print(f"Chunks: {len(chunks)} chunks created")
        print(f"Ready for embedding and storage!")
        print("=" * 80)
        
        return True
        
    except TranscriptError as e:
        print(f"\n✗ TRANSCRIPT ERROR: {e}")
        return False
        
    except ChunkingError as e:
        print(f"\n✗ CHUNKING ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)
