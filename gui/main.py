#!/usr/bin/env python3
"""
Simple VidSage GUI Application

A basic graphical interface for VidSage YouTube video analysis tool.
"""

import os
import sys
import traceback
import re
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QProgressBar,
    QTabWidget, QMessageBox, QSplitter, QFrame, QGroupBox,
    QFormLayout, QScrollArea, QComboBox, QCheckBox, QSpinBox,
    QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor
import markdown

# Import core modules
from core.youtube_processor import YouTubeProcessor
from core.transcriber import Transcriber
from core.summarizer import Summarizer
from core.rag_system import RAGSystem
from core.storage_manager import StorageManager
from utils.helpers import extract_video_id, is_youtube_url, load_api_key


class WorkerThread(QThread):
    """Simple worker thread for background tasks"""
    
    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(bool, str)  # Success, result/error
    
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.task(*self.args, **self.kwargs)
            self.finished.emit(True, str(result))
        except Exception as e:
            self.finished.emit(False, str(e))


class VidSageGUI(QMainWindow):
    """Simple VidSage GUI Main Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VidSage - YouTube Video Analysis")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables
        self.current_video_id = None
        self.current_video_info = {}
        self.current_transcript = ""
        self.current_summary = ""
        self.worker_thread = None
        self.conversation_history = []  # Store Q&A conversation history
        
        # Initialize core components
        self.youtube_processor = YouTubeProcessor()
        self.transcriber = Transcriber()
        self.summarizer = Summarizer()
        self.storage_manager = StorageManager()
        self.rag_system = None
        
        # Load API key
        self.api_key = load_api_key()
        
        self.setup_ui()
        self.setup_connections()
        
        # Load conversation history on startup
        self.refresh_conversation_history()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Input and Controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Content tabs
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes
        splitter.setSizes([400, 800])
    
    def create_left_panel(self):
        """Create left control panel"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("VidSage")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # URL Input Group
        url_group = QGroupBox("YouTube URL")
        url_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL...")
        url_layout.addWidget(self.url_input)
        
        self.process_btn = QPushButton("Process Video")
        self.process_btn.setEnabled(False)
        url_layout.addWidget(self.process_btn)
        
        layout.addWidget(url_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.transcribe_btn = QPushButton("Transcribe Video")
        self.transcribe_btn.setEnabled(False)
        actions_layout.addWidget(self.transcribe_btn)
        
        self.summarize_btn = QPushButton("Generate Summary")
        self.summarize_btn.setEnabled(False)
        actions_layout.addWidget(self.summarize_btn)
        
        self.setup_rag_btn = QPushButton("Setup Q&A System")
        self.setup_rag_btn.setEnabled(False)
        actions_layout.addWidget(self.setup_rag_btn)
        
        layout.addWidget(actions_group)
        
        # Q&A Group
        qa_group = QGroupBox("Ask Questions")
        qa_layout = QVBoxLayout(qa_group)
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask a question about the video...")
        self.question_input.setEnabled(False)
        qa_layout.addWidget(self.question_input)
        
        self.ask_btn = QPushButton("Ask Question")
        self.ask_btn.setEnabled(False)
        qa_layout.addWidget(self.ask_btn)
        
        layout.addWidget(qa_group)
        
        # Video History Group
        history_group = QGroupBox("Previous Videos")
        history_layout = QVBoxLayout(history_group)
        
        self.history_combo = QComboBox()
        self.history_combo.setEnabled(False)
        self.history_combo.addItem("No processed videos available")
        history_layout.addWidget(self.history_combo)
        
        history_buttons_layout = QHBoxLayout()
        
        self.load_history_btn = QPushButton("Load Video")
        self.load_history_btn.setEnabled(False)
        history_buttons_layout.addWidget(self.load_history_btn)
        
        self.refresh_history_btn = QPushButton("Refresh")
        self.refresh_history_btn.setEnabled(True)
        history_buttons_layout.addWidget(self.refresh_history_btn)
        
        history_layout.addLayout(history_buttons_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        return panel
    
    def create_right_panel(self):
        """Create right content panel"""
        self.tab_widget = QTabWidget()
        
        # Video Info Tab
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText("Video information will appear here...")
        self.tab_widget.addTab(self.info_text, "Video Info")
        
        # Transcript Tab
        self.transcript_text = QTextEdit()
        self.transcript_text.setReadOnly(True)
        self.transcript_text.setPlaceholderText("Video transcript will appear here...")
        self.tab_widget.addTab(self.transcript_text, "Transcript")
        
        # Summary Tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlaceholderText("Video summary will appear here...")
        self.tab_widget.addTab(self.summary_text, "Summary")
        
        # Q&A Tab - Use QTextBrowser for Markdown rendering
        self.qa_text = QTextBrowser()
        self.qa_text.setPlaceholderText("Q&A conversation will appear here...")
        self.qa_text.setOpenExternalLinks(True)  # Allow opening links
        
        # Set some basic CSS styling for better appearance
        self.qa_text.document().setDefaultStyleSheet("""
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                line-height: 1.6; 
                margin: 10px; 
                background-color: #ffffff;
            }
            h3 { 
                color: #2c3e50; 
                border-bottom: 2px solid #3498db; 
                padding-bottom: 5px; 
                margin-bottom: 15px;
            }
            h4 {
                color: #28a745;
                margin-top: 0;
                margin-bottom: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            strong { 
                color: #e74c3c; 
                font-weight: 600;
            }
            ul, ol { 
                margin-left: 20px; 
                padding-left: 10px;
            }
            li { 
                margin: 8px 0; 
                line-height: 1.5;
            }
            hr { 
                border: none; 
                border-top: 1px solid #bdc3c7; 
                margin: 20px 0; 
            }
            blockquote { 
                background-color: #f8f9fa; 
                border-left: 4px solid #3498db; 
                padding: 10px 20px; 
                margin: 10px 0; 
                font-style: italic;
            }
            p {
                margin: 8px 0;
                text-align: justify;
            }
            div {
                margin: 10px 0;
            }
            code {
                background-color: #f1f2f6;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                color: #e74c3c;
            }
        """)
        
        self.tab_widget.addTab(self.qa_text, "Q&A")
        
        return self.tab_widget
    
    def setup_connections(self):
        """Setup signal connections"""
        self.url_input.textChanged.connect(self.on_url_changed)
        self.process_btn.clicked.connect(self.process_video)
        self.transcribe_btn.clicked.connect(self.transcribe_video)
        self.summarize_btn.clicked.connect(self.summarize_video)
        self.setup_rag_btn.clicked.connect(self.setup_rag)
        self.ask_btn.clicked.connect(self.ask_question)
        self.question_input.returnPressed.connect(self.ask_question)
        self.load_history_btn.clicked.connect(self.load_conversation_history)
        self.refresh_history_btn.clicked.connect(self.refresh_conversation_history)
        self.history_combo.currentTextChanged.connect(self.on_history_selection_changed)
    
    def on_url_changed(self, text):
        """Handle URL input change"""
        url = text.strip()
        is_valid = bool(url and is_youtube_url(url))
        self.process_btn.setEnabled(is_valid)
        
        if not url:
            self.status_label.setText("")
        elif not is_valid and url:
            self.status_label.setText("Please enter a valid YouTube URL")
        else:
            self.status_label.setText("Ready to process")
    
    def show_progress(self, message):
        """Show progress"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText(message)
    
    def hide_progress(self):
        """Hide progress"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
    
    def process_video(self):
        """Process YouTube video"""
        url = self.url_input.text().strip()
        if not url or not is_youtube_url(url):
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid YouTube URL")
            return
        
        self.show_progress("Processing video...")
        self.process_btn.setEnabled(False)
        
        # Create worker thread
        self.worker_thread = WorkerThread(self._process_video_task, url)
        self.worker_thread.progress.connect(self.status_label.setText)
        self.worker_thread.finished.connect(self.on_video_processed)
        self.worker_thread.start()
    
    def _process_video_task(self, url):
        """Background task for processing video"""
        try:
            # Extract video ID
            video_id = extract_video_id(url)
            self.current_video_id = video_id
            
            # Get video info first
            video_info = self.youtube_processor.get_video_info(url, save_info=True)
            
            # Try to get transcript from subtitles first
            transcript = self.youtube_processor.get_transcript_from_subtitles(url)
            
            if transcript:
                # Save transcript and mark as available
                self.current_transcript = transcript
                self.storage_manager.save_transcript(video_id, transcript)
                result_message = f"Video processed successfully: {video_info.get('title', 'Unknown')} - Transcript loaded from subtitles!"
            else:
                # Download audio for transcription
                audio_path, _ = self.youtube_processor.download_audio(url)
                self.current_audio_path = audio_path
                result_message = f"Video processed successfully: {video_info.get('title', 'Unknown')} - Audio downloaded for transcription."
            
            self.current_video_info = video_info
            return result_message
                
        except Exception as e:
            raise Exception(f"Error processing video: {str(e)}")
    
    def on_video_processed(self, success, message):
        """Handle video processing completion"""
        self.hide_progress()
        self.process_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("Video processed successfully!")
            self.update_video_info()
            self.enable_actions()
            
            # If we have transcript from subtitles, update the transcript tab
            if self.current_transcript:
                self.transcript_text.setPlainText(self.current_transcript)
                self.tab_widget.setCurrentIndex(1)  # Switch to transcript tab
                # Enable Q&A setup since we have transcript
                self.setup_rag_btn.setEnabled(True)
            else:
                # Show video info tab if no transcript yet
                self.tab_widget.setCurrentIndex(0)
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def update_video_info(self):
        """Update video information display"""
        if not self.current_video_info:
            return
        
        info = self.current_video_info
        info_text = f"""
Title: {info.get('title', 'Unknown')}
Author: {info.get('author', 'Unknown')}
Duration: {info.get('length', 0)} seconds
Views: {info.get('views', 0):,}
Description: {info.get('description', 'No description')[:200]}...
        """.strip()
        
        self.info_text.setPlainText(info_text)
        self.tab_widget.setCurrentIndex(0)  # Switch to info tab
    
    def enable_actions(self):
        """Enable action buttons after video processing"""
        # Enable transcription only if we don't already have a transcript
        if not self.current_transcript:
            self.transcribe_btn.setEnabled(True)
        else:
            # If we already have transcript, we can skip transcription
            self.transcribe_btn.setText("Transcript Available")
            self.transcribe_btn.setEnabled(False)
        
        # Always enable summarization if we have transcript
        if self.current_transcript:
            self.summarize_btn.setEnabled(True)
            self.setup_rag_btn.setEnabled(True)
        else:
            self.summarize_btn.setEnabled(False)
    
    def transcribe_video(self):
        """Transcribe video"""
        if not self.current_video_id:
            QMessageBox.warning(self, "No Video", "Please process a video first")
            return
        
        self.show_progress("Transcribing video...")
        self.transcribe_btn.setEnabled(False)
        
        self.worker_thread = WorkerThread(self._transcribe_task)
        self.worker_thread.progress.connect(self.status_label.setText)
        self.worker_thread.finished.connect(self.on_transcription_finished)
        self.worker_thread.start()
    
    def _transcribe_task(self):
        """Background task for transcription"""
        try:
            # Check if we already have transcript from subtitles
            if self.current_transcript:
                return "Transcript already available from subtitles"
            
            # Check if audio file exists
            if not hasattr(self, 'current_audio_path') or not self.current_audio_path:
                return "No audio file available for transcription"
            
            # Transcribe using the correct method
            result = self.transcriber.transcribe_with_segments(self.current_audio_path)
            
            if result and 'text' in result:
                # Format transcript
                transcript_text = self.transcriber.format_transcript(result, include_timestamps=True)
                
                # Save transcript
                self.storage_manager.save_transcript(self.current_video_id, transcript_text)
                
                self.current_transcript = transcript_text
                return "Transcription completed successfully"
            else:
                return "Failed to transcribe video"
        except Exception as e:
            raise Exception(f"Error transcribing video: {str(e)}")
    
    def on_transcription_finished(self, success, message):
        """Handle transcription completion"""
        self.hide_progress()
        self.transcribe_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("Transcription completed!")
            self.transcript_text.setPlainText(self.current_transcript)
            self.tab_widget.setCurrentIndex(1)  # Switch to transcript tab
            self.setup_rag_btn.setEnabled(True)
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def summarize_video(self):
        """Generate video summary"""
        if not self.current_transcript:
            QMessageBox.warning(self, "No Transcript", "Please transcribe the video first")
            return
        
        self.show_progress("Generating summary...")
        self.summarize_btn.setEnabled(False)
        
        self.worker_thread = WorkerThread(self._summarize_task)
        self.worker_thread.progress.connect(self.status_label.setText)
        self.worker_thread.finished.connect(self.on_summary_finished)
        self.worker_thread.start()
    
    def _summarize_task(self):
        """Background task for summarization"""
        try:
            # Use the correct method name from the Summarizer class
            summary = self.summarizer.summarize(
                transcript=self.current_transcript, 
                summary_type="default",
                engine="gemini",
                stream=False
            )
            if summary:
                self.current_summary = summary
                # Save summary using storage manager with correct parameter order
                self.storage_manager.save_summary(summary, "default", self.current_video_id)
                return "Summary generated successfully"
            else:
                return "Failed to generate summary"
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def on_summary_finished(self, success, message):
        """Handle summary completion"""
        self.hide_progress()
        self.summarize_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("Summary generated!")
            self.summary_text.setPlainText(self.current_summary)
            self.tab_widget.setCurrentIndex(2)  # Switch to summary tab
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def setup_rag(self):
        """Setup RAG system for Q&A"""
        if not self.current_transcript:
            QMessageBox.warning(self, "No Transcript", "Please transcribe the video first")
            return
        
        self.show_progress("Setting up Q&A system...")
        self.setup_rag_btn.setEnabled(False)
        
        self.worker_thread = WorkerThread(self._setup_rag_task)
        self.worker_thread.progress.connect(self.status_label.setText)
        self.worker_thread.finished.connect(self.on_rag_setup_finished)
        self.worker_thread.start()
    
    def _setup_rag_task(self):
        """Background task for RAG setup"""
        try:
            # Initialize RAG system
            self.rag_system = RAGSystem(api_key=self.api_key)
            
            # Process transcript into chunks
            docs = self.rag_system.process_transcript(self.current_transcript)
            
            # Create vector store with persistence
            persist_dir = f"gui/data/vectorstores/{self.current_video_id}/chroma_db"
            self.rag_system.create_vectorstore(docs, persist_directory=persist_dir)
            
            # Create QA chain
            self.rag_system.create_qa_chain()
            
            return "Q&A system ready"
        except Exception as e:
            raise Exception(f"Error setting up Q&A: {str(e)}")
    
    def on_rag_setup_finished(self, success, message):
        """Handle RAG setup completion"""
        self.hide_progress()
        self.setup_rag_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("Q&A system ready!")
            self.question_input.setEnabled(True)
            self.ask_btn.setEnabled(True)
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def ask_question(self):
        """Ask a question about the video"""
        question = self.question_input.text().strip()
        if not question:
            return
        
        if not self.rag_system or not hasattr(self.rag_system, 'rag_chain') or not self.rag_system.rag_chain:
            QMessageBox.warning(self, "Q&A Not Ready", "Please setup the Q&A system first")
            return
        
        self.show_progress("Getting answer...")
        self.ask_btn.setEnabled(False)
        
        self.worker_thread = WorkerThread(self._ask_question_task, question)
        self.worker_thread.progress.connect(self.status_label.setText)
        self.worker_thread.finished.connect(self.on_question_answered)
        self.worker_thread.start()
    
    def _ask_question_task(self, question):
        """Background task for asking question"""
        try:
            # Use the correct method from RAG system
            response = self.rag_system.answer_question(question)
            
            # Format the response in a more human-readable way
            formatted_response = self._format_qa_response(question, response)
            return formatted_response
        except Exception as e:
            raise Exception(f"Error getting answer: {str(e)}")
    
    def _format_qa_response(self, question, response, timestamp=None):
        """Format Q&A response for better readability with improved styling"""
        import re
        
        # Clean up the response text
        cleaned_response = response.strip()
        
        # Create timestamp string if provided
        time_info = ""
        if timestamp:
            time_info = f"<p style='color: #6c757d; font-size: 12px; margin: 5px 0;'><em>Asked on: {timestamp}</em></p>"
        
        # Parse and format the response content
        formatted_content = self._parse_and_format_answer(cleaned_response)
        
        # Create the formatted response with modern card-like styling
        html_response = f"""
<div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
           padding: 16px; 
           border-radius: 12px; 
           margin: 15px 0; 
           box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);">
    <div style="display: flex; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 20px; margin-right: 8px;">❓</span>
        <h3 style="margin: 0; color: #ffffff; font-size: 16px; font-weight: 600;">{question}</h3>
    </div>
    {time_info}
</div>

<div style="background: #f8f9fa; 
           padding: 20px; 
           border-left: 5px solid #28a745; 
           margin: 15px 0; 
           border-radius: 8px;
           box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <div style="display: flex; align-items: center; margin-bottom: 12px;">
        <span style="font-size: 18px; margin-right: 8px;">💡</span>
        <h4 style="color: #28a745; margin: 0; font-size: 16px; font-weight: 600;">Answer</h4>
    </div>
    <div style="color: #2c3e50; line-height: 1.6;">
        {formatted_content}
    </div>
</div>

<hr style="border: none; 
          height: 3px; 
          background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); 
          margin: 25px 0; 
          border-radius: 2px;">

"""
        return html_response
    
    def _parse_and_format_answer(self, answer_text):
        """Parse and format the answer content with better structure"""
        import re
        
        # Clean up the text
        text = answer_text.strip()
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        formatted_content = ""
        
        for paragraph in paragraphs:
            # Check if it's a header (contains only caps and common words)
            if self._is_likely_header(paragraph):
                formatted_content += f"<h5 style='color: #2c3e50; font-weight: 600; margin: 16px 0 8px 0; font-size: 15px;'>{paragraph}</h5>"
            
            # Check if it's a list item
            elif paragraph.startswith('- ') or paragraph.startswith('• '):
                list_items = [item.strip() for item in paragraph.split('\n') if item.strip()]
                formatted_content += "<ul style='margin: 8px 0; padding-left: 20px;'>"
                for item in list_items:
                    clean_item = item.lstrip('- •').strip()
                    formatted_content += f"<li style='margin: 4px 0; line-height: 1.5;'>{clean_item}</li>"
                formatted_content += "</ul>"
            
            # Check if it contains timestamp references like [00:00]
            elif '[' in paragraph and ']' in paragraph:
                # Format timestamp references
                formatted_paragraph = re.sub(
                    r'\[(\d{2}:\d{2})\]', 
                    r'<span style="background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 500;">[⏱️ \1]</span>', 
                    paragraph
                )
                formatted_content += f"<p style='margin: 8px 0; text-align: justify;'>{formatted_paragraph}</p>"
            
            # Regular paragraph
            else:
                formatted_content += f"<p style='margin: 8px 0; text-align: justify;'>{paragraph}</p>"
        
        return formatted_content
    
    def _is_likely_header(self, text):
        """Check if text is likely a header/title"""
        # Simple heuristic: short text, mostly uppercase, or contains keywords
        header_keywords = ['main', 'key', 'important', 'summary', 'overview', 'conclusion', 'introduction']
        
        if len(text) < 60 and (
            text.isupper() or 
            any(keyword in text.lower() for keyword in header_keywords) or
            text.count(' ') < 4
        ):
            return True
        return False
    
    def on_question_answered(self, success, result):
        """Handle question answer completion"""
        self.hide_progress()
        self.ask_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("Answer received!")
            
            # Extract question and clean answer for history
            question = self.question_input.text().strip()
            
            # Extract the clean answer from the response
            # The result contains HTML formatted content, we need to extract just the text
            import re
            from html import unescape
            
            # Remove HTML tags and get clean text
            clean_answer = re.sub(r'<[^>]+>', '', result)
            clean_answer = unescape(clean_answer).strip()
            
            # Find the answer section by looking for "Answer" keyword
            if "Answer" in clean_answer:
                answer_start = clean_answer.find("Answer")
                if answer_start != -1:
                    # Get everything after "Answer"
                    clean_answer = clean_answer[answer_start + 6:].strip()
                    # Remove any leading colons or whitespace
                    clean_answer = clean_answer.lstrip(': \n').strip()
            
            # Add to conversation history with clean answer
            if question and clean_answer:
                self.add_to_conversation_history(question, clean_answer)
            
            # Get current content and append new result
            current_html = self.qa_text.toHtml()
            
            # The result is already HTML formatted, so we don't need to convert it
            result_html = result
            
            # Append the new content
            if current_html.strip() and not current_html.strip().endswith('</body></html>'):
                # If there's existing content, append to it
                new_html = current_html + result_html
            else:
                # First question, set initial content
                new_html = result_html
            
            self.qa_text.setHtml(new_html)
            
            # Scroll to bottom
            cursor = self.qa_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.qa_text.setTextCursor(cursor)
            
            self.tab_widget.setCurrentIndex(3)  # Switch to Q&A tab
            self.question_input.clear()
        else:
            self.status_label.setText(f"Error: {result}")
            QMessageBox.critical(self, "Error", result)
    
    def refresh_conversation_history(self):
        """Refresh the conversation history dropdown with all processed videos"""
        try:
            # Get list of all processed videos
            processed_videos = self.storage_manager.list_processed_videos()
            
            # Clear the combo box
            self.history_combo.clear()
            
            # Add all processed videos to the dropdown
            videos_with_data = []
            for video_id in processed_videos:
                # Get video info to display title
                video_info = self.storage_manager.load_video_info(video_id)
                if video_info:
                    title = video_info.get('title', 'Unknown Video')
                    # Truncate title if too long
                    if len(title) > 50:
                        title = title[:47] + "..."
                    
                    # Check what data is available for this video
                    has_transcript = self.storage_manager.has_transcript(video_id)
                    has_summary = self.storage_manager.has_summary(video_id=video_id)
                    has_conversation = self.storage_manager.has_conversation(video_id)
                    has_vectorstore = self.storage_manager.has_vectorstore(video_id)
                    
                    # Create status indicators
                    status_indicators = []
                    if has_transcript:
                        status_indicators.append("📝")
                    if has_summary:
                        status_indicators.append("📋")
                    if has_vectorstore:
                        status_indicators.append("🔍")
                    if has_conversation:
                        status_indicators.append("💬")
                    
                    status_text = " ".join(status_indicators) if status_indicators else "⭕"
                    display_text = f"{status_text} {title} ({video_id})"
                    videos_with_data.append((display_text, video_id))
            
            if videos_with_data:
                self.history_combo.addItem("Select a video to load...")
                for display_text, video_id in videos_with_data:
                    self.history_combo.addItem(display_text)
                
                # Store video IDs for later reference
                self.conversation_video_ids = [video_id for _, video_id in videos_with_data]
                self.history_combo.setEnabled(True)
            else:
                self.history_combo.addItem("No processed videos available")
                self.conversation_video_ids = []
                self.history_combo.setEnabled(False)
                
            self.load_history_btn.setEnabled(False)
                
        except Exception as e:
            self.status_label.setText(f"Error loading video history: {str(e)}")
    
    def on_history_selection_changed(self, text):
        """Handle conversation history selection change"""
        if hasattr(self, 'conversation_video_ids') and self.conversation_video_ids:
            current_index = self.history_combo.currentIndex()
            if current_index > 0:  # Skip the "Select a video..." item
                self.load_history_btn.setEnabled(True)
            else:
                self.load_history_btn.setEnabled(False)
        else:
            self.load_history_btn.setEnabled(False)
    
    def load_conversation_history(self):
        """Load and display a selected video with all its available data"""
        try:
            current_index = self.history_combo.currentIndex()
            if current_index <= 0 or not hasattr(self, 'conversation_video_ids'):
                return
            
            # Get the selected video ID
            video_id = self.conversation_video_ids[current_index - 1]
            
            # Load all available data for this video
            video_info = self.storage_manager.load_video_info(video_id)
            transcript = self.storage_manager.load_transcript(video_id)
            summary = self.storage_manager.load_summary(video_id=video_id)
            conversation = self.storage_manager.load_conversation(video_id)
            
            # Set current video data
            self.current_video_id = video_id
            self.current_video_info = video_info or {}
            self.current_transcript = transcript or ""
            self.current_summary = summary or ""
            self.conversation_history = conversation or []
            
            # Update URL input if available
            if video_info and 'webpage_url' in video_info:
                self.url_input.setText(video_info['webpage_url'])
            elif video_info and 'id' in video_info:
                # Construct YouTube URL from video ID
                self.url_input.setText(f"https://www.youtube.com/watch?v={video_info['id']}")
            
            # Update all tabs with available data
            self.update_video_info()
            
            if transcript:
                self.transcript_text.setPlainText(transcript)
                self.status_label.setText("Transcript loaded")
            else:
                self.transcript_text.setPlainText("No transcript available for this video")
            
            if summary:
                self.summary_text.setPlainText(summary)
                self.status_label.setText("Summary loaded")
            else:
                self.summary_text.setPlainText("No summary available for this video")
            
            # Load conversation if available
            if conversation:
                self.display_conversation_history()
                self.tab_widget.setCurrentIndex(3)  # Switch to Q&A tab
                self.status_label.setText("Conversation history loaded")
            else:
                self.qa_text.setPlainText("No conversation history available for this video")
                self.tab_widget.setCurrentIndex(0)  # Switch to video info tab
            
            # Enable appropriate buttons based on available data
            self.enable_actions_for_loaded_video()
            
            # Show status message
            title = video_info.get('title', 'Unknown Video') if video_info else 'Unknown Video'
            self.status_label.setText(f"Loaded data for: {title}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading video data: {str(e)}")
            self.status_label.setText(f"Error loading video data: {str(e)}")
    
    def display_conversation_history(self):
        """Display the loaded conversation history in the Q&A tab"""
        if not self.conversation_history:
            return
        
        # Build HTML content from conversation history
        html_content = ""
        
        for entry in self.conversation_history:
            question = entry.get('question', '')
            answer = entry.get('answer', '')
            timestamp = entry.get('timestamp', 0)
            
            # Convert timestamp to readable format
            try:
                from datetime import datetime
                dt = datetime.fromtimestamp(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = "Unknown time"
            
            # Format as HTML directly using the improved styling
            formatted_qa = self._format_qa_response(question, answer, time_str)
            html_content += formatted_qa
        
        # Set the content
        self.qa_text.setHtml(html_content)
    
    def enable_actions_for_loaded_video(self):
        """Enable appropriate action buttons for loaded video"""
        # Enable process button to allow reprocessing if needed
        self.process_btn.setEnabled(True)
        
        # Set transcription button state
        if self.current_transcript:
            self.transcribe_btn.setText("Transcript Available")
            self.transcribe_btn.setEnabled(False)
            self.summarize_btn.setEnabled(True)
        else:
            self.transcribe_btn.setText("Transcribe Video")
            self.transcribe_btn.setEnabled(True)
            self.summarize_btn.setEnabled(False)
        
        # Enable RAG setup if we have transcript
        if self.current_transcript:
            self.setup_rag_btn.setEnabled(True)
            
            # Try to setup RAG system automatically
            if self.storage_manager.has_vectorstore(self.current_video_id):
                self.setup_rag_system_for_loaded_video()
            else:
                # Reset button text if no vectorstore exists
                self.setup_rag_btn.setText("Setup Q&A System")
                self.question_input.setEnabled(False)
                self.ask_btn.setEnabled(False)
        else:
            self.setup_rag_btn.setEnabled(False)
            self.question_input.setEnabled(False)
            self.ask_btn.setEnabled(False)
        
    def setup_rag_system_for_loaded_video(self):
        """Setup RAG system for a loaded video with existing vectorstore"""
        try:
            # Initialize RAG system
            self.rag_system = RAGSystem(api_key=self.api_key)
            
            # Load existing vectorstore
            persist_dir = self.storage_manager.vectorstore_dir / self.current_video_id / "chroma_db"
            if persist_dir.exists():
                self.rag_system.load_vectorstore(str(persist_dir))
                self.rag_system.create_qa_chain()
                
                # Enable Q&A
                self.question_input.setEnabled(True)
                self.ask_btn.setEnabled(True)
                self.setup_rag_btn.setText("Q&A System Ready")
                self.setup_rag_btn.setEnabled(False)
                
                self.status_label.setText("Q&A system loaded successfully!")
            
        except Exception as e:
            self.status_label.setText(f"Error setting up Q&A system: {str(e)}")
    
    def save_current_conversation(self):
        """Save the current conversation history"""
        if self.current_video_id and self.conversation_history:
            try:
                self.storage_manager.save_conversation(self.current_video_id, self.conversation_history)
            except Exception as e:
                self.status_label.setText(f"Error saving conversation: {str(e)}")
    
    def add_to_conversation_history(self, question: str, answer: str):
        """Add a new Q&A to the conversation history"""
        from datetime import datetime
        
        entry = {
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().timestamp()
        }
        
        self.conversation_history.append(entry)
        self.save_current_conversation()
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
        event.accept()


def main():
    """Main function to run the GUI"""
    app = QApplication(sys.argv)
    app.setApplicationName("VidSage")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = VidSageGUI()
    window.show()
    
    # Run the application
    try:
        sys.exit(app.exec())
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
