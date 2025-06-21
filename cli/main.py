#!/usr/bin/env python3
"""
CLI Main Module

This module provides the command-line interface for VidSage.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
import time
from dotenv import load_dotenv

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

# Prompt toolkit for command input
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
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

# Setup rich console
console = Console()

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)
logger = logging.getLogger("vidsage")

# Load environment variables
load_dotenv()

class VidSageCLI:
    """Main CLI class for VidSage"""
    
    def __init__(self):
        """Initialize the VidSage CLI"""
        # Load API key
        self.api_key = load_api_key('GOOGLE_API_KEY')
        
        # Initialize components
        self.storage_manager = StorageManager()
        self.youtube_processor = YouTubeProcessor()
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
        
        # Command completer
        self.commands = [
            'process', 'transcribe', 'summarize', 'embed', 'rag', 'ask', 'chat',
            'tts', 'show transcript', 'show summary', 'show info', 'cleanup', 'help', 'exit'
        ]
        self.completer = WordCompleter(self.commands)
        
        logger.info("VidSage CLI initialized")
    
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
        Process a YouTube video URL
        
        Args:
            url: YouTube video URL
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate URL
            if not is_youtube_url(url):
                console.print("[bold red]Error:[/bold red] Invalid YouTube URL")
                return False
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Extract video ID
                task = progress.add_task("[cyan]Extracting video ID...[/cyan]", total=None)
                video_id = extract_video_id(url)
                progress.update(task, completed=True, description="[green]Video ID extracted[/green]")
                
                # Set current video ID and URL
                self.current_video_id = video_id
                self.current_video_url = url
                self.storage_manager.set_current_video(video_id)
                
                # Get video info
                task = progress.add_task("[cyan]Getting video info...[/cyan]", total=None)
                self.current_video_info = self.youtube_processor.get_video_info(url)
                progress.update(task, completed=True, description="[green]Video info retrieved[/green]")
                
                # Save video info
                task = progress.add_task("[cyan]Saving video info...[/cyan]", total=None)
                self.storage_manager.save_video_info(self.current_video_info)
                progress.update(task, completed=True, description="[green]Video info saved[/green]")
                
                # Download audio
                task = progress.add_task("[cyan]Downloading audio...[/cyan]", total=None)
                audio_data, _ = self.youtube_processor.download_audio(url)
                progress.update(task, completed=True, description="[green]Audio downloaded[/green]")
                
                # Save audio
                task = progress.add_task("[cyan]Saving audio...[/cyan]", total=None)
                self.storage_manager.save_audio(audio_data)
                progress.update(task, completed=True, description="[green]Audio saved[/green]")
            
            # Display video info
            self._display_video_info()
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def transcribe_video(self) -> bool:
        """
        Transcribe the current video
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[bold red]Error:[/bold red] No video selected. Use 'process' command first.")
                return False
            
            # Check if transcript already exists
            if self.storage_manager.has_transcript(self.current_video_id):
                # Ask if user wants to overwrite
                if not Confirm.ask("Transcript already exists. Do you want to regenerate it?"):
                    # Load existing transcript
                    self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                    console.print("[green]Loaded existing transcript[/green]")
                    return True
            
            # Load audio data
            audio_path = self.storage_manager.audio_dir / self.current_video_id / f"{self.current_video_id}.mp3"
            if not audio_path.exists():
                console.print("[bold red]Error:[/bold red] Audio file not found")
                return False
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Transcribe audio
                task = progress.add_task("[cyan]Transcribing audio (this may take a while)...[/cyan]", total=None)
                result = self.transcriber.transcribe_with_segments(audio_path)
                progress.update(task, completed=True, description="[green]Transcription complete[/green]")
                
                # Format transcript
                task = progress.add_task("[cyan]Formatting transcript...[/cyan]", total=None)
                transcript_text = self.transcriber.format_transcript(result, include_timestamps=True)
                progress.update(task, completed=True, description="[green]Transcript formatted[/green]")
                
                # Save transcript
                task = progress.add_task("[cyan]Saving transcript...[/cyan]", total=None)
                self.storage_manager.save_transcript(transcript_text, self.current_video_id)
                progress.update(task, completed=True, description="[green]Transcript saved[/green]")
            
            # Set current transcript
            self.current_transcript = transcript_text
            
            # Display preview
            console.print("\n[bold]Transcript Preview:[/bold]")
            preview_lines = transcript_text.split('\n')[:10]
            preview_text = '\n'.join(preview_lines)
            console.print(Panel(preview_text, width=100, expand=False))
            console.print(f"\n[dim]Full transcript length: {len(transcript_text)} characters[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def summarize_video(self, summary_type: str = "default", engine: str = "gemini") -> bool:
        """
        Summarize the current video
        
        Args:
            summary_type: Type of summary to generate
            engine: Engine to use (gemini or ollama)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[bold red]Error:[/bold red] No video selected. Use 'process' command first.")
                return False
            
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[bold red]Error:[/bold red] No transcript found. Use 'transcribe' command first.")
                    return False
            
            # Check if summary already exists
            if self.storage_manager.has_summary(summary_type, self.current_video_id):
                # Ask if user wants to overwrite
                if not Confirm.ask(f"{summary_type.capitalize()} summary already exists. Do you want to regenerate it?"):
                    # Load existing summary
                    self.current_summary = self.storage_manager.load_summary(summary_type, self.current_video_id)
                    console.print(f"[green]Loaded existing {summary_type} summary[/green]")
                    self._display_summary(summary_type)
                    return True
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Generate summary
                task = progress.add_task(f"[cyan]Generating {summary_type} summary with {engine}...[/cyan]", total=None)
                summary = self.summarizer.summarize(self.current_transcript, summary_type, engine)
                progress.update(task, completed=True, description="[green]Summary generated[/green]")
                
                # Save summary
                task = progress.add_task("[cyan]Saving summary...[/cyan]", total=None)
                self.storage_manager.save_summary(summary, summary_type, self.current_video_id)
                progress.update(task, completed=True, description="[green]Summary saved[/green]")
            
            # Set current summary
            self.current_summary = summary
            
            # Display summary
            self._display_summary(summary_type)
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def create_embeddings(self, for_rag: bool = True) -> bool:
        """
        Create embeddings for the current transcript
        
        Args:
            for_rag: Whether to use embeddings for RAG
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[bold red]Error:[/bold red] No video selected. Use 'process' command first.")
                return False
            
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[bold red]Error:[/bold red] No transcript found. Use 'transcribe' command first.")
                    return False
            
            # Initialize RAG components if needed
            self._init_rag_components()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Process transcript into chunks
                task = progress.add_task("[cyan]Processing transcript into chunks...[/cyan]", total=None)
                docs = self.rag_system.process_transcript(self.current_transcript)
                progress.update(task, completed=True, description="[green]Transcript chunked[/green]")
                
                # Create vector store
                task = progress.add_task("[cyan]Creating vector store...[/cyan]", total=None)
                self.rag_system.create_vectorstore(docs)
                progress.update(task, completed=True, description="[green]Vector store created[/green]")
                
                if for_rag:
                    # Create QA chain
                    task = progress.add_task("[cyan]Creating QA chain...[/cyan]", total=None)
                    self.rag_system.create_qa_chain()
                    progress.update(task, completed=True, description="[green]QA chain created[/green]")
                
                # Save vector store
                task = progress.add_task("[cyan]Saving vector store...[/cyan]", total=None)
                self.storage_manager.save_vectorstore(self.rag_system.vectorstore, self.current_video_id)
                progress.update(task, completed=True, description="[green]Vector store saved[/green]")
            
            console.print("[green]Embeddings created successfully[/green]")
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def setup_rag(self) -> bool:
        """
        Set up RAG for the current video
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[bold red]Error:[/bold red] No video selected. Use 'process' command first.")
                return False
            
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[bold red]Error:[/bold red] No transcript found. Use 'transcribe' command first.")
                    return False
            
            # Initialize RAG components
            self._init_rag_components()
            
            # Check if vector store exists
            vectorstore = self.storage_manager.load_vectorstore(self.current_video_id)
            
            if vectorstore:
                console.print("[green]Loading existing vector store[/green]")
                self.rag_system.vectorstore = vectorstore
                self.rag_system.retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                self.rag_system.create_qa_chain()
            else:
                console.print("[yellow]No vector store found. Creating embeddings...[/yellow]")
                self.create_embeddings(for_rag=True)
            
            console.print("[green]RAG system ready[/green]")
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def ask_question(self, question: str) -> bool:
        """
        Ask a question about the video using RAG
        
        Args:
            question: Question to ask
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if RAG is set up
            if not self.rag_system or not self.rag_system.rag_chain:
                console.print("[yellow]RAG not set up. Setting up RAG...[/yellow]")
                if not self.setup_rag():
                    return False
            
            # Initialize query analyzer if needed
            if self.query_analyzer is None:
                self.query_analyzer = QueryAnalyzer(api_key=self.api_key)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Analyze and improve the query
                task = progress.add_task("[cyan]Analyzing question...[/cyan]", total=None)
                improved_question = self.query_analyzer.improve_query(question)
                progress.update(task, completed=True)
                
                # Get citation sources
                task = progress.add_task("[cyan]Finding relevant information...[/cyan]", total=None)
                citations = self.rag_system.get_citation_sources(improved_question)
                
                # Save citations
                if self.citation_manager:
                    self.citation_manager.add_citation(question, citations)
                    
                progress.update(task, completed=True)
                
                # Generate answer
                task = progress.add_task("[cyan]Generating answer...[/cyan]", total=None)
                answer = self.rag_system.answer_question(improved_question)
                progress.update(task, completed=True)
            
            # Display answer
            console.print("\n[bold cyan]Question:[/bold cyan]")
            console.print(question)
            
            console.print("\n[bold green]Answer:[/bold green]")
            console.print(Markdown(answer))
            
            # Display citations
            if citations and self.citation_manager:
                console.print("\n[bold]Sources:[/bold]")
                formatted_citations = self.citation_manager.format_citations(citations, "markdown")
                console.print(Markdown(formatted_citations))
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def interactive_chat(self) -> bool:
        """
        Start an interactive chat about the video
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if RAG is set up
            if not self.rag_system or not self.rag_system.rag_chain:
                console.print("[yellow]RAG not set up. Setting up RAG...[/yellow]")
                if not self.setup_rag():
                    return False
            
            # Initialize query analyzer if needed
            if self.query_analyzer is None:
                self.query_analyzer = QueryAnalyzer(api_key=self.api_key)
            
            console.print("\n[bold green]Starting Interactive Chat[/bold green]")
            console.print("Ask questions about the video content. Type 'exit', 'quit', or 'q' to end the chat.\n")
            
            while True:
                try:
                    # Get user input
                    user_question = Prompt.ask("[bold cyan]Your question[/bold cyan]")
                    
                    # Check for exit command
                    if user_question.lower() in ['exit', 'quit', 'q']:
                        break
                    
                    # Process the question
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        TimeElapsedColumn(),
                        console=console
                    ) as progress:
                        # Analyze and improve the query
                        task = progress.add_task("[cyan]Analyzing question...[/cyan]", total=None)
                        improved_question = self.query_analyzer.improve_query(user_question)
                        progress.update(task, completed=True)
                        
                        # Get citation sources
                        task = progress.add_task("[cyan]Finding relevant information...[/cyan]", total=None)
                        citations = self.rag_system.get_citation_sources(improved_question)
                        
                        # Save citations
                        if self.citation_manager:
                            self.citation_manager.add_citation(user_question, citations)
                            
                        progress.update(task, completed=True)
                        
                        # Generate answer
                        task = progress.add_task("[cyan]Generating answer...[/cyan]", total=None)
                        answer = self.rag_system.answer_question(improved_question)
                        progress.update(task, completed=True)
                    
                    # Display answer
                    console.print("\n[bold green]Answer:[/bold green]")
                    console.print(Markdown(answer))
                    
                    # Display citations
                    if citations and self.citation_manager:
                        console.print("\n[bold]Sources:[/bold]")
                        formatted_citations = self.citation_manager.format_citations(citations, "markdown")
                        console.print(Markdown(formatted_citations))
                    
                    console.print("\n" + "-" * 50 + "\n")
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[bold red]Error:[/bold red] {str(e)}")
            
            console.print("[bold green]Chat session ended[/bold green]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def text_to_speech(self, text_type: str = "summary") -> bool:
        """
        Convert text to speech
        
        Args:
            text_type: Type of text to convert (summary or transcript)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[bold red]Error:[/bold red] No video selected. Use 'process' command first.")
                return False
            
            # Get text based on type
            if text_type == "summary":
                if not self.current_summary:
                    # Try to load summary
                    self.current_summary = self.storage_manager.load_summary("default", self.current_video_id)
                    
                    if not self.current_summary:
                        console.print("[bold red]Error:[/bold red] No summary found. Use 'summarize' command first.")
                        return False
                
                text = self.current_summary
                
            elif text_type == "transcript":
                if not self.current_transcript:
                    # Try to load transcript
                    self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                    
                    if not self.current_transcript:
                        console.print("[bold red]Error:[/bold red] No transcript found. Use 'transcribe' command first.")
                        return False
                
                text = self.current_transcript
                
            else:
                console.print(f"[bold red]Error:[/bold red] Invalid text type: {text_type}")
                return False
            
            # Create output directory
            output_dir = Path("data/tts") / self.current_video_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Generate audio segments
                task = progress.add_task("[cyan]Generating audio segments...[/cyan]", total=None)
                audio_files = self.tts_generator.generate_audio_segments(text, 1000, output_dir)
                progress.update(task, completed=True, description=f"[green]Generated {len(audio_files)} audio segments[/green]")
                
                # Combine audio segments
                task = progress.add_task("[cyan]Combining audio segments...[/cyan]", total=None)
                output_file = output_dir / f"{self.current_video_id}_{text_type}.mp3"
                combined_path = self.tts_generator.combine_audio_files(audio_files, output_file)
                progress.update(task, completed=True, description="[green]Audio combined[/green]")
            
            console.print(f"[green]Audio saved to {output_file}[/green]")
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def show_transcript(self) -> bool:
        """
        Display the current transcript
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if transcript exists
            if not self.current_transcript:
                # Try to load transcript
                self.current_transcript = self.storage_manager.load_transcript(self.current_video_id)
                
                if not self.current_transcript:
                    console.print("[bold red]Error:[/bold red] No transcript found. Use 'transcribe' command first.")
                    return False
            
            # Display transcript
            console.print("\n[bold]Transcript:[/bold]")
            console.print(Panel(self.current_transcript, width=100, expand=False))
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def show_summary(self, summary_type: str = "default") -> bool:
        """
        Display the current summary
        
        Args:
            summary_type: Type of summary to show
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load summary if needed
            summary = self.storage_manager.load_summary(summary_type, self.current_video_id)
            
            if not summary:
                console.print(f"[bold red]Error:[/bold red] No {summary_type} summary found. Use 'summarize --type={summary_type}' command first.")
                return False
            
            # Display summary
            self._display_summary(summary_type, summary)
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def show_video_info(self) -> bool:
        """
        Display information about the current video
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if video info exists
            if not self.current_video_info:
                # Try to load video info
                self.current_video_info = self.storage_manager.load_video_info(self.current_video_id)
                
                if not self.current_video_info:
                    console.print("[bold red]Error:[/bold red] No video info found. Use 'process' command first.")
                    return False
            
            # Display video info
            self._display_video_info()
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def cleanup_files(self) -> bool:
        """
        Delete all files for the current video
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if there is a current video
            if not self.current_video_id:
                console.print("[bold red]Error:[/bold red] No video selected. Use 'process' command first.")
                return False
            
            # Ask for confirmation
            if not Confirm.ask(f"Are you sure you want to delete all files for video {self.current_video_id}?"):
                console.print("[yellow]Cleanup canceled[/yellow]")
                return False
            
            # Delete files
            self.storage_manager.cleanup(self.current_video_id)
            
            # Reset current state
            self.current_transcript = None
            self.current_summary = None
            
            console.print("[green]Cleanup completed[/green]")
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def _display_video_info(self) -> None:
        """Display information about the current video"""
        if not self.current_video_info:
            return
            
        # Create a table
        table = Table(title="Video Information", box=box.ROUNDED)
        
        # Add columns
        table.add_column("Property", style="cyan")
        table.add_column("Value")
        
        # Add rows
        table.add_row("Title", self.current_video_info.get("title", "Unknown"))
        table.add_row("Author", self.current_video_info.get("author", "Unknown"))
        table.add_row("Video ID", self.current_video_info.get("id", "Unknown"))
        
        # Format duration
        duration = self.current_video_info.get("length", 0)
        minutes = duration // 60
        seconds = duration % 60
        table.add_row("Duration", f"{minutes}m {seconds}s")
        
        table.add_row("Views", f"{self.current_video_info.get('views', 0):,}")
        table.add_row("Publish Date", self.current_video_info.get("publish_date", "Unknown"))
        
        # Add URL
        table.add_row("URL", self.current_video_url or "Unknown")
        
        # Print the table
        console.print(table)
        
        # Print description
        description = self.current_video_info.get("description", "")
        if description:
            console.print("\n[bold]Description:[/bold]")
            console.print(Panel(description[:500] + ("..." if len(description) > 500 else ""), 
                               width=100, expand=False))
    
    def _display_summary(self, summary_type: str = "default", summary: Optional[str] = None) -> None:
        """
        Display a summary
        
        Args:
            summary_type: Type of summary to display
            summary: Summary text (uses current_summary if None)
        """
        if summary is None:
            summary = self.current_summary
            
        if not summary:
            return
            
        # Format title based on summary type
        if summary_type == "concise":
            title = "Concise Summary"
        elif summary_type == "detailed":
            title = "Detailed Summary"
        elif summary_type == "bullet":
            title = "Bullet-Point Summary"
        elif summary_type == "sections":
            title = "Sectioned Summary"
        else:
            title = "Summary"
            
        # Display summary as markdown
        console.print(f"\n[bold]{title}:[/bold]")
        console.print(Markdown(summary))
    
    def show_help(self) -> None:
        """Display help information"""
        help_text = """
# VidSage Help

## Basic Commands

* `process <url>` - Download and process a YouTube video
* `transcribe` - Transcribe the audio of the current video
* `summarize [--type=<type>] [--gemini|--ollama]` - Generate a summary of the transcript
* `embed [--rag]` - Create embeddings for the transcript
* `rag` - Set up the RAG system for question answering
* `ask <question>` - Ask a question about the video content
* `chat` - Start an interactive chat about the video content
* `tts [--transcript|--summary]` - Convert text to speech

## Display Commands

* `show transcript` - Display the full transcript
* `show summary [--type=<type>]` - Display the summary
* `show info` - Show video information

## Other Commands

* `cleanup` - Delete all files for the current video
* `help` - Show this help message
* `exit` - Exit the application

## Summary Types

* `concise` - Brief 3-5 sentence summary
* `detailed` - Comprehensive summary (30% of original length)
* `bullet` - Bullet-point summary with key points
* `sections` - Summary organized by topics or themes
"""
        console.print(Markdown(help_text))
    
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
        Run a command
        
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
                    console.print("[bold red]Error:[/bold red] URL is required")
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
                    console.print("[bold red]Error:[/bold red] Question is required")
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
                
            elif cmd == "help":
                self.show_help()
                
            elif cmd in ["exit", "quit", "q"]:
                console.print("[bold green]Exiting VidSage. Goodbye![/bold green]")
                return False
                
            elif cmd:
                console.print(f"[bold red]Error:[/bold red] Unknown command: {cmd}")
                console.print("Type 'help' for available commands")
                
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return True
    
    def run(self) -> None:
        """Run the CLI interface"""
        # Display welcome message
        console.print(Panel.fit(
            "[bold blue]VidSage[/bold blue] - YouTube Video Analysis Tool",
            subtitle="Type 'help' for available commands"
        ))
        
        # Check API key
        if not self.api_key:
            console.print("[bold yellow]Warning:[/bold yellow] GOOGLE_API_KEY environment variable not found")
            console.print("Some features may be limited or unavailable")
        
        # Main loop
        while True:
            try:
                # Get user input
                command = self.session.prompt(
                    "VidSage> ",
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self.completer
                )
                
                # Run command
                if not self.run_command(command):
                    break
                    
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Use 'exit' to quit[/bold yellow]")
            except EOFError:
                console.print("\n[bold green]Exiting VidSage. Goodbye![/bold green]")
                break


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
