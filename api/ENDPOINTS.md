# VidSage API Endpoints Reference 📚

This document provides detailed information about all available API endpoints in VidSage.

## Table of Contents

- [Authentication](#authentication)
- [Video Processing](#video-processing)
- [Transcription](#transcription)
- [Summarization](#summarization)
- [RAG & Q&A](#rag--qa)
- [Text-to-Speech](#text-to-speech)
- [System](#system)
- [Response Format](#response-format)
- [Error Codes](#error-codes)

## Authentication

Currently, the API uses Google API key authentication through environment variables. No additional authentication is required for endpoints.

**Required Environment Variable:**
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
```

## Video Processing

### POST /videos/process

Process a YouTube video and extract metadata.

**Request Body:**
```json
{
  "url": "string (required) - YouTube video URL",
  "download_audio": "boolean (optional, default: true) - Download audio",
  "extract_subtitles": "boolean (optional, default: true) - Extract subtitles"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Video processed successfully. ID: dQw4w9WgXcQ",
  "timestamp": "2024-01-15T10:30:00",
  "video_info": {
    "id": "dQw4w9WgXcQ",
    "title": "Video Title",
    "description": "Video description...",
    "duration": 212,
    "view_count": 1000000,
    "channel": "Channel Name",
    "publish_date": "2023-01-01"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/videos/process" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "download_audio": true,
    "extract_subtitles": true
  }'
```

---

### GET /videos/{video_id}/info

Get stored information about a processed video.

**Parameters:**
- `video_id` (path): YouTube video ID

**Response:**
```json
{
  "success": true,
  "message": "Video information retrieved successfully",
  "timestamp": "2024-01-15T10:30:00",
  "video_info": {
    "id": "dQw4w9WgXcQ",
    "title": "Video Title",
    "duration": 212,
    "description": "Description...",
    "channel": "Channel Name"
  }
}
```

---

### GET /videos/{video_id}/status

Check processing status and available features for a video.

**Parameters:**
- `video_id` (path): YouTube video ID

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "video_exists": true,
  "has_audio": true,
  "has_transcript": true,
  "has_embeddings": false,
  "summaries": ["default", "concise"],
  "rag_ready": true,
  "last_updated": "2024-01-15T10:30:00"
}
```

---

### GET /videos

List all processed videos.

**Response:**
```json
{
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Video Title",
      "duration": 212,
      "processed_at": "2024-01-15T10:30:00",
      "features": ["transcript", "summary", "rag"]
    }
  ],
  "total_count": 1
}
```

---

### DELETE /videos/{video_id}

Delete all stored data for a video.

**Parameters:**
- `video_id` (path): YouTube video ID

**Response:**
```json
{
  "success": true,
  "message": "All data for video dQw4w9WgXcQ deleted successfully",
  "deleted_files": 8
}
```

## Transcription

### POST /videos/{video_id}/transcribe

Transcribe video audio to text using Whisper.

**Parameters:**
- `video_id` (path): YouTube video ID

**Request Body:**
```json
{
  "video_id": "string (required) - YouTube video ID",
  "model_name": "string (optional, default: 'base') - Whisper model",
  "force_retranscribe": "boolean (optional, default: false) - Force new transcription"
}
```

**Whisper Models:**
- `tiny` - Fastest, basic accuracy
- `base` - Good balance (recommended)
- `small` - Better accuracy  
- `medium` - High accuracy
- `large` - Best accuracy, slower

**Response:**
```json
{
  "success": true,
  "message": "Transcription completed successfully",
  "timestamp": "2024-01-15T10:30:00",
  "transcript": {
    "text": "Full transcript text here...",
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

**Example:**
```bash
curl -X POST "http://localhost:8000/videos/dQw4w9WgXcQ/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "model_name": "base",
    "force_retranscribe": false
  }'
```

---

### GET /videos/{video_id}/transcript

Get stored transcript for a video.

**Parameters:**
- `video_id` (path): YouTube video ID

**Response:**
```json
{
  "success": true,
  "message": "Transcript retrieved successfully",
  "timestamp": "2024-01-15T10:30:00",
  "transcript": {
    "text": "Complete transcript text...",
    "language": "en"
  },
  "segments": [...]
}
```

## Summarization

### POST /videos/{video_id}/summarize

Generate AI-powered summary of video content.

**Parameters:**
- `video_id` (path): YouTube video ID

**Request Body:**
```json
{
  "video_id": "string (required) - YouTube video ID",
  "summary_type": "string (optional, default: 'default') - Summary type",
  "engine": "string (optional, default: 'gemini') - AI engine",
  "force_regenerate": "boolean (optional, default: false) - Force new summary"
}
```

**Summary Types:**
- `default` - Balanced summary with key points
- `concise` - Brief overview (2-3 paragraphs)
- `detailed` - Comprehensive analysis with examples
- `bullet` - Structured bullet points
- `sections` - Organized by topics/sections

**Response:**
```json
{
  "success": true,
  "message": "Summary generated successfully",
  "timestamp": "2024-01-15T10:30:00",
  "summary": "This video discusses the main concepts...",
  "summary_type": "default"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/videos/dQw4w9WgXcQ/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "summary_type": "bullet",
    "engine": "gemini"
  }'
```

---

### GET /videos/{video_id}/summary

Get stored summary for a video.

**Parameters:**
- `video_id` (path): YouTube video ID
- `summary_type` (query, optional): Summary type (default: "default")

**Response:**
```json
{
  "success": true,
  "message": "Summary retrieved successfully",
  "timestamp": "2024-01-15T10:30:00",
  "summary": "This video discusses...",
  "summary_type": "default"
}
```

## RAG & Q&A

### POST /videos/{video_id}/embeddings

Create vector embeddings for RAG functionality.

**Parameters:**
- `video_id` (path): YouTube video ID

**Request Body:**
```json
{
  "video_id": "string (required) - YouTube video ID",
  "for_rag": "boolean (optional, default: true) - Create for RAG system",
  "force_recreate": "boolean (optional, default: false) - Force recreation"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Embeddings created successfully",
  "chunks_created": 45,
  "embedding_dimension": 768
}
```

---

### POST /videos/{video_id}/setup-rag

Initialize RAG system for intelligent Q&A.

**Parameters:**
- `video_id` (path): YouTube video ID

**Response:**
```json
{
  "success": true,
  "message": "RAG system initialized successfully",
  "status": "ready_for_questions",
  "video_id": "dQw4w9WgXcQ"
}
```

---

### POST /videos/{video_id}/ask

Ask questions about video content using RAG.

**Parameters:**
- `video_id` (path): YouTube video ID

**Request Body:**
```json
{
  "video_id": "string (required) - YouTube video ID",
  "question": "string (required) - Question to ask",
  "context_length": "integer (optional, default: 3) - Context chunks to retrieve"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Question answered successfully",
  "timestamp": "2024-01-15T10:30:00",
  "answer": "Based on the video content, the main topic is...",
  "sources": [
    {
      "text": "Relevant transcript segment...",
      "start": 45.2,
      "end": 52.8,
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.87
}
```

**Example Questions:**
- "What are the main points discussed?"
- "How does the speaker explain X concept?"
- "What examples are given?"
- "What is the conclusion?"

**Example:**
```bash
curl -X POST "http://localhost:8000/videos/dQw4w9WgXcQ/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "question": "What are the key takeaways from this video?",
    "context_length": 3
  }'
```

---

### POST /videos/{video_id}/chat

Interactive chat about video content with conversation memory.

**Parameters:**
- `video_id` (path): YouTube video ID

**Request Body:**
```json
{
  "video_id": "string (required) - YouTube video ID",
  "message": "string (required) - Chat message",
  "conversation_id": "string (optional) - Conversation ID for context"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat response generated successfully",
  "timestamp": "2024-01-15T10:30:00",
  "response": "Based on our previous discussion and the video content...",
  "conversation_id": "conv_12345",
  "sources": [...]
}
```

**Example Conversation Flow:**
```bash
# First message
curl -X POST "http://localhost:8000/videos/dQw4w9WgXcQ/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "message": "What is this video about?"
  }'

# Follow-up with conversation ID
curl -X POST "http://localhost:8000/videos/dQw4w9WgXcQ/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "message": "Can you elaborate on the first point?",
    "conversation_id": "conv_12345"
  }'
```

## Text-to-Speech

### POST /videos/{video_id}/tts

Convert summaries or transcripts to audio.

**Parameters:**
- `video_id` (path): YouTube video ID

**Request Body:**
```json
{
  "video_id": "string (required) - YouTube video ID",
  "text_type": "string (optional, default: 'summary') - Text source",
  "summary_type": "string (optional, default: 'default') - Summary type if text_type is summary"
}
```

**Text Types:**
- `summary` - Convert summary to speech
- `transcript` - Convert full transcript to speech

**Response:**
- Returns audio file for download (MP3 format)
- Content-Type: `audio/mpeg`
- Filename: `{video_id}_{text_type}_tts.mp3`

**Example:**
```bash
curl -X POST "http://localhost:8000/videos/dQw4w9WgXcQ/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "text_type": "summary",
    "summary_type": "concise"
  }' \
  --output "video_summary.mp3"
```

## System

### GET /

API welcome message and basic information.

**Response:**
```json
{
  "message": "Welcome to VidSage API 🎥",
  "description": "AI-powered YouTube video analysis platform",
  "docs": "/docs",
  "health": "/health"
}
```

---

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "components": {
    "youtube_processor": "active",
    "transcriber": "active",
    "storage_manager": "active",
    "api_key_configured": true
  }
}
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    // Endpoint-specific data
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-15T10:30:00",
  "detail": "Detailed error information"
}
```

## Error Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameters, malformed JSON |
| 404 | Not Found | Video not found, resource missing |
| 422 | Validation Error | Invalid request body schema |
| 500 | Internal Server Error | Server-side processing error |

### Common Error Scenarios

**Video Not Found (404):**
```json
{
  "success": false,
  "message": "Video not found",
  "detail": "Video with ID 'invalid_id' does not exist"
}
```

**Invalid YouTube URL (400):**
```json
{
  "success": false,
  "message": "Invalid YouTube URL",
  "detail": "URL must be a valid YouTube video URL"
}
```

**Missing API Key (400):**
```json
{
  "success": false,
  "message": "API key is required",
  "detail": "GOOGLE_API_KEY environment variable not found"
}
```

**Transcript Not Found (404):**
```json
{
  "success": false,
  "message": "Transcript not found. Transcribe video first.",
  "detail": "No transcript exists for video ID 'dQw4w9WgXcQ'"
}
```

## Rate Limits

Currently, no rate limits are implemented. Consider implementing rate limiting in production environments:

- **Process Video**: 10 requests per minute
- **Transcribe**: 5 requests per minute per video
- **Ask Questions**: 30 requests per minute
- **Chat**: 20 requests per minute

## Best Practices

1. **Check video status** before processing to avoid unnecessary operations
2. **Use appropriate Whisper models** based on accuracy vs speed requirements
3. **Cache results** by checking if resources exist before recreating
4. **Handle async operations** properly for long-running tasks
5. **Implement retry logic** for external API calls
6. **Monitor API key usage** to avoid quota limits

---

**For more detailed examples and use cases, see the [API README](README.md).**
