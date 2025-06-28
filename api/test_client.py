#!/usr/bin/env python3
"""
VidSage API Test Client

Example client showing how to use all VidSage API endpoints.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class VidSageClient:
    """Simple client for VidSage API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def process_video(self, url: str, download_audio: bool = True, extract_subtitles: bool = True) -> Dict[str, Any]:
        """Process a YouTube video"""
        data = {
            "url": url,
            "download_audio": download_audio,
            "extract_subtitles": extract_subtitles
        }
        response = self.session.post(f"{self.base_url}/videos/process", json=data)
        return response.json()
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get video information"""
        response = self.session.get(f"{self.base_url}/videos/{video_id}/info")
        return response.json()
    
    def transcribe_video(self, video_id: str, model_name: str = "base", force_retranscribe: bool = False) -> Dict[str, Any]:
        """Transcribe video audio"""
        data = {
            "video_id": video_id,
            "model_name": model_name,
            "force_retranscribe": force_retranscribe
        }
        response = self.session.post(f"{self.base_url}/videos/{video_id}/transcribe", json=data)
        return response.json()
    
    def get_transcript(self, video_id: str) -> Dict[str, Any]:
        """Get video transcript"""
        response = self.session.get(f"{self.base_url}/videos/{video_id}/transcript")
        return response.json()
    
    def summarize_video(self, video_id: str, summary_type: str = "default", force_regenerate: bool = False) -> Dict[str, Any]:
        """Generate video summary"""
        data = {
            "video_id": video_id,
            "summary_type": summary_type,
            "engine": "gemini",
            "force_regenerate": force_regenerate
        }
        response = self.session.post(f"{self.base_url}/videos/{video_id}/summarize", json=data)
        return response.json()
    
    def get_summary(self, video_id: str, summary_type: str = "default") -> Dict[str, Any]:
        """Get video summary"""
        response = self.session.get(f"{self.base_url}/videos/{video_id}/summary", params={"summary_type": summary_type})
        return response.json()
    
    def create_embeddings(self, video_id: str, for_rag: bool = True, force_recreate: bool = False) -> Dict[str, Any]:
        """Create vector embeddings"""
        data = {
            "video_id": video_id,
            "for_rag": for_rag,
            "force_recreate": force_recreate
        }
        response = self.session.post(f"{self.base_url}/videos/{video_id}/embeddings", json=data)
        return response.json()
    
    def setup_rag(self, video_id: str) -> Dict[str, Any]:
        """Setup RAG system"""
        response = self.session.post(f"{self.base_url}/videos/{video_id}/setup-rag")
        return response.json()
    
    def ask_question(self, video_id: str, question: str, context_length: int = 3) -> Dict[str, Any]:
        """Ask a question about the video"""
        data = {
            "video_id": video_id,
            "question": question,
            "context_length": context_length
        }
        response = self.session.post(f"{self.base_url}/videos/{video_id}/ask", json=data)
        return response.json()
    
    def chat(self, video_id: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Chat about the video"""
        data = {
            "video_id": video_id,
            "message": message
        }
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        response = self.session.post(f"{self.base_url}/videos/{video_id}/chat", json=data)
        return response.json()
    
    def text_to_speech(self, video_id: str, text_type: str = "summary", summary_type: str = "default") -> bytes:
        """Convert text to speech"""
        data = {
            "video_id": video_id,
            "text_type": text_type,
            "summary_type": summary_type
        }
        response = self.session.post(f"{self.base_url}/videos/{video_id}/tts", json=data)
        return response.content
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get video processing status"""
        response = self.session.get(f"{self.base_url}/videos/{video_id}/status")
        return response.json()
    
    def list_videos(self) -> Dict[str, Any]:
        """List all processed videos"""
        response = self.session.get(f"{self.base_url}/videos")
        return response.json()
    
    def delete_video(self, video_id: str) -> Dict[str, Any]:
        """Delete video data"""
        response = self.session.delete(f"{self.base_url}/videos/{video_id}")
        return response.json()

def main():
    """Example usage of VidSage API"""
    
    # Initialize client
    client = VidSageClient()
    
    # Test video URL (Rick Roll - short and well-known)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print("🔍 Testing VidSage API...")
        print("=" * 50)
        
        # 1. Health check
        print("1. Health Check...")
        health = client.health_check()
        print(f"   Status: {health.get('status')}")
        print()
        
        # 2. Process video
        print("2. Processing video...")
        result = client.process_video(test_url)
        if not result.get('success'):
            print(f"   Error: {result.get('message')}")
            return
        
        video_id = result['video_info']['id']
        print(f"   Video ID: {video_id}")
        print(f"   Title: {result['video_info']['title']}")
        print()
        
        # 3. Check status
        print("3. Checking video status...")
        status = client.get_video_status(video_id)
        print(f"   Has audio: {status.get('has_audio')}")
        print(f"   Has transcript: {status.get('has_transcript')}")
        print()
        
        # 4. Transcribe (if needed)
        if not status.get('has_transcript'):
            print("4. Transcribing video...")
            transcript_result = client.transcribe_video(video_id, model_name="tiny")  # Use tiny for speed
            if transcript_result.get('success'):
                print("   Transcription completed!")
            else:
                print(f"   Transcription failed: {transcript_result.get('message')}")
        else:
            print("4. Transcript already exists, skipping...")
        print()
        
        # 5. Get transcript
        print("5. Getting transcript...")
        transcript = client.get_transcript(video_id)
        if transcript.get('success'):
            text = transcript['transcript']['text']
            print(f"   Transcript length: {len(text)} characters")
            print(f"   Preview: {text[:100]}...")
        print()
        
        # 6. Generate summary
        print("6. Generating summary...")
        summary_result = client.summarize_video(video_id, summary_type="concise")
        if summary_result.get('success'):
            print("   Summary generated!")
            print(f"   Preview: {summary_result['summary'][:150]}...")
        else:
            print(f"   Summary failed: {summary_result.get('message')}")
        print()
        
        # 7. Setup RAG system
        print("7. Setting up RAG system...")
        rag_result = client.setup_rag(video_id)
        if rag_result.get('success'):
            print("   RAG system ready!")
        else:
            print(f"   RAG setup failed: {rag_result.get('message')}")
        print()
        
        # 8. Ask questions
        if rag_result.get('success'):
            print("8. Asking questions...")
            questions = [
                "What is this video about?",
                "What are the main points?",
                "How long is the video?"
            ]
            
            for i, question in enumerate(questions, 1):
                print(f"   Q{i}: {question}")
                answer_result = client.ask_question(video_id, question)
                if answer_result.get('success'):
                    answer = answer_result['answer']
                    print(f"   A{i}: {answer[:100]}...")
                else:
                    print(f"   A{i}: Error - {answer_result.get('message')}")
                print()
        
        # 9. Interactive chat example
        print("9. Testing chat functionality...")
        chat_result = client.chat(video_id, "Can you tell me more about this video?")
        if chat_result.get('success'):
            print(f"   Chat response: {chat_result['response'][:100]}...")
            conversation_id = chat_result['conversation_id']
            
            # Follow-up question
            followup = client.chat(video_id, "What makes it special?", conversation_id)
            if followup.get('success'):
                print(f"   Follow-up: {followup['response'][:100]}...")
        print()
        
        # 10. List all videos
        print("10. Listing processed videos...")
        videos = client.list_videos()
        print(f"    Total videos: {videos.get('total_count', 0)}")
        print()
        
        print("✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to VidSage API server")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main()
