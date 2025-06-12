# YouTube Insight ChatBot

A CLI-based tool for analyzing YouTube videos using local transcription, summarization, and text-to-speech capabilities.

## Features

- **Download YouTube Videos**: Extract audio from any YouTube video
- **Transcription**: Convert speech to text using OpenAI's Whisper
- **Summarization**: Generate concise summaries using Ollama LLM
- **Embeddings**: Create and store vector embeddings for transcript text
- **Text-to-Speech**: Convert summaries back to audio

## Architecture

This project follows a modular, object-oriented design with the following components:

- **CLI**: Command-line interface for user interaction
- **YouTubeProcessor**: Downloads videos and extracts audio
- **Transcriber**: Converts audio to text
- **Summarizer**: Generates summaries from transcripts
- **Embedder**: Creates vector embeddings for text retrieval
- **TTSGenerator**: Converts text to speech
- **StorageManager**: Manages file I/O operations

## Requirements

- Python 3.8+
- Ollama (for local LLM capabilities)
- GPU recommended for faster transcription

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd yt_insight_chatbot
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Ollama (if not already installed):
   - Follow instructions at [https://ollama.com/](https://ollama.com/)
   - Pull the required model: `ollama pull llama3`

## Usage

### Basic Usage

```bash
python -m cli.main
```

This will start the CLI interface, where you can enter commands.

### Process a YouTube Video

```bash
# In the CLI interface:
YTInsight> process https://www.youtube.com/watch?v=VIDEO_ID
```

### Workflow Commands

1. Download and extract audio:
   ```
   YTInsight> process https://www.youtube.com/watch?v=VIDEO_ID
   ```

2. Transcribe the video:
   ```
   YTInsight> transcribe
   ```

3. Generate a summary:
   ```
   YTInsight> summarize
   ```

4. Generate embeddings for search:
   ```
   YTInsight> embed
   ```

5. Convert summary to speech:
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
│   ├── tts_generator.py
│   └── storage_manager.py
│
├── data/                # Transcripts, summaries, embeddings
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
- Improved question-answering using RAG
- Multiple language support
- Enhanced audio processing options
- Chat history and persistent storage

## License

[License information]

## Contributors

[Your Name or Team]