from PyQt6.QtCore import QThread, pyqtSignal
from typing import Dict, Any, Optional
from core.youtube_processor import YouTubeProcessor
from core.summarizer import Summarizer
from core.rag_system import RAGSystem
import traceback
import os

class WorkerThread(QThread):
    finished = pyqtSignal(dict)  # Signal emits Dict[str, Any] with type and data
    error = pyqtSignal(str)     # Signal emits error message
    progress = pyqtSignal(int, str)  # Signal emits (progress %, status message)

    def __init__(self, task_type: str, data_dir: str = "Apps/gui/data", *, 
                 url: Optional[str] = None, question: Optional[str] = None):
        """Initialize the worker thread
        
        Args:
            task_type: Type of task ("analyze", "summarize", or "ask")
            data_dir: Directory for storing data files
            url: YouTube video URL
            question: Question for Q&A task
        """
        super().__init__()
        self.task_type = task_type
        self.url = url
        self.question = question
        self.youtube_processor = YouTubeProcessor(data_dir=data_dir)
        self.summarizer = Summarizer()
        self.rag_system = RAGSystem()
        self.should_stop = False

    def stop(self) -> None:
        """Signal the worker to stop gracefully"""
        self.should_stop = True
        self.wait()  # Wait for the thread to finish

    def run(self) -> None:
        """Main thread execution"""
        try:
            if self.task_type == "analyze":
                self._run_analyze()
            elif self.task_type == "summarize":
                self._run_summarize()
            elif self.task_type == "ask":
                self._run_ask()
        except Exception as e:
            self.error.emit(f"{str(e)}\n{traceback.format_exc()}")

    def _run_analyze(self) -> None:
        """Handle video analysis"""
        if not self.url:
            raise ValueError("URL is required for analysis")
            
        try:
            self.progress.emit(10, "Fetching video information...")
            info = self.youtube_processor.get_video_info(self.url,True)
            if self.should_stop:
                return
                
            self.progress.emit(30, "Downloading thumbnail...")
            try:
                thumb_path, _ = self.youtube_processor.download_thumbnail(self.url)
                if not os.path.exists(thumb_path):
                    print(f"Warning: Thumbnail not found at {thumb_path}")
            except Exception as e:
                print(f"Warning: Could not download thumbnail: {str(e)}")
                
            if self.should_stop:
                return
                
            self.progress.emit(60, "Extracting subtitles...")
            try:
                self.youtube_processor.extract_subtitles_from_info(self.url, str(info.get('id', '')))
            except Exception as e:
                print(f"Warning: Could not extract subtitles: {str(e)}")
            
            self.progress.emit(90, "Finalizing...")
            self.finished.emit({"type": "analyze", "data": info})
            
        except Exception as e:
            self.error.emit(f"Failed to fetch video info:\n{str(e)}\n{traceback.format_exc()}")

    def _run_summarize(self) -> None:
        """Handle video summarization"""
        if not self.url:
            raise ValueError("URL is required for summarization")
            
        try:
            self.progress.emit(20, "Getting transcript...")
            # video info info
            info = self.youtube_processor.get_video_info(self.url)
            
            if not info:
                raise ValueError("No video info found for the provided URL")
            
            # Get transcript
            transcript = self.youtube_processor.get_transcript_from_subtitles(self.url)
            if not transcript:
                raise Exception("No transcript/subtitles found for this video.")
            if self.should_stop:
                return
                
            self.progress.emit(60, "Generating summary...")
            summary = self.summarizer.summarize(transcript, summary_type="default", engine="gemini")
            if self.should_stop:
                return
                
            self.progress.emit(90, "Formatting summary...")
            self.finished.emit({"type": "summarize", "data": summary})
            
        except Exception as e:
            self.error.emit(f"Failed to generate summary:\n{str(e)}\n{traceback.format_exc()}")

    def _run_ask(self) -> None:
        """Handle Q&A processing"""
        if not self.url or not self.question:
            raise ValueError("URL and question are required for Q&A")
            
        try:
            self.progress.emit(20, "Getting transcript...")
            transcript = self.youtube_processor.get_transcript_from_subtitles(self.url)
            if not transcript:
                raise Exception("No transcript/subtitles found for this video.")
            if self.should_stop:
                return
                
            self.progress.emit(40, "Processing transcript...")
            video_id = self.youtube_processor.extract_video_id(self.url)
            persist_dir = f"Apps/gui/data/vectorstores/{video_id}/chroma_db"
            docs = self.rag_system.process_transcript(transcript)
            if self.should_stop:
                return
                
            self.progress.emit(60, "Creating vector store...")
            self.rag_system.create_vectorstore(docs, persist_directory=persist_dir)
            if self.should_stop:
                return
                
            self.progress.emit(80, "Generating answer...")
            self.rag_system.create_qa_chain()
            answer = self.rag_system.answer_question(self.question)
            
            self.progress.emit(90, "Formatting response...")
            self.finished.emit({"type": "ask", "data": answer})
            
        except Exception as e:
            self.error.emit(f"Failed to answer question:\n{str(e)}\n{traceback.format_exc()}")
