#!/usr/bin/env python3
"""
CLI Main Module

This module provides the command-line interface for VidSage.
"""

import os
import sys
import argparse
import logging
import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from dotenv import load_dotenv

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Rich for pretty terminal output
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.markdown import Markdown
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.status import Status
from rich.live import Live
import rich.repr
from rich.style import Style
from rich.theme import Theme

# Prompt toolkit for command input
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import WordCompleter

# Import core modules
from core.youtube_processor import YouTubeProcessor
from core.transcriber import Transcriber
from core.summarizer import Summarizer
from core.embedder import Embedder
from core.rag_system import RAGSystem
from core.rag_agents import QueryAnalyzer, ContentSummarizer, CitationManager
from core.tts_generator import TTSGenerator
from core.storage_manager import StorageManager

# Import utility functions
from utils.helpers import extract_video_id, is_youtube_url, load_api_key, format_transcript_for_display

# Custom theme for chocolatey-like colors
custom_theme = Theme({
    "primary": "bold cyan",
    "secondary": "bold magenta", 
    "accent": "bold yellow",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "bold blue",
    "muted": "dim white",
    "highlight": "bold white on blue",
    "thinking": "dim cyan italic",
    "progress": "green",
    "user_input": "bold cyan",
    "ai_response": "white",
    "citation": "dim blue",
})

# Setup rich console with custom theme
console = Console(theme=custom_theme)

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True, console=console)]
)
logger = logging.getLogger("vidsage")

# Load environment variables
load_dotenv()

class VidSageCLI:
    """Main CLI class for VidSage with enhanced UX"""
    
    def __init__(self):
        """Initialize the VidSage CLI"""
        self._show_startup_animation()
        
        # Load API key
        self.api_key = load_api_key('GOOGLE_API_KEY')
        
        # Initialize components
        self.storage_manager = StorageManager()
        self.youtube_processor = YouTubeProcessor(data_dir="data")  
        self.transcriber = Transcriber(model_name="base")
        self.summarizer = Summarizer(api_key=self.api_key)
        self.tts_generator = TTSGenerator()
        
        # RAG components will be initialized when needed
        self.rag_system = None
        self.query_analyzer = None
        self.content_summarizer = None
        self.citation_manager = None
        
        # Current state
        self.current_video_id = None
        self.current_video_url = None
        self.current_video_info = None
        self.current_transcript = None
        self.current_summary = None
        
        # Command history
        self.history = InMemoryHistory()
        self.session = PromptSession(history=self.history)
        
        # Command completer with enhanced commands
        self.commands = [
            'process', 'transcribe', 'summarize', 'embed', 'rag', 'ask', 'chat',
            'tts', 'show transcript', 'show summary', 'show info', 'cleanup', 
            'help', 'exit', 'clear', 'status'
        ]
        self.completer = WordCompleter(self.commands)
        
        logger.info("VidSage CLI initialized")
    
    def _show_startup_animation(self):
        """Show animated startup sequence"""
        startup_text = """
╭─────────────────────────────────────────╮
│                VidSage                  │
│        🎥 YouTube Analysis Tool         │
╰─────────────────────────────────────────╯
        """
        
        with Status("[primary]Initializing VidSage...[/primary]", console=console) as status:
            import time
            time.sleep(1)
            status.update("[success]Components loaded ✓[/success]")
            time.sleep(0.5)
            
        console.print(Panel(startup_text, style="primary", box=box.DOUBLE))
    
    def _create_thinking_animation(self, message: str = "Thinking"):
        """Create animated thinking indicator"""
        thinking_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return Status(f"[thinking]{message}...[/thinking] [dim]({' '.join(thinking_frames)})[/dim]", console=console)
    
    def _init_rag_components(self):
        """Initialize RAG components when needed"""
        if self.rag_system is None:
            self.rag_system = RAGSystem(api_key=self.api_key)
            
        if self.query_analyzer is None:
            self.query_analyzer = QueryAnalyzer(api_key=self.api_key)
            
        if self.content_summarizer is None:
            self.content_summarizer = ContentSummarizer(api_key=self.api_key)
            
        if self.citation_manager is None:
            self.citation_manager = CitationManager()
    
    def process_video(self, url: str) -> bool:
        """
        Process a YouTube video URL with enhanced UX
        
        Args:
            url: YouTube video URL
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate URL
            if not is_youtube_url(url):
                console.print("[error]Error:[/error] Invalid YouTube URL")
                return False
            
            console.print(f"\n[primary]🔗 Processing:[/primary] {url}")
            
            with Progress(
                SpinnerColumn(style="primary"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="success", finished_style="success"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Extract video ID
                task = progress.add_task("[primary]🔍 Extracting video information...[/primary]", total=100)
                video_id = extract_video_id(url)
                progress.update(task, advance=25)
                
                # Set current video ID and URL
                self.current_video_id = video_id
                self.current_video_url = url
                self.storage_manager.set_current_video(video_id)
                progress.update(task, advance=25)
                
                # Get video info
                progress.update(task, description="[primary]📋 Getting video metadata...[/primary]")
                self.current_video_info = self.youtube_processor.get_video_info(url)
                progress.update(task, advance=25)
                
                # Save video info
                progress.update(task, description="[primary]💾 Saving video information...[/primary]")
                self.storage_manager.save_video_info(self.current_video_info)
                progress.update(task, advance=25, description="[success]✅ Video info processed[/success]")
                
                # Check for subtitles
                subtitles_task = progress.add_task("[primary]🔍 Checking for subtitles...[/primary]", total=100)
                subtitles_info = self.current_video_info.get('subtitles', {})
                has_manual_subs = bool(subtitles_info.get('languages', {}).get('manual', []))
                has_auto_subs = bool(subtitles_info.get('languages', {}).get('automatic', []))
                progress.update(subtitles_task, advance=50)
                
                subtitle_transcript = None
                if has_manual_subs or has_auto_subs:
                    progress.update(subtitles_task, description="[success]📝 Subtitles found - downloading...[/success]")
                    
                    # Try to get transcript from subtitles
                    subtitle_transcript = self.youtube_processor.get_transcript_from_subtitles(url)
                    
                    if subtitle_transcript:
                        progress.update(subtitles_task, advance=50, description="[success]✅ Subtitles processed as transcript[/success]")
                        
                        # Save subtitle transcript
                        self.storage_manager.save_transcript(self.current_video_id, subtitle_transcript)
                        self.current_transcript = subtitle_transcript
                    else:
                        progress.update(subtitles_task, advance=50, description="[warning]⚠️ Subtitles found but failed to extract[/warning]")
                else:
                    progress.update(subtitles_task, advance=50, description="[warning]ℹ️ No subtitles available[/warning]")
                
                # If no subtitles available, download audio for transcription
                if not subtitle_transcript:
                    audio_task = progress.add_task("[primary]🎵 Downloading audio for transcription...[/primary]", total=100)
                    
                    # Download audio
                    audio_data, _ = self.youtube_processor.download_audio(url)
                    progress.update(audio_task, advance=70)
                    
                    # Save audio
                    self.storage_manager.save_audio(audio_data)
                    progress.update(audio_task, advance=30, description="[success]✅ Audio downloaded and saved[/success]")
            
            # Display results with elegant formatting
            console.print()
            if subtitle_transcript:
                console.print("[success]🎉 Processing complete! Using subtitles as transcript.[/success]")
                console.print("[info]💡 Ready for summarization and Q&A![/info]")
            else:
                console.print("[success]🎉 Processing complete! Audio downloaded.[/success]") 
                console.print("[info]💡 Use 'transcribe' command next, then you can summarize or ask questions.[/info]")
            
            # Display video info
            self._display_video_info_enhanced()
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def transcribe_video(self) -> bool:
        """
        Transcribe the current video with enhanced UX
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[error]Error:[/error] No video selected. Use [user_input]process[/user_input] command first.")
                return False
            
            # Check if transcript already exists (from subtitles or previous transcription)
            if self.storage_manager.has_transcript(self.current_video_id):
                # Ask if user wants to overwrite
                console.print("[warning]⚠️ Transcript already exists.[/warning]")
                if not Confirm.ask("[accent]Regenerate using audio transcription?[/accent]"):
                    # Load existing transcript
                    with self._create_thinking_animation("Loading existing transcript"):
                        self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                    console.print("[success]✅ Loaded existing transcript[/success]")
                    self._display_transcript_preview_enhanced()
                    return True
            
            # Check if audio file exists
            audio_path = self.storage_manager.audio_dir / self.current_video_id / f"{self.current_video_id}.mp3"
            if not audio_path.exists():
                console.print("[error]Error:[/error] Audio file not found.")
                console.print("[info]💡 Tip:[/info] If the video has subtitles, they were already used during processing.")
                return False
            
            console.print("\n[primary]🎵 Starting audio transcription...[/primary]")
            console.print("[muted]This may take several minutes depending on video length[/muted]")
            
            with Progress(
                SpinnerColumn(style="primary"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="success"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Transcribe audio
                task = progress.add_task("[primary]🎤 Transcribing audio...[/primary]", total=100)
                result = self.transcriber.transcribe_with_segments(audio_path)
                progress.update(task, advance=70, description="[primary]📝 Formatting transcript...[/primary]")
                
                # Format transcript
                transcript_text = self.transcriber.format_transcript(result, include_timestamps=True)
                progress.update(task, advance=20, description="[primary]💾 Saving transcript...[/primary]")
                
                # Save transcript
                self.storage_manager.save_transcript(self.current_video_id, transcript_text)
                progress.update(task, advance=10, description="[success]✅ Transcription complete[/success]")
            
            # Set current transcript
            self.current_transcript = transcript_text
            
            console.print("[success]🎉 Audio transcription completed![/success]")
            
            # Display preview
            self._display_transcript_preview_enhanced()
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def _display_transcript_preview_enhanced(self):
        """Display a preview of the current transcript with enhanced formatting"""
        if self.current_transcript:
            preview_lines = self.current_transcript.split('\n')[:8]
            preview_text = '\n'.join(preview_lines)
            
            preview_panel = Panel(
                preview_text,
                title="[info]📝 Transcript Preview[/info]",
                box=box.ROUNDED,
                border_style="info"
            )
            
            console.print()
            console.print(preview_panel)
            console.print(f"[muted]📊 Full transcript: {len(self.current_transcript)} characters, {len(self.current_transcript.split())} words[/muted]")
    
    def summarize_video(self, summary_type: str = "default", engine: str = "gemini") -> bool:
        """
        Summarize the current video with enhanced UX
        
        Args:
            summary_type: Type of summary to generate
            engine: Engine to use (gemini or ollama)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[error]Error:[/error] No video selected. Use [user_input]process[/user_input] command first.")
                return False
            
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                with self._create_thinking_animation("Loading transcript"):
                    self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[error]Error:[/error] No transcript found. Use [user_input]transcribe[/user_input] command first.")
                    return False
            
            # Check if summary already exists
            if self.storage_manager.has_summary(summary_type, self.current_video_id):
                console.print(f"[warning]⚠️ {summary_type.capitalize()} summary already exists.[/warning]")
                if not Confirm.ask(f"[accent]Regenerate {summary_type} summary?[/accent]"):
                    # Load existing summary
                    with self._create_thinking_animation("Loading existing summary"):
                        self.current_summary = self.storage_manager.load_summary(summary_type, self.current_video_id)
                    console.print(f"[success]✅ Loaded existing {summary_type} summary[/success]")
                    self._display_summary_enhanced(summary_type)
                    return True
            
            console.print(f"\n[primary]📊 Generating {summary_type} summary using {engine.upper()}...[/primary]")
            
            with Progress(
                SpinnerColumn(style="primary"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="success"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Generate summary
                task = progress.add_task(f"[primary]🧠 Creating {summary_type} summary...[/primary]", total=100)
                summary = self.summarizer.summarize(self.current_transcript, summary_type, engine)
                progress.update(task, advance=80, description="[primary]💾 Saving summary...[/primary]")
                
                # Save summary
                self.storage_manager.save_summary(summary, summary_type, self.current_video_id)
                progress.update(task, advance=20, description="[success]✅ Summary complete[/success]")
            
            # Set current summary
            self.current_summary = summary
            
            console.print(f"[success]🎉 {summary_type.capitalize()} summary generated![/success]")
            
            # Display summary
            self._display_summary_enhanced(summary_type)
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def create_embeddings(self, for_rag: bool = True) -> bool:
        """
        Create embeddings for the current transcript with enhanced UX
        
        Args:
            for_rag: Whether to use embeddings for RAG
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[error]Error:[/error] No video selected. Use [user_input]process[/user_input] command first.")
                return False
            
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[error]Error:[/error] No transcript found. Use [user_input]transcribe[/user_input] command first.")
                    return False
            
            # Initialize RAG components if needed
            self._init_rag_components()
            
            console.print("\n[primary]🧠 Creating embeddings for Q&A system...[/primary]")
            
            with Progress(
                SpinnerColumn(style="primary"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="success"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Process transcript into chunks
                task = progress.add_task("[primary]📝 Processing transcript into chunks...[/primary]", total=100)
                docs = self.rag_system.process_transcript(self.current_transcript)
                progress.update(task, advance=30, description="[primary]🔗 Creating vector store...[/primary]")
                
                # Create persistence directory
                persist_dir = self.storage_manager.vectorstore_dir / self.current_video_id / "chroma_db"
                persist_dir.mkdir(parents=True, exist_ok=True)
                
                # Create vector store
                self.rag_system.create_vectorstore(docs, persist_directory=str(persist_dir))
                progress.update(task, advance=40, description="[primary]⚡ Setting up QA system...[/primary]")
                
                if for_rag:
                    # Create QA chain
                    self.rag_system.create_qa_chain()
                
                progress.update(task, advance=20, description="[primary]💾 Saving vector store...[/primary]")
                
                # Save vector store
                self.storage_manager.save_vectorstore(self.rag_system.vectorstore, self.current_video_id)
                progress.update(task, advance=10, description="[success]✅ Embeddings complete[/success]")
            
            console.print("[success]🎉 Embeddings created successfully![/success]")
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def setup_rag(self) -> bool:
        """
        Set up RAG for the current video with enhanced UX
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[error]Error:[/error] No video selected. Use [user_input]process[/user_input] command first.")
                return False
            
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[error]Error:[/error] No transcript found. Use [user_input]transcribe[/user_input] command first.")
                    return False
            
            # Initialize RAG components
            self._init_rag_components()
            
            # Check if vector store exists
            vectorstore_result = self.storage_manager.load_vectorstore(self.current_video_id)
            
            if vectorstore_result == "marker_exists" or vectorstore_result == "needs_recreation":
                # Load from persistence directory
                persist_dir = self.storage_manager.vectorstore_dir / self.current_video_id / "chroma_db"
                if persist_dir.exists():
                    console.print("[success]✅ Loading existing vector store[/success]")
                    try:
                        self.rag_system.load_vectorstore(str(persist_dir))
                        # Create QA chain after loading vectorstore
                        self.rag_system.create_qa_chain()
                    except Exception as e:
                        console.print(f"[warning]⚠️ Could not load vectorstore: {e}[/warning]")
                        console.print("[info]ℹ️ Creating new embeddings...[/info]")
                        if not self.create_embeddings_silent(for_rag=True):
                            return False
                else:
                    console.print("[info]ℹ️ Vector store directory not found. Creating embeddings...[/info]")
                    if not self.create_embeddings_silent(for_rag=True):
                        return False
            elif vectorstore_result is not None:
                # Old pickle format - use it but recreate for future
                console.print("[success]✅ Loading existing vector store (legacy format)[/success]")
                self.rag_system.vectorstore = vectorstore_result
                self.rag_system.retriever = vectorstore_result.as_retriever(search_kwargs={"k": 5})
                self.rag_system.create_qa_chain()
            else:
                console.print("[info]ℹ️ No vector store found. Creating embeddings...[/info]")
                if not self.create_embeddings_silent(for_rag=True):
                    return False
            
            console.print("[success]✅ RAG system ready[/success]")
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def create_embeddings_silent(self, for_rag: bool = True) -> bool:
        """
        Create embeddings silently without overlapping progress displays
        
        Args:
            for_rag: Whether to use embeddings for RAG
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize RAG components if needed
            self._init_rag_components()
            
            console.print("[info]🧠 Processing transcript into chunks...[/info]")
            docs = self.rag_system.process_transcript(self.current_transcript)
            
            console.print("[info]🔗 Creating vector store...[/info]")
            
            # Create persistence directory
            persist_dir = self.storage_manager.vectorstore_dir / self.current_video_id / "chroma_db"
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            # Create vectorstore with persistence
            self.rag_system.create_vectorstore(docs, persist_directory=str(persist_dir))
            
            if for_rag:
                console.print("[info]⚡ Creating QA chain...[/info]")
                self.rag_system.create_qa_chain()
            
            console.print("[info]💾 Saving vector store...[/info]")
            self.storage_manager.save_vectorstore(self.rag_system.vectorstore, self.current_video_id)
            
            console.print("[success]✅ Embeddings created successfully[/success]")
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error creating embeddings:[/error] {str(e)}")
            return False
    
    def ask_question(self, question: str) -> bool:
        """
        Ask a question about the video using RAG with enhanced UX
        
        Args:
            question: Question to ask
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if RAG is set up
            if not self.rag_system or not self.rag_system.rag_chain:
                with self._create_thinking_animation("Setting up RAG"):
                    if not self.setup_rag():
                        return False
            
            # Initialize query analyzer if needed
            if self.query_analyzer is None:
                self.query_analyzer = QueryAnalyzer(api_key=self.api_key)
            
            console.print(f"\n[user_input]❓ Question:[/user_input] {question}")
            
            # Process question with thinking animation
            with self._create_thinking_animation("Processing your question") as status:
                # Analyze and improve the query
                improved_question = self.query_analyzer.improve_query(question)
                status.update("[thinking]Finding relevant information...[/thinking]")
                
                # Get citation sources
                citations = self.rag_system.get_citation_sources(improved_question)
                
                # Save citations
                if self.citation_manager:
                    self.citation_manager.add_citation(question, citations)
                    
                status.update("[thinking]Generating answer...[/thinking]")
                
                # Generate answer
                answer = self.rag_system.answer_question(improved_question)
                
                # Clean answer
                answer = self._clean_response(answer)
            
            # Display answer elegantly with terminal-friendly formatting
            console.print()
            console.print("[success]🤖 Answer:[/success]")
            console.print("[muted]" + "─" * 50 + "[/muted]")
            
            # Format answer for terminal display
            formatted_answer = self._format_for_terminal(answer)
            console.print(formatted_answer)
            
            console.print("\n[muted]" + "─" * 50 + "[/muted]")
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def interactive_chat(self) -> bool:
        """
        Start an interactive chat about the video using enhanced chat interface
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if RAG is set up
            if not self.rag_system or not self.rag_system.rag_chain:
                with self._create_thinking_animation("Setting up RAG"):
                    if not self.setup_rag():
                        return False
            
            # Initialize RAG components if needed
            self._init_rag_components()
            
            # Start enhanced chat session
            return self._enhanced_interactive_chat()
                
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def _enhanced_interactive_chat(self) -> bool:
        """Enhanced interactive chat implementation with better UX"""
        try:
            # Clear screen and show chat header
            console.clear()
            self._show_chat_header()
            
            chat_history = []
            
            while True:
                try:
                    # Create elegant prompt
                    console.print()
                    user_question = Prompt.ask(
                        "[user_input]💭 Ask about the video[/user_input]",
                        default="",
                        show_default=False
                    )
                    
                    # Check for exit command
                    if user_question.lower() in ['exit', 'quit', 'q', 'bye']:
                        break
                        
                    if user_question.lower() == 'clear':
                        console.clear()
                        self._show_chat_header()
                        continue
                    
                    if not user_question.strip():
                        continue
                    
                    # Add user question to history
                    chat_history.append({"role": "user", "content": user_question})
                    
                    # Show thinking animation while processing
                    with self._create_thinking_animation("Analyzing your question") as status:
                        time.sleep(0.5)  # Brief pause for animation
                        
                        # Process in background without showing details
                        improved_question = self.query_analyzer.improve_query(user_question)
                        status.update("[thinking]Finding relevant information...[/thinking]")
                        time.sleep(0.3)
                        
                        citations = self.rag_system.get_citation_sources(improved_question)
                        if self.citation_manager:
                            self.citation_manager.add_citation(user_question, citations)
                        
                        status.update("[thinking]Generating response...[/thinking]")
                        time.sleep(0.3)
                        
                        answer = self.rag_system.answer_question(improved_question)
                        
                        # Clean answer to remove timestamps like [00:00]
                        answer = self._clean_response(answer)
                    
                    # Display response elegantly
                    self._display_chat_response(answer, chat_history)
                    
                except KeyboardInterrupt:
                    console.print("\n[muted]Use 'exit' to quit chat[/muted]")
                    continue
                except Exception as e:
                    console.print(f"\n[error]Error processing question:[/error] {str(e)}")
                    continue
            
            # Show farewell message
            console.print("\n[success]✨ Chat session ended. Thanks for using VidSage![/success]")
            return True
            
        except Exception as e:
            console.print(f"[error]Error in chat:[/error] {str(e)}")
            return False
    
    def _show_chat_header(self):
        """Display chat session header"""
        if self.current_video_info:
            title = self.current_video_info.get("title", "Unknown Video")
            author = self.current_video_info.get("author", "Unknown Author")
            
            header_content = f"""
[primary]🎥 Video:[/primary] {title[:60]}{'...' if len(title) > 60 else ''}
[secondary]👤 Author:[/secondary] {author}
[accent]💡 Ready to answer your questions![/accent]

[muted]Commands: 'clear' to clear screen, 'exit'/'quit'/'q' to end chat[/muted]
            """
        else:
            header_content = "[accent]💡 Chat Mode - Ready to answer your questions![/accent]"
            
        console.print(Panel(header_content, box=box.ROUNDED, style="primary"))
    
    def _clean_response(self, response: str) -> str:
        """Remove timestamp markers and clean response"""
        import re
        # Remove timestamp patterns like [00:00], [1:23], [12:34], etc.
        cleaned = re.sub(r'\[\d{1,2}:\d{2}\]', '', response)
        # Remove "at the X mark" references
        cleaned = re.sub(r'at the \[\d{1,2}:\d{2}\] mark', '', cleaned)
        cleaned = re.sub(r'mentioned at the.*?mark', '', cleaned)
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _display_chat_response(self, answer: str, chat_history: list):
        """Display chat response with terminal-friendly formatting"""
        console.print()
        
        # Simple terminal-friendly header
        console.print("[success]🤖 VidSage:[/success]")
        console.print("[muted]" + "─" * 50 + "[/muted]")
        
        # Display answer with simple formatting
        # Convert markdown-style formatting to terminal-friendly format
        formatted_answer = self._format_for_terminal(answer)
        console.print(formatted_answer)
        
        # Add to chat history
        chat_history.append({"role": "assistant", "content": answer})
        
        # Show separator
        console.print("\n[muted]" + "─" * 50 + "[/muted]")
    
    def text_to_speech(self, text_type: str = "summary") -> bool:
        """
        Convert text to speech with enhanced UX
        
        Args:
            text_type: Type of text to convert (summary or transcript)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[error]Error:[/error] No video selected. Use [user_input]process[/user_input] command first.")
                return False
            
            # Get text based on type
            if text_type == "summary":
                if not self.current_summary:
                    # Try to load summary
                    self.current_summary = self.storage_manager.load_summary("default", self.current_video_id)
                    
                    if not self.current_summary:
                        console.print("[error]Error:[/error] No summary found. Use [user_input]summarize[/user_input] command first.")
                        return False
                
                text = self.current_summary
                
            elif text_type == "transcript":
                if not self.current_transcript:
                    # Try to load transcript
                    self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                    
                    if not self.current_transcript:
                        console.print("[error]Error:[/error] No transcript found. Use [user_input]transcribe[/user_input] command first.")
                        return False
                
                text = self.current_transcript
                
            else:
                console.print(f"[error]Error:[/error] Invalid text type: {text_type}")
                return False
            
            # Create output directory
            output_dir = Path("data/tts") / self.current_video_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            console.print(f"\n[primary]🔊 Converting {text_type} to speech...[/primary]")
            
            with Progress(
                SpinnerColumn(style="primary"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="success"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Generate audio segments
                task = progress.add_task("[primary]🎵 Generating audio segments...[/primary]", total=100)
                audio_files = self.tts_generator.generate_audio_segments(text, 1000, output_dir)
                progress.update(task, advance=70, description=f"[primary]🔗 Combining {len(audio_files)} audio segments...[/primary]")
                
                # Combine audio segments
                output_file = output_dir / f"{self.current_video_id}_{text_type}.mp3"
                combined_path = self.tts_generator.combine_audio_files(audio_files, output_file)
                progress.update(task, advance=30, description="[success]✅ Audio generation complete[/success]")
            
            console.print(f"[success]🎉 Audio saved to:[/success] [info]{output_file}[/info]")
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def show_transcript(self) -> bool:
        """
        Display the current transcript with enhanced formatting
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                with self._create_thinking_animation("Loading transcript"):
                    self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[error]Error:[/error] No transcript found. Use [user_input]transcribe[/user_input] command first.")
                    return False
            
            # Display transcript in elegant panel
            transcript_panel = Panel(
                self.current_transcript,
                title="[info]📝 Full Transcript[/info]",
                box=box.ROUNDED,
                border_style="info",
                padding=(1, 2)
            )
            
            console.print()
            console.print(transcript_panel)
            
            # Show stats
            word_count = len(self.current_transcript.split())
            char_count = len(self.current_transcript)
            line_count = len(self.current_transcript.split('\n'))
            
            console.print(f"[muted]📊 Stats: {word_count} words • {char_count} characters • {line_count} lines[/muted]")
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def show_summary(self, summary_type: str = "default") -> bool:
        """
        Display the current summary with enhanced formatting
        
        Args:
            summary_type: Type of summary to show
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load summary
            with self._create_thinking_animation("Loading summary"):
                summary = self.storage_manager.load_summary(summary_type, self.current_video_id)
            
            if not summary:
                console.print(f"[error]Error:[/error] No {summary_type} summary found.")
                console.print(f"[info]💡 Use[/info] [user_input]summarize --type={summary_type}[/user_input] [info]to create one[/info]")
                return False
            
            # Display summary
            self._display_summary_enhanced(summary_type, summary)
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def show_video_info(self) -> bool:
        """
        Display information about the current video with enhanced formatting
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if video info exists
            if not self.current_video_info:
                # Try to load video info
                with self._create_thinking_animation("Loading video information"):
                    self.current_video_info = self.storage_manager.load_video_info(self.current_video_id)
                
                if not self.current_video_info:
                    console.print("[error]Error:[/error] No video info found. Use [user_input]process[/user_input] command first.")
                    return False
            
            # Display video info
            self._display_video_info_enhanced()
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def cleanup_files(self) -> bool:
        """
        Delete all files for the current video with enhanced UX
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[error]Error:[/error] No video selected. Use [user_input]process[/user_input] command first.")
                return False
            
            # Ask for confirmation
            console.print(f"[warning]⚠️ This will delete all files for video {self.current_video_id}[/warning]")
            if not Confirm.ask("[accent]Are you sure you want to continue?[/accent]"):
                console.print("[info]✅ Cleanup canceled[/info]")
                return False
            
            # Delete files with progress
            with self._create_thinking_animation("Cleaning up files"):
                self.storage_manager.cleanup(self.current_video_id)
                
                # Reset current state
                self.current_transcript = None
                self.current_summary = None
            
            console.print("[success]🎉 Cleanup completed successfully[/success]")
            
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return False
    
    def _display_video_info_enhanced(self) -> None:
        """Display information about the current video with enhanced formatting"""
        if not self.current_video_info:
            return
            
        # Create elegant video info display
        title = self.current_video_info.get("title", "Unknown")
        author = self.current_video_info.get("author", "Unknown")
        video_id = self.current_video_info.get("id", "Unknown")
        duration = self.current_video_info.get("length", 0)
        views = self.current_video_info.get("views", 0)
        publish_date = self.current_video_info.get("publish_date", "Unknown")
        
        # Format duration elegantly
        minutes = duration // 60
        seconds = duration % 60
        duration_str = f"{minutes}m {seconds}s"
        
        # Create info panel content
        info_content = f"""[primary]🎥 Title:[/primary] {title}
[secondary]👤 Author:[/secondary] {author}
[accent]🆔 Video ID:[/accent] {video_id}
[info]⏱️ Duration:[/info] {duration_str}
[success]👁️ Views:[/success] {views:,}
[muted]📅 Published:[/muted] {publish_date}"""
        
        info_panel = Panel(
            info_content,
            title="[highlight]📺 Video Information[/highlight]",
            box=box.ROUNDED,
            border_style="primary"
        )
        
        console.print()
        console.print(info_panel)
        
        # Show description if available
        description = self.current_video_info.get("description", "")
        if description:
            desc_preview = description[:200] + ("..." if len(description) > 200 else "")
            desc_panel = Panel(
                desc_preview,
                title="[muted]📝 Description[/muted]",
                box=box.ROUNDED,
                border_style="muted"
            )
            console.print()
            console.print(desc_panel)
    
    def _display_summary_enhanced(self, summary_type: str = "default", summary: Optional[str] = None) -> None:
        """
        Display a summary with enhanced formatting
        
        Args:
            summary_type: Type of summary to display
            summary: Summary text (uses current_summary if None)
        """
        if summary is None:
            summary = self.current_summary
            
        if not summary:
            return
            
        # Format title based on summary type
        title_map = {
            "concise": "📄 Concise Summary",
            "detailed": "📋 Detailed Summary", 
            "bullet": "📝 Bullet-Point Summary",
            "sections": "🗂️ Sectioned Summary",
            "default": "📊 Summary"
        }
        
        title = title_map.get(summary_type, "📊 Summary")
        
        # Display summary in elegant panel
        summary_panel = Panel(
            Markdown(summary),
            title=f"[success]{title}[/success]",
            box=box.ROUNDED,
            border_style="success"
        )
        
        console.print()
        console.print(summary_panel)
    
    def show_help(self) -> None:
        """Display help information with enhanced formatting"""
        help_content = """
[primary]🎯 Basic Workflow[/primary]

[accent]1.[/accent] [user_input]process <url>[/user_input] - Process a YouTube video (auto-detects subtitles/audio)
[accent]2.[/accent] [user_input]transcribe[/user_input] - Transcribe audio (only if subtitles unavailable)  
[accent]3.[/accent] [user_input]summarize[/user_input] - Generate AI summary
[accent]4.[/accent] [user_input]chat[/user_input] - Interactive Q&A about the video

[primary]📋 All Commands[/primary]

[secondary]Processing:[/secondary]
• [user_input]process <url>[/user_input] - Download and analyze video
• [user_input]transcribe[/user_input] - Transcribe audio (if needed)

[secondary]Analysis:[/secondary]  
• [user_input]summarize [--type=<type>] [--gemini|--ollama][/user_input] - Generate summary
• [user_input]embed [--rag][/user_input] - Create embeddings
• [user_input]rag[/user_input] - Set up Q&A system
• [user_input]ask <question>[/user_input] - Ask about video content
• [user_input]chat[/user_input] - Interactive chat mode

[secondary]Display:[/secondary]
• [user_input]show transcript[/user_input] - View full transcript
• [user_input]show summary [--type=<type>][/user_input] - View summary
• [user_input]show info[/user_input] - Video information
• [user_input]status[/user_input] - Current application status

[secondary]Utilities:[/secondary]
• [user_input]tts [--transcript|--summary][/user_input] - Text-to-speech
• [user_input]cleanup[/user_input] - Delete video files
• [user_input]clear[/user_input] - Clear screen
• [user_input]help[/user_input] - Show this help
• [user_input]exit[/user_input] - Quit application

[primary]📝 Summary Types[/primary]
• [accent]concise[/accent] - Brief 3-5 sentence summary
• [accent]detailed[/accent] - Comprehensive analysis
• [accent]bullet[/accent] - Key points in bullet format
• [accent]sections[/accent] - Organized by topics

[primary]💡 Example Usage[/primary]
[muted]VidSage ❯[/muted] [user_input]process https://youtube.com/watch?v=VIDEO_ID[/user_input]
[muted]VidSage ❯[/muted] [user_input]summarize --type=bullet[/user_input]
[muted]VidSage ❯[/muted] [user_input]ask What are the main topics?[/user_input]
[muted]VidSage ❯[/muted] [user_input]chat[/user_input]
        """
        
        help_panel = Panel(
            help_content,
            title="[highlight]📚 VidSage Help[/highlight]",
            box=box.ROUNDED,
            border_style="primary",
            padding=(1, 2)
        )
        
        console.print()
        console.print(help_panel)
    
    def parse_args(self, command: str) -> Tuple[str, Dict[str, str]]:
        """
        Parse command line arguments
        
        Args:
            command: Command string
            
        Returns:
            Tuple of (command, args)
        """
        # Split command and arguments
        parts = command.strip().split()
        if not parts:
            return "", {}
            
        cmd = parts[0].lower()
        args = {}
        
        # Parse arguments
        for part in parts[1:]:
            # Check for --key=value format
            if part.startswith("--") and "=" in part:
                key, value = part[2:].split("=", 1)
                args[key] = value
            # Check for --key format (flags)
            elif part.startswith("--"):
                args[part[2:]] = "true"
            # Otherwise it's a positional argument
            else:
                # Handle special cases
                if cmd == "process":
                    args["url"] = part
                elif cmd == "ask":
                    # For ask command, combine all remaining parts as the question
                    question_index = parts.index(part)
                    args["question"] = " ".join(parts[question_index:])
                    break
                elif cmd == "show" and part == "transcript":
                    return "show transcript", {}
                elif cmd == "show" and part == "summary":
                    return "show summary", {}
                elif cmd == "show" and part == "info":
                    return "show info", {}
        
        return cmd, args
    
    def run_command(self, command: str) -> bool:
        """
        Run a command with enhanced UX
        
        Args:
            command: Command string
            
        Returns:
            True if successful or command should continue, False to exit
        """
        try:
            # Parse command and arguments
            cmd, args = self.parse_args(command)
            
            # Process commands
            if cmd == "process":
                url = args.get("url")
                if not url:
                    console.print("[error]Error:[/error] URL is required")
                    console.print("[info]Usage:[/info] process <youtube_url>")
                    return True
                self.process_video(url)
                
            elif cmd == "transcribe":
                self.transcribe_video()
                
            elif cmd == "summarize":
                summary_type = args.get("type", "default")
                engine = "ollama" if "ollama" in args else "gemini"
                self.summarize_video(summary_type, engine)
                
            elif cmd == "embed":
                for_rag = "rag" in args
                self.create_embeddings(for_rag)
                
            elif cmd == "rag":
                self.setup_rag()
                
            elif cmd == "ask":
                question = args.get("question")
                if not question:
                    console.print("[error]Error:[/error] Question is required")
                    console.print("[info]Usage:[/info] ask <your question>")
                    return True
                self.ask_question(question)
                
            elif cmd == "chat":
                self.interactive_chat()
                
            elif cmd == "tts":
                text_type = "transcript" if "transcript" in args else "summary"
                self.text_to_speech(text_type)
                
            elif cmd == "show transcript":
                self.show_transcript()
                
            elif cmd == "show summary":
                summary_type = args.get("type", "default")
                self.show_summary(summary_type)
                
            elif cmd == "show info":
                self.show_video_info()
                
            elif cmd == "cleanup":
                self.cleanup_files()
                
            elif cmd == "clear":
                self.clear_screen()
                
            elif cmd == "status":
                self.show_status()
                
            elif cmd == "help":
                self.show_help()
                
            elif cmd in ["exit", "quit", "q"]:
                console.print("[success]✨ Thanks for using VidSage! Goodbye![/success]")
                return False
                
            elif cmd:
                console.print(f"[error]Unknown command:[/error] [user_input]{cmd}[/user_input]")
                console.print("[info]💡 Type 'help' to see available commands[/info]")
                
            return True
            
        except Exception as e:
            console.print(f"[error]Error:[/error] {str(e)}")
            return True
    
    def run(self) -> None:
        """Run the CLI interface with enhanced UX"""
        # Display welcome message with animation
        self._show_welcome_screen()
        
        # Check API key
        if not self.api_key:
            console.print("[warning]⚠️ Warning:[/warning] GOOGLE_API_KEY environment variable not found")
            console.print("[muted]Some features may be limited or unavailable[/muted]")
        
        # Main loop
        while True:
            try:
                # Create elegant prompt
                console.print()
                command = self.session.prompt(
                    HTML('<primary><b>VidSage</b></primary> <accent>❯</accent> '),
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self.completer
                )
                
                # Run command
                if not self.run_command(command):
                    break
                    
            except KeyboardInterrupt:
                console.print("\n[warning]💡 Use 'exit' to quit gracefully[/warning]")
            except EOFError:
                console.print("\n[success]✨ Thanks for using VidSage! Goodbye![/success]")
                break
    
    def _show_welcome_screen(self):
        """Show enhanced welcome screen"""
        welcome_content = f"""
[primary]Welcome to VidSage![/primary] 🚀

[accent]🎯 Quick Start:[/accent]
• [user_input]process <youtube_url>[/user_input] - Analyze a video
• [user_input]chat[/user_input] - Interactive Q&A about your video  
• [user_input]help[/user_input] - Show all commands

[muted]💡 Pro tip: VidSage automatically uses subtitles when available for faster processing![/muted]
        """
        
        welcome_panel = Panel(
            welcome_content,
            title="[highlight]🎥 YouTube Video Analysis Tool[/highlight]",
            box=box.DOUBLE,
            border_style="primary",
            padding=(1, 2)
        )
        
        console.print(welcome_panel)
    
    def clear_screen(self):
        """Clear screen and show header"""
        console.clear()
        console.print("[primary]VidSage[/primary] - [accent]YouTube Video Analysis Tool[/accent]")
        console.print("[muted]" + "─" * 60 + "[/muted]")
    
    def show_status(self):
        """Show current application status"""
        status_content = ""
        
        if self.current_video_id:
            video_title = self.current_video_info.get("title", "Unknown") if self.current_video_info else "Unknown"
            status_content += f"[primary]📹 Current Video:[/primary] {video_title[:50]}{'...' if len(video_title) > 50 else ''}\n"
            status_content += f"[secondary]🆔 Video ID:[/secondary] {self.current_video_id}\n"
            
            # Check what's available
            has_transcript = bool(self.current_transcript or self.storage_manager.has_transcript(self.current_video_id))
            has_summary = bool(self.current_summary or self.storage_manager.has_summary("default", self.current_video_id))
            has_rag = bool(self.rag_system and self.rag_system.rag_chain)
            
            status_content += f"[{'success' if has_transcript else 'muted'}]📝 Transcript: {'✓' if has_transcript else '✗'}[/{'success' if has_transcript else 'muted'}]\n"
            status_content += f"[{'success' if has_summary else 'muted'}]📊 Summary: {'✓' if has_summary else '✗'}[/{'success' if has_summary else 'muted'}]\n" 
            status_content += f"[{'success' if has_rag else 'muted'}]🤖 RAG System: {'✓' if has_rag else '✗'}[/{'success' if has_rag else 'muted'}]"
        else:
            status_content = "[muted]No video currently loaded. Use 'process <url>' to get started.[/muted]"
        
        status_panel = Panel(
            status_content,
            title="[info]📊 Current Status[/info]",
            box=box.ROUNDED,
            border_style="info"
        )
        
        console.print()
        console.print(status_panel)

    def _format_for_terminal(self, text: str):
        """Format answer for terminal display using rich Markdown rendering."""
        from rich.markdown import Markdown
        return Markdown(text)


def main() -> None:
    """Main entry point"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="VidSage - YouTube Video Analysis Tool")
    parser.add_argument("--url", type=str, help="YouTube URL to process")
    args = parser.parse_args()
    
    # Create and run CLI
    cli = VidSageCLI()
    
    # Process URL if provided
    if args.url:
        cli.process_video(args.url)
    
    # Run CLI
    cli.run()


if __name__ == "__main__":
    main()
