# HomeTab for YT Insight AI
from typing import Optional, Dict, Any, TypeVar, cast
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTabWidget, QProgressBar, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QPixmap
from workers import WorkerThread
import re
import os
from markdown import markdown

ResultDict = Dict[str, Any]

class HomeTab(QWidget):
    def __init__(self):
        """Initialize the HomeTab"""
        super().__init__()
        self._build_ui()
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        self.ask_btn.clicked.connect(self.on_ask_clicked)
        self.summary_btn.clicked.connect(self.on_summary_clicked)
        self.current_worker: Optional[WorkerThread] = None
        self.current_video_id: Optional[str] = None

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        # URL Input
        url_row = QHBoxLayout()
        url_label = QLabel("🔗 YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste URL here…")
        self.analyze_btn = QPushButton("Fetch + Analyze")
        url_row.addWidget(url_label)
        url_row.addWidget(self.url_input)
        url_row.addWidget(self.analyze_btn)
        layout.addLayout(url_row)

        # Video Info Card
        self.info_card = QGroupBox("Video Info")
        info_layout = QHBoxLayout()
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(120, 68)
        self.title = QLabel("Title: -")
        self.duration = QLabel("Duration: -")
        self.channel = QLabel("Channel: -")
        info_texts = QVBoxLayout()
        info_texts.addWidget(self.title)
        info_texts.addWidget(self.duration)
        info_texts.addWidget(self.channel)
        info_layout.addWidget(self.thumbnail)
        info_layout.addLayout(info_texts)
        self.info_card.setLayout(info_layout)
        layout.addWidget(self.info_card)
        self.info_card.setVisible(False)

        # Progress Bar and Status
        progress_layout = QVBoxLayout()
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.progress)
        progress_layout.addWidget(self.status_label)
        layout.addLayout(progress_layout)

        # Summary Button
        self.summary_btn = QPushButton("Generate Summary")
        self.summary_btn.setEnabled(False)
        self.summary_btn.clicked.connect(self.on_summary_clicked)
        layout.addWidget(self.summary_btn)

        # Tabs for Summary & Q&A
        self.result_tabs = QTabWidget()
        self.summary_tab = QWidget()
        self.qa_tab = QWidget()
        self.result_tabs.addTab(self.summary_tab, "📋 Summary")
        self.result_tabs.addTab(self.qa_tab, "❓ Q&A")
        layout.addWidget(self.result_tabs)
        self.result_tabs.setVisible(False)

        # --- Summary Tab Layout ---
        summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        self.summary_box.setPlaceholderText("Summary will appear here…")
        summary_layout.addWidget(self.summary_box)

        # --- Q&A Tab Layout ---
        qa_layout = QVBoxLayout(self.qa_tab)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlaceholderText("Chat about the video…")
        self.chat_area.setAcceptRichText(True)
        qa_layout.addWidget(self.chat_area)
        
        ask_row = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask a question…")
        self.ask_btn = QPushButton("Ask")
        ask_row.addWidget(self.question_input)
        ask_row.addWidget(self.ask_btn)
        qa_layout.addLayout(ask_row)

    def _on_progress(self, value: int, status: str) -> None:
        """Update progress bar and status label"""
        self.progress.setValue(value)
        self.status_label.setText(status)
        self.status_label.repaint()

    def _on_analyze_finished(self, result: ResultDict) -> None:
        """Handle completed video analysis"""
        if result["type"] == "analyze":
            info = result["data"]
            self.current_video_id = str(info.get('id', ''))
            
            # Update video info
            self.title.setText(f"Title: {info.get('title', '-')}")
            duration_sec = info.get('length', '-')
            if isinstance(duration_sec, int):
                mins = duration_sec // 60
                secs = duration_sec % 60
                self.duration.setText(f"Duration: {mins}m {secs:02d}s")
            else:
                self.duration.setText(f"Duration: {duration_sec}")
            self.channel.setText(f"Channel: {info.get('author', '-')}")

            # Try to load thumbnail
            thumb_path = os.path.join("Apps/gui/data/thumbnails", f"{self.current_video_id}.jpg")
            if os.path.exists(thumb_path):
                pixmap = QPixmap(thumb_path)
                self.thumbnail.setPixmap(pixmap.scaled(
                    self.thumbnail.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.thumbnail.clear()

            # Show UI elements
            self.info_card.setVisible(True)
            self.result_tabs.setVisible(True)
            self.summary_btn.setEnabled(True)

        # Reset UI state
        self._reset_ui_state()

    def _on_summary_finished(self, result: ResultDict) -> None:
        """Handle completed summarization"""
        if result["type"] == "summarize":
            summary = str(result["data"])
            self.summary_box.setMarkdown(summary)
            self.result_tabs.setCurrentWidget(self.summary_tab)
        self._reset_ui_state()

    def _on_ask_finished(self, result: ResultDict) -> None:
        """Handle completed Q&A with consistent styling"""
        if result["type"] == "ask":
            answer = str(result["data"])
            question = self.question_input.text()
            
            # Format Q&A with consistent styling
            user_html = (
                "<div class='qa-card user-turn' style='margin-bottom:2px;'>"
                "<span style='color:#007acc;font-weight:bold;'>You:</span> "
                f"<span style='color:#23272f;font-size:1.08em;'>{question}</span>"
                "</div>"
            )
            ai_html = self.clean_and_format_answer(answer)
            
            # Add to chat with proper margins
            self.chat_area.append(
                "<div style='margin:0 0 18px 0; padding:0;'>"
                f"{user_html}"
                f"{ai_html}"
                "</div>"
            )
            self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
            self.question_input.clear()
            
        self._reset_ui_state()

    def _on_worker_error(self, error_msg: str) -> None:
        """Handle worker errors"""
        QMessageBox.critical(self, "Error", f"An error occurred: {error_msg}")
        self._reset_ui_state()

    def _reset_ui_state(self) -> None:
        """Reset UI elements to their default state"""
        self.analyze_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        self.ask_btn.setEnabled(True)
        self.question_input.setEnabled(True)
        self.summary_btn.setEnabled(True)
        self.progress.setVisible(False)
        self.status_label.clear()

    def clean_and_format_answer(self, answer: str) -> str:
        """Clean and format answer text with consistent styling
        
        Args:
            answer: Raw answer text
            
        Returns:
            Formatted HTML string with qa-card styling
        """
        # Remove timestamps
        answer = re.sub(r'\[\d{1,2}:\d{2}\]', '', answer)
        # Convert markdown to HTML
        html = markdown(answer, extensions=['extra', 'sane_lists'])
        # Format with consistent qa-card styling
        return (
            "<div class='qa-card ai-turn' style='margin-bottom:2px;'>"
            "<span style='color:#10a37f;font-weight:bold;'>Assistant:</span> "
            f"<span style='color:#23272f;font-size:1.08em;'>{html}</span>"
            "</div>"
        )

    def on_analyze_clicked(self) -> None:
        """Handle analyze button click"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return

        # Stop any running worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()

        # Disable UI elements
        self.analyze_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.summary_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # Create and start worker thread
        self.current_worker = WorkerThread(task_type="analyze", url=url)
        self.current_worker.finished.connect(self._on_analyze_finished)
        self.current_worker.error.connect(self._on_worker_error)
        self.current_worker.progress.connect(self._on_progress)
        self.current_worker.start()

    def on_summary_clicked(self) -> None:
        """Handle summary button click"""
        if not self.current_video_id:
            return

        # Stop any running worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()

        # Disable UI elements
        self.summary_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # Create and start worker thread
        self.current_worker = WorkerThread(
            task_type="summarize",
            url=self.url_input.text().strip()
        )
        self.current_worker.finished.connect(self._on_summary_finished)
        self.current_worker.error.connect(self._on_worker_error)
        self.current_worker.progress.connect(self._on_progress)
        self.current_worker.start()

    def on_ask_clicked(self) -> None:
        """Handle ask button click"""
        if not self.current_video_id:
            QMessageBox.warning(self, "Error", "Please analyze a video first")
            return

        question = self.question_input.text().strip()
        if not question:
            QMessageBox.warning(self, "Error", "Please enter a question")
            return

        # Stop any running worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()

        # Disable UI elements
        self.ask_btn.setEnabled(False)
        self.question_input.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # Create and start worker thread
        self.current_worker = WorkerThread(
            task_type="ask",
            url=self.url_input.text().strip(),
            question=question
        )
        self.current_worker.finished.connect(self._on_ask_finished)
        self.current_worker.error.connect(self._on_worker_error)
        self.current_worker.progress.connect(self._on_progress)
        self.current_worker.start()
