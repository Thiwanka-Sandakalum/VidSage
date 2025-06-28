#!/usr/bin/env python3
"""
FastAPI Main Module for VidSage

This module provides REST API endpoints for all VidSage functionalities.
"""

import os
import sys
import logging
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends, Query, Form
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

# Core VidSage imports
from core.youtube_processor import YouTubeProcessor
from core.transcriber import Transcriber
from core.summarizer import Summarizer, SummaryType
from core.embedder import Embedder
from core.rag_system import RAGSystem
from core.rag_agents import QueryAnalyzer, ContentSummarizer, CitationManager
from core.tts_generator import TTSGenerator
from core.storage_manager import StorageManager
from utils.helpers import extract_video_id, is_youtube_url, load_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Initialize FastAPI app
app = FastAPI(
    title="VidSage API",
    description="🎥 **VidSage** - Comprehensive YouTube Video Analysis API\n\n"
                "Analyze YouTube videos with AI-powered transcription, summarization, "
                "and intelligent Q&A capabilities using RAG (Retrieval-Augmented Generation).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure according to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components - Initialize once for better performance
YOUTUBE_PROCESSOR = YouTubeProcessor(data_dir="data")
TRANSCRIBER = Transcriber(model_name="base")
STORAGE_MANAGER = StorageManager()

# API key management
def get_api_key():
    """Get API key from environment"""
    return load_api_key('GOOGLE_API_KEY')

# Pydantic models for request/response validation

class VideoProcessRequest(BaseModel):
    """Request model for video processing"""
    url: str = Field(..., description="YouTube video URL")
    download_audio: bool = Field(True, description="Whether to download audio")
    extract_subtitles: bool = Field(True, description="Whether to extract subtitles")
    
    @validator('url')
    def validate_youtube_url(cls, v):
        if not is_youtube_url(v):
            raise ValueError('Invalid YouTube URL')
        return v

class TranscribeRequest(BaseModel):
    """Request model for transcription"""
    video_id: str = Field(..., description="YouTube video ID")
    model_name: str = Field("base", description="Whisper model name (tiny, base, small, medium, large)")
    force_retranscribe: bool = Field(False, description="Force re-transcription even if transcript exists")

class SummarizeRequest(BaseModel):
    """Request model for summarization"""
    video_id: str = Field(..., description="YouTube video ID")
    summary_type: SummaryType = Field("default", description="Type of summary to generate")
    engine: str = Field("gemini", description="AI engine to use (gemini only supported)")
    force_regenerate: bool = Field(False, description="Force regeneration even if summary exists")

class EmbeddingRequest(BaseModel):
    """Request model for creating embeddings"""
    video_id: str = Field(..., description="YouTube video ID")
    for_rag: bool = Field(True, description="Create embeddings for RAG system")
    force_recreate: bool = Field(False, description="Force recreation of embeddings")

class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    video_id: str = Field(..., description="YouTube video ID")
    question: str = Field(..., description="Question to ask about the video")
    context_length: int = Field(3, description="Number of context chunks to retrieve")

class ChatRequest(BaseModel):
    """Request model for chat"""
    video_id: str = Field(..., description="YouTube video ID")
    message: str = Field(..., description="Chat message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for maintaining context")

class TTSRequest(BaseModel):
    """Request model for text-to-speech"""
    video_id: str = Field(..., description="YouTube video ID")
    text_type: str = Field("summary", description="Type of text to convert (summary, transcript)")
    summary_type: Optional[SummaryType] = Field("default", description="Summary type if text_type is summary")

# Response models

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

class VideoInfoResponse(BaseResponse):
    """Response model for video information"""
    video_info: Optional[Dict[str, Any]] = None

class TranscriptResponse(BaseResponse):
    """Response model for transcript"""
    transcript: Optional[Dict[str, Any]] = None
    segments: Optional[List[Dict[str, Any]]] = None

class SummaryResponse(BaseResponse):
    """Response model for summary"""
    summary: Optional[str] = None
    summary_type: Optional[str] = None

class QuestionResponse(BaseResponse):
    """Response model for questions"""
    answer: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None

class ChatResponse(BaseResponse):
    """Response model for chat"""
    response: Optional[str] = None
    conversation_id: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

# In-memory storage for active sessions (use Redis in production)
active_sessions: Dict[str, Dict[str, Any]] = {}
chat_conversations: Dict[str, List[Dict[str, Any]]] = {}

# Helper functions

def get_or_create_components(api_key: str = None) -> Dict[str, Any]:
    """Get or create AI components with API key"""
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    return {
        'summarizer': Summarizer(api_key=api_key),
        'rag_system': RAGSystem(api_key=api_key),
        'tts_generator': TTSGenerator(),
        'api_key': api_key
    }

def validate_video_exists(video_id: str) -> bool:
    """Validate if video data exists"""
    return STORAGE_MANAGER.video_exists(video_id)

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    ## Welcome to VidSage API 🎥
    
    A comprehensive YouTube video analysis API with AI-powered features.
    
    **Key Features:**
    - Video processing and metadata extraction
    - Audio transcription using OpenAI Whisper
    - AI-powered summarization with multiple formats
    - RAG-based question answering
    - Interactive chat about video content
    - Text-to-speech conversion
    """
    return {
        "message": "Welcome to VidSage API 🎥",
        "description": "AI-powered YouTube video analysis platform",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """
    ## Health Check Endpoint
    
    Returns the health status of the API and its components.
    """
    try:
        # Test core components
        api_key = get_api_key()
        has_api_key = bool(api_key)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "components": {
                "youtube_processor": "active",
                "transcriber": "active", 
                "storage_manager": "active",
                "api_key_configured": has_api_key
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now()
            }
        )

@app.post("/videos/process", response_model=VideoInfoResponse)
async def process_video(request: VideoProcessRequest, background_tasks: BackgroundTasks):
    """
    ## Process YouTube Video 🎬
    
    **Process a YouTube video and extract metadata, audio, and subtitles.**
    
    This endpoint:
    1. Extracts video information and metadata
    2. Downloads audio if requested
    3. Extracts subtitles if available
    4. Stores all data for further processing
    
    **Parameters:**
    - `url`: YouTube video URL
    - `download_audio`: Whether to download audio (default: true)
    - `extract_subtitles`: Whether to extract subtitles (default: true)
    
    **Returns:**
    - Video metadata including title, duration, description
    - Processing status and file locations
    
    **Example:**
    ```json
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "download_audio": true,
        "extract_subtitles": true
    }
    ```
    """
    try:
        video_id = extract_video_id(request.url)
        
        # Get video info
        video_info = YOUTUBE_PROCESSOR.get_video_info(request.url)
        
        # Store video info
        STORAGE_MANAGER.save_video_info(video_id, video_info)
        
        # Download audio in background if requested
        if request.download_audio:
            background_tasks.add_task(
                YOUTUBE_PROCESSOR.download_audio,
                request.url
            )
        
        # Extract subtitles in background if requested
        if request.extract_subtitles:
            background_tasks.add_task(
                YOUTUBE_PROCESSOR.extract_subtitles,
                request.url
            )
        
        return VideoInfoResponse(
            success=True,
            message=f"Video processed successfully. ID: {video_id}",
            video_info=video_info
        )
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/videos/{video_id}/info", response_model=VideoInfoResponse)
async def get_video_info(video_id: str):
    """
    ## Get Video Information 📋
    
    **Retrieve stored information about a processed video.**
    
    Returns comprehensive metadata about the video including:
    - Title, description, duration
    - Channel information
    - View count, publish date
    - Available processing status
    
    **Parameters:**
    - `video_id`: YouTube video ID
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Video info retrieved",
        "video_info": {
            "title": "Video Title",
            "duration": 180,
            "description": "Video description...",
            "channel": "Channel Name"
        }
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_info = STORAGE_MANAGER.load_video_info(video_id)
        
        return VideoInfoResponse(
            success=True,
            message="Video information retrieved successfully",
            video_info=video_info
        )
        
    except Exception as e:
        logger.error(f"Error retrieving video info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/videos/{video_id}/transcribe", response_model=TranscriptResponse)
async def transcribe_video(video_id: str, request: TranscribeRequest):
    """
    ## Transcribe Video Audio 🎙️
    
    **Convert video audio to text using OpenAI Whisper.**
    
    This endpoint:
    1. Checks for existing subtitles first
    2. Uses Whisper for transcription if no subtitles available
    3. Returns timestamped transcript segments
    4. Stores transcript for future use
    
    **Models Available:**
    - `tiny`: Fastest, least accurate
    - `base`: Good balance (default)
    - `small`: Better accuracy
    - `medium`: High accuracy
    - `large`: Best accuracy, slowest
    
    **Parameters:**
    - `model_name`: Whisper model to use
    - `force_retranscribe`: Force new transcription
    
    **Example Response:**
    ```json
    {
        "success": true,
        "transcript": {
            "text": "Full transcript text...",
            "language": "en"
        },
        "segments": [
            {
                "text": "Hello world",
                "start": 0.0,
                "end": 2.5
            }
        ]
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Check if transcript already exists
        if not request.force_retranscribe and STORAGE_MANAGER.has_transcript(video_id):
            transcript_data = STORAGE_MANAGER.load_transcript(video_id)
            return TranscriptResponse(
                success=True,
                message="Transcript already exists",
                transcript=transcript_data.get('transcript'),
                segments=transcript_data.get('segments')
            )
        
        # Initialize transcriber with specified model
        transcriber = Transcriber(model_name=request.model_name)
        
        # Get audio file path
        audio_path = STORAGE_MANAGER.get_audio_path(video_id)
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found. Process video first.")
        
        # Transcribe
        result = transcriber.transcribe_file(str(audio_path))
        
        # Save transcript
        STORAGE_MANAGER.save_transcript(video_id, result)
        
        return TranscriptResponse(
            success=True,
            message="Transcription completed successfully",
            transcript=result,
            segments=result.get('segments', [])
        )
        
    except Exception as e:
        logger.error(f"Error transcribing video: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/videos/{video_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(video_id: str):
    """
    ## Get Video Transcript 📝
    
    **Retrieve the stored transcript for a video.**
    
    Returns the full transcript with timestamps if available.
    
    **Example Response:**
    ```json
    {
        "success": true,
        "transcript": {
            "text": "Complete transcript...",
            "language": "en"
        },
        "segments": [...]
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        if not STORAGE_MANAGER.has_transcript(video_id):
            raise HTTPException(status_code=404, detail="Transcript not found. Transcribe video first.")
        
        transcript_data = STORAGE_MANAGER.load_transcript(video_id)
        
        return TranscriptResponse(
            success=True,
            message="Transcript retrieved successfully",
            transcript=transcript_data.get('transcript'),
            segments=transcript_data.get('segments')
        )
        
    except Exception as e:
        logger.error(f"Error retrieving transcript: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/videos/{video_id}/summarize", response_model=SummaryResponse)
async def summarize_video(video_id: str, request: SummarizeRequest):
    """
    ## Generate Video Summary 📊
    
    **Create AI-powered summaries of video content in multiple formats.**
    
    **Summary Types:**
    - `default`: Balanced summary
    - `concise`: Brief overview
    - `detailed`: Comprehensive analysis
    - `bullet`: Bullet-point format
    - `sections`: Organized by topics
    
    **Features:**
    - Uses Gemini AI for high-quality summaries
    - Maintains context and key insights
    - Customizable length and format
    
    **Example Request:**
    ```json
    {
        "video_id": "dQw4w9WgXcQ",
        "summary_type": "bullet",
        "engine": "gemini"
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        if not STORAGE_MANAGER.has_transcript(video_id):
            raise HTTPException(status_code=404, detail="Transcript not found. Transcribe video first.")
        
        # Check if summary already exists
        if not request.force_regenerate and STORAGE_MANAGER.has_summary(request.summary_type, video_id):
            summary = STORAGE_MANAGER.load_summary(request.summary_type, video_id)
            return SummaryResponse(
                success=True,
                message="Summary already exists",
                summary=summary,
                summary_type=request.summary_type
            )
        
        # Get components
        components = get_or_create_components()
        summarizer = components['summarizer']
        
        # Load transcript
        transcript_data = STORAGE_MANAGER.load_transcript(video_id)
        transcript_text = transcript_data.get('text', '')
        
        if not transcript_text:
            raise HTTPException(status_code=400, detail="Empty transcript")
        
        # Generate summary
        summary = summarizer.summarize(transcript_text, summary_type=request.summary_type)
        
        # Save summary
        STORAGE_MANAGER.save_summary(request.summary_type, video_id, summary)
        
        return SummaryResponse(
            success=True,
            message="Summary generated successfully",
            summary=summary,
            summary_type=request.summary_type
        )
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/videos/{video_id}/summary", response_model=SummaryResponse)
async def get_summary(video_id: str, summary_type: SummaryType = Query("default")):
    """
    ## Get Video Summary 📖
    
    **Retrieve stored summary for a video.**
    
    **Parameters:**
    - `summary_type`: Type of summary to retrieve (default, concise, detailed, bullet, sections)
    
    **Example Response:**
    ```json
    {
        "success": true,
        "summary": "This video discusses...",
        "summary_type": "default"
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        if not STORAGE_MANAGER.has_summary(summary_type, video_id):
            raise HTTPException(status_code=404, detail=f"Summary of type '{summary_type}' not found")
        
        summary = STORAGE_MANAGER.load_summary(summary_type, video_id)
        
        return SummaryResponse(
            success=True,
            message="Summary retrieved successfully",
            summary=summary,
            summary_type=summary_type
        )
        
    except Exception as e:
        logger.error(f"Error retrieving summary: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/videos/{video_id}/embeddings")
async def create_embeddings(video_id: str, request: EmbeddingRequest):
    """
    ## Create Vector Embeddings 🧠
    
    **Generate vector embeddings for the video transcript to enable RAG functionality.**
    
    This endpoint:
    1. Chunks the transcript into meaningful segments
    2. Creates vector embeddings using Google's embedding model
    3. Stores embeddings in vector database (Chroma)
    4. Prepares the video for question-answering
    
    **Use Cases:**
    - Enable semantic search through video content
    - Prepare for RAG-based question answering
    - Find similar content segments
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Embeddings created successfully",
        "chunks_created": 45,
        "embedding_dimension": 768
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        if not STORAGE_MANAGER.has_transcript(video_id):
            raise HTTPException(status_code=404, detail="Transcript not found. Transcribe video first.")
        
        # Get components
        components = get_or_create_components()
        embedder = Embedder(api_key=components['api_key'])
        
        # Load transcript
        transcript_data = STORAGE_MANAGER.load_transcript(video_id)
        transcript_text = transcript_data.get('text', '')
        segments = transcript_data.get('segments', [])
        
        if not transcript_text:
            raise HTTPException(status_code=400, detail="Empty transcript")
        
        # Create embeddings
        if request.for_rag:
            result = embedder.create_embeddings_for_rag(
                transcript_text, 
                video_id,
                segments=segments
            )
        else:
            result = embedder.create_embeddings(transcript_text, video_id)
        
        return {
            "success": True,
            "message": "Embeddings created successfully",
            "chunks_created": result.get('chunks_created', 0),
            "embedding_dimension": result.get('embedding_dimension', 0)
        }
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/videos/{video_id}/setup-rag")
async def setup_rag(video_id: str):
    """
    ## Setup RAG System 🤖
    
    **Initialize the Retrieval-Augmented Generation system for intelligent Q&A.**
    
    This endpoint:
    1. Loads existing embeddings or creates them if needed
    2. Initializes the RAG retrieval system
    3. Prepares question-answering capabilities
    4. Sets up context-aware response generation
    
    **Required Prerequisites:**
    - Video must be processed
    - Transcript must exist
    - Embeddings should be created (will create if missing)
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "RAG system initialized",
        "status": "ready_for_questions"
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        if not STORAGE_MANAGER.has_transcript(video_id):
            raise HTTPException(status_code=404, detail="Transcript not found. Transcribe video first.")
        
        # Get components
        components = get_or_create_components()
        rag_system = components['rag_system']
        
        # Load transcript
        transcript_data = STORAGE_MANAGER.load_transcript(video_id)
        transcript_text = transcript_data.get('text', '')
        segments = transcript_data.get('segments', [])
        
        if not transcript_text:
            raise HTTPException(status_code=400, detail="Empty transcript")
        
        # Setup RAG system
        rag_system.setup(transcript_text, video_id, segments=segments)
        
        # Store RAG system in active sessions
        active_sessions[video_id] = {
            'rag_system': rag_system,
            'components': components,
            'created_at': datetime.now()
        }
        
        return {
            "success": True,
            "message": "RAG system initialized successfully",
            "status": "ready_for_questions",
            "video_id": video_id
        }
        
    except Exception as e:
        logger.error(f"Error setting up RAG: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/videos/{video_id}/ask", response_model=QuestionResponse)
async def ask_question(video_id: str, request: QuestionRequest):
    """
    ## Ask Question About Video 🤔
    
    **Ask intelligent questions about video content using RAG technology.**
    
    **Features:**
    - Context-aware answers based on video transcript
    - Source citations with timestamps
    - Confidence scoring
    - Handles complex, nuanced questions
    
    **How it works:**
    1. Analyzes your question for intent and context
    2. Retrieves relevant video segments
    3. Generates accurate answer using AI
    4. Provides source timestamps for verification
    
    **Example Questions:**
    - "What are the main points discussed?"
    - "How does the speaker explain X concept?"
    - "What examples are given for Y?"
    - "What is the conclusion of the video?"
    
    **Example Request:**
    ```json
    {
        "video_id": "dQw4w9WgXcQ",
        "question": "What are the key takeaways from this video?",
        "context_length": 3
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get or setup RAG system
        if video_id not in active_sessions:
            # Auto-setup RAG if not exists
            await setup_rag(video_id)
        
        session = active_sessions.get(video_id)
        if not session:
            raise HTTPException(status_code=400, detail="RAG system not initialized")
        
        rag_system = session['rag_system']
        
        # Ask question
        result = rag_system.ask_question(
            request.question,
            k=request.context_length
        )
        
        return QuestionResponse(
            success=True,
            message="Question answered successfully",
            answer=result.get('answer'),
            sources=result.get('sources', []),
            confidence=result.get('confidence')
        )
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/videos/{video_id}/chat", response_model=ChatResponse)
async def chat_with_video(video_id: str, request: ChatRequest):
    """
    ## Interactive Chat About Video 💬
    
    **Have a conversation about video content with context retention.**
    
    **Features:**
    - Maintains conversation context across messages
    - References previous questions and answers
    - Contextual follow-up questions
    - Source citations for all responses
    
    **Conversation Flow:**
    1. Start with any question about the video
    2. Follow up with related questions
    3. System remembers conversation history
    4. Get detailed, contextual responses
    
    **Example Conversation:**
    ```
    You: "What is this video about?"
    AI: "This video discusses..."
    
    You: "Can you elaborate on that first point?"
    AI: "Certainly! Referring to the first point I mentioned..."
    ```
    
    **Parameters:**
    - `message`: Your chat message or question
    - `conversation_id`: Optional ID to maintain conversation context
    
    **Example Request:**
    ```json
    {
        "video_id": "dQw4w9WgXcQ",
        "message": "What are the main topics covered?",
        "conversation_id": "conv_123"
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get or setup RAG system
        if video_id not in active_sessions:
            await setup_rag(video_id)
        
        session = active_sessions.get(video_id)
        if not session:
            raise HTTPException(status_code=400, detail="RAG system not initialized")
        
        rag_system = session['rag_system']
        
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        if conversation_id not in chat_conversations:
            chat_conversations[conversation_id] = []
        
        conversation_history = chat_conversations[conversation_id]
        
        # Get response with conversation context
        result = rag_system.chat(
            request.message,
            conversation_history=conversation_history
        )
        
        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now()
        })
        conversation_history.append({
            "role": "assistant", 
            "content": result.get('response'),
            "sources": result.get('sources', []),
            "timestamp": datetime.now()
        })
        
        return ChatResponse(
            success=True,
            message="Chat response generated successfully",
            response=result.get('response'),
            conversation_id=conversation_id,
            sources=result.get('sources', [])
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/videos/{video_id}/tts")
async def text_to_speech(video_id: str, request: TTSRequest):
    """
    ## Text-to-Speech Conversion 🔊
    
    **Convert summaries or transcripts to audio using text-to-speech.**
    
    **Features:**
    - High-quality speech synthesis
    - Multiple text source options
    - Downloadable audio files
    - Fast processing
    
    **Text Sources:**
    - `summary`: Convert summary to speech (default)
    - `transcript`: Convert full transcript to speech
    
    **Returns:**
    - Audio file URL for download
    - Audio metadata (duration, format, size)
    
    **Example Request:**
    ```json
    {
        "video_id": "dQw4w9WgXcQ",
        "text_type": "summary",
        "summary_type": "concise"
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get text content based on type
        if request.text_type == "summary":
            if not STORAGE_MANAGER.has_summary(request.summary_type, video_id):
                raise HTTPException(status_code=404, detail=f"Summary of type '{request.summary_type}' not found")
            text_content = STORAGE_MANAGER.load_summary(request.summary_type, video_id)
        elif request.text_type == "transcript":
            if not STORAGE_MANAGER.has_transcript(video_id):
                raise HTTPException(status_code=404, detail="Transcript not found")
            transcript_data = STORAGE_MANAGER.load_transcript(video_id)
            text_content = transcript_data.get('text', '')
        else:
            raise HTTPException(status_code=400, detail="Invalid text_type. Use 'summary' or 'transcript'")
        
        if not text_content:
            raise HTTPException(status_code=400, detail="No content found to convert")
        
        # Generate TTS
        tts_generator = TTSGenerator()
        audio_path = tts_generator.generate_speech(text_content, video_id, request.text_type)
        
        # Return file for download
        return FileResponse(
            path=audio_path,
            media_type='audio/mpeg',
            filename=f"{video_id}_{request.text_type}_tts.mp3",
            headers={"Content-Disposition": f"attachment; filename={video_id}_{request.text_type}_tts.mp3"}
        )
        
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/videos/{video_id}/status")
async def get_video_status(video_id: str):
    """
    ## Get Video Processing Status 📊
    
    **Check the processing status of a video and available features.**
    
    **Status Information:**
    - Video processing status
    - Available transcripts
    - Generated summaries
    - RAG system status
    - Embeddings status
    
    **Example Response:**
    ```json
    {
        "video_id": "dQw4w9WgXcQ",
        "video_exists": true,
        "has_audio": true,
        "has_transcript": true,
        "summaries": ["default", "concise"],
        "rag_ready": true,
        "last_updated": "2024-01-15T10:30:00"
    }
    ```
    """
    try:
        status = {
            "video_id": video_id,
            "video_exists": validate_video_exists(video_id),
            "has_audio": False,
            "has_transcript": False,
            "has_embeddings": False,
            "summaries": [],
            "rag_ready": video_id in active_sessions,
            "last_updated": None
        }
        
        if status["video_exists"]:
            # Check audio
            audio_path = STORAGE_MANAGER.get_audio_path(video_id)
            status["has_audio"] = audio_path.exists()
            
            # Check transcript
            status["has_transcript"] = STORAGE_MANAGER.has_transcript(video_id)
            
            # Check summaries
            summary_types = ["default", "concise", "detailed", "bullet", "sections"]
            status["summaries"] = [
                stype for stype in summary_types 
                if STORAGE_MANAGER.has_summary(stype, video_id)
            ]
            
            # Get last updated timestamp
            video_info = STORAGE_MANAGER.load_video_info(video_id)
            if video_info:
                status["last_updated"] = video_info.get("processed_at")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting video status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/videos/{video_id}")
async def delete_video_data(video_id: str):
    """
    ## Delete Video Data 🗑️
    
    **Clean up all stored data for a video.**
    
    **Deletes:**
    - Video metadata
    - Audio files  
    - Transcripts
    - Summaries
    - Embeddings
    - Vector store data
    - Active RAG sessions
    
    **Warning:** This action cannot be undone!
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "All data for video dQw4w9WgXcQ deleted successfully",
        "deleted_files": 8
    }
    ```
    """
    try:
        if not validate_video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Clean up storage
        deleted_files = STORAGE_MANAGER.cleanup_video_data(video_id)
        
        # Remove from active sessions
        if video_id in active_sessions:
            del active_sessions[video_id]
        
        # Clean up chat conversations for this video
        conversations_to_remove = [
            conv_id for conv_id, history in chat_conversations.items()
            if any(msg.get('video_id') == video_id for msg in history)
        ]
        
        for conv_id in conversations_to_remove:
            del chat_conversations[conv_id]
        
        return {
            "success": True,
            "message": f"All data for video {video_id} deleted successfully",
            "deleted_files": deleted_files
        }
        
    except Exception as e:
        logger.error(f"Error deleting video data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/videos")
async def list_processed_videos():
    """
    ## List Processed Videos 📋
    
    **Get a list of all processed videos and their status.**
    
    **Returns:**
    - List of video IDs
    - Basic metadata for each video
    - Processing status summary
    
    **Example Response:**
    ```json
    {
        "videos": [
            {
                "video_id": "dQw4w9WgXcQ",
                "title": "Video Title",
                "duration": 180,
                "processed_at": "2024-01-15T10:30:00",
                "features": ["transcript", "summary", "rag"]
            }
        ],
        "total_count": 1
    }
    ```
    """
    try:
        videos = STORAGE_MANAGER.list_processed_videos()
        
        video_list = []
        for video_id in videos:
            try:
                video_info = STORAGE_MANAGER.load_video_info(video_id)
                features = []
                
                if STORAGE_MANAGER.has_transcript(video_id):
                    features.append("transcript")
                
                summary_types = ["default", "concise", "detailed", "bullet", "sections"]
                if any(STORAGE_MANAGER.has_summary(stype, video_id) for stype in summary_types):
                    features.append("summary")
                
                if video_id in active_sessions:
                    features.append("rag")
                
                video_list.append({
                    "video_id": video_id,
                    "title": video_info.get("title", "Unknown"),
                    "duration": video_info.get("duration", 0),
                    "processed_at": video_info.get("processed_at"),
                    "features": features
                })
                
            except Exception as e:
                logger.warning(f"Error loading info for video {video_id}: {e}")
                continue
        
        return {
            "videos": video_list,
            "total_count": len(video_list)
        }
        
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
