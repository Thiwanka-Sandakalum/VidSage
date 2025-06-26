# VidSage

A powerful tool for analyzing YouTube videos using transcription, AI summarization, Retrieval-Augmented Generation (RAG), and text-to-speech capabilities. This tool helps you extract insights from video content with advanced AI features.

## Features

- **Download YouTube Videos**: Extract audio from any YouTube video
- **Transcription**: Convert speech to text using OpenAI's Whisper
- **Summarization**: Generate concise summaries using Ollama LLM or Gemini AI
- **Question-Answering**: Ask questions about video content using RAG with Gemini
- **Interactive Chat**: Have conversations about video content with context-aware responses
- **Embeddings**: Create and store vector embeddings for transcript text
- **Text-to-Speech**: Convert summaries back to audio
- **Subtitles Processing**: Automatically fetch subtitles when available

## Quick Start with Video RAG Pipeline

The simplest way to use VidSage is through the new end-to-end pipeline:

```bash
# Process a video and start an interactive Q&A session
python video_rag_pipeline.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --interactive

# Just process a video without Q&A
python video_rag_pipeline.py --url "https://www.youtube.com/watch?v=VIDEO_ID" 

# Start the tool and enter URL interactively
python video_rag_pipeline.py
```

### Pipeline Features

The video_rag_pipeline.py script provides:

1. **Automatic Subtitle Detection**: Uses subtitles when available instead of transcribing
2. **Full Automatic Processing**: Downloads, transcribes, and prepares RAG system in one step
3. **Interactive Q&A**: Ask unlimited questions about the video content
4. **Citation Support**: Answers include references to the relevant parts of the video

## Architecture

VidSage follows a clean, modular, object-oriented design with the following components:

- **CLI**: Command-line interface for user interaction
- **YouTubeProcessor**: Downloads videos and extracts audio
- **Transcriber**: Converts audio to text
- **Storage Manager**: Handles file operations and data persistence
- **AI Module**: Provides unified AI capabilities
  - **RAG System**: Core retrieval-augmented generation functionality
  - **Query Analyzer**: Improves question understanding
  - **Content Summarizer**: Generates various types of content summaries
  - **Citation Manager**: Tracks sources and manages feedback

### AI Module Features

The AI module provides several advanced capabilities:

1. **Retrieval-Augmented Generation (RAG)**
   - Chunks and indexes transcripts for efficient retrieval
   - Retrieves relevant transcript sections based on user queries
   - Generates accurate answers with context awareness

2. **Multiple Summarization Formats**
   - Concise summaries for quick overviews
   - Detailed summaries with comprehensive coverage
   - Bullet-point summaries for easy scanning
   - Sectioned summaries organized by topic

3. **Citation and Feedback System**
   - Tracks source timestamps in the video
   - Collects user feedback to improve responses
   - Provides evidence for AI-generated answers

### Process a YouTube Video

```bash
# In the CLI interface:
VidSage> process https://www.youtube.com/watch?v=VIDEO_ID
```

### Workflow Examples

1. Basic workflow - Transcribe and Summarize:
   ```
   VidSage> process https://www.youtube.com/watch?v=VIDEO_ID
   VidSage> transcribe
   VidSage> summarize
   ```

2. Advanced Q&A workflow:
   ```
   VidSage> process https://www.youtube.com/watch?v=VIDEO_ID
   VidSage> transcribe
   VidSage> rag
   VidSage> ask What are the main points covered in this video?
   ```

3. Different summary formats:
   ```
   VidSage> summarize --type=concise
   VidSage> summarize --type=bullet
   VidSage> summarize --type=sections
   ```
  ```

2. Transcribe the video:
   ```
   YTInsight> transcribe
   ```

3. Generate a summary:
   ```
   YTInsight> summarize
   ```
   Use `summarize --gemini` to use Gemini AI instead of Ollama.

4. Generate embeddings for RAG:
   ```
   YTInsight> embed --rag
   ```

5. Ask questions about the video:
   ```
   YTInsight> ask What is the main topic of this video?
   ```

6. Start an interactive chat about the video:
   ```
   YTInsight> chat
   ```

7. Convert summary to speech:
   ```
   YTInsight> tts
   ```

### Other Commands

- `show transcript` - Display the full transcript
- `show summary` - Display the summary
- `show info` - Show video information
- `cleanup` - Delete all files for the current video
- `exit` - Exit the application

### Direct URL Processing

You can also provide a YouTube URL directly when starting the application:

```bash
python -m cli.main --url https://www.youtube.com/watch?v=VIDEO_ID
```

## Project Structure

```
/yt_insight_chatbot/
│
├── cli/                 # CLI logic and interaction
│   ├── __init__.py
│   └── main.py
│
├── core/                # Core logic
│   ├── __init__.py
│   ├── youtube_processor.py
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── embedder.py
│   ├── rag_system.py    # RAG implementation
│   ├── rag_agents.py    # AI agents and tools
│   ├── tts_generator.py
│   └── storage_manager.py
│
├── data/                # Transcripts, summaries, embeddings, vectorstores
│
├── utils/               # Helper functions
│   ├── __init__.py
│   └── helpers.py
│
├── requirements.txt
└── README.md
```

## OOP Principles Applied

- **Encapsulation**: Each module encapsulates its own functionality
- **Abstraction**: High-level interfaces hide implementation details
- **Modularity**: Components are independent and interchangeable
- **Reusability**: Components can be reused in other applications

## Design Patterns

- **Facade**: CLI acts as a facade to the underlying system
- **Strategy**: Different implementations can be swapped (e.g., TTS engines)
- **Dependency Injection**: Components receive their dependencies

## Future Enhancements

- Web UI using Flask/FastAPI
- Multiple language support
- Enhanced audio processing options
- Chat history and persistent storage
- RAG retrieval optimization
- Multi-modal Gemini integration with video frames

## License

[License information]

## Contributors

[Your Name or Team]