# HomeTab for YT Insight AI
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QProgressBar, QFrame, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from core.youtube_processor import YouTubeProcessor
from core.summarizer import Summarizer
from core.rag_system import RAGSystem
import traceback
import re
from markdown import markdown

class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        self.youtube_processor = YouTubeProcessor(data_dir="Apps/gui/data")
        self.summarizer = Summarizer()
        self.rag_system = RAGSystem()
        self.ask_btn.clicked.connect(self.on_ask_clicked)

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

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Summary Button (after progress bar)
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
        # # Highlights
        # self.highlights = QTextEdit()
        # self.highlights.setReadOnly(True)
        # self.highlights.setPlaceholderText("Key takeaways…")
        # summary_layout.addWidget(self.highlights)
        # # Find in Text
        # find_row = QHBoxLayout()
        # self.find_input = QLineEdit()
        # self.find_input.setPlaceholderText("Find in summary…")
        # self.copy_btn = QPushButton("Copy")
        # self.export_btn = QPushButton("Export")
        # find_row.addWidget(self.find_input)
        # find_row.addWidget(self.copy_btn)
        # find_row.addWidget(self.export_btn)
        # summary_layout.addLayout(find_row)

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
        # Loading spinner/status
        self.qa_status = QLabel()
        qa_layout.addWidget(self.qa_status)
        # Suggested Qs (optional, placeholder)
        self.suggested_qs = QLabel("Suggested: What is the main topic?")
        qa_layout.addWidget(self.suggested_qs)
        self.suggested_qs.setVisible(False)

    def clean_and_format_answer(self, answer: str) -> str:
        # Remove timestamps like [00:00], [0:00], [12:34]
        answer = re.sub(r'\[\d{1,2}:\d{2}\]', '', answer)
        # Convert markdown to HTML
        html = markdown(answer, extensions=['extra', 'sane_lists'])
        # Use .qa-card class for styling (no inline CSS)
        styled = f"""
        <div class='qa-card ai-turn'>
            <div>{html}</div>
        </div>
        """
        return styled

    def on_analyze_clicked(self):
        from PyQt6.QtGui import QPixmap
        import os
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL.")
            return
        self.progress.setVisible(True)
        self.progress.setValue(10)
        try:
            # Fetch video info (sync for now, ideally move to QThread for real app)
            info = self.youtube_processor.get_video_info(url)
            self.progress.setValue(60)
            # Update video info card
            self.title.setText(f"Title: {info.get('title', '-')}")
            # Show duration in minutes
            duration_sec = info.get('length', '-')
            if isinstance(duration_sec, int):
                mins = duration_sec // 60
                secs = duration_sec % 60
                self.duration.setText(f"Duration: {mins}m {secs:02d}s")
            else:
                self.duration.setText(f"Duration: {duration_sec}")
            self.channel.setText(f"Channel: {info.get('author', '-')}")
            # Download and show thumbnail
            thumb_path = None
            try:
                thumb_path, _ = self.youtube_processor.download_thumbnail(url)
            except Exception as e:
                thumb_path = None
            if thumb_path and os.path.exists(thumb_path):
                pixmap = QPixmap(thumb_path)
                self.thumbnail.setPixmap(pixmap)
                self.thumbnail.setScaledContents(True)
            else:
                self.thumbnail.clear()
            self.info_card.setVisible(True)
            self.result_tabs.setVisible(True)
            self.progress.setValue(100)
            self.summary_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch video info:\n{str(e)}\n{traceback.format_exc()}")
            self.info_card.setVisible(False)
            self.result_tabs.setVisible(False)
            self.summary_btn.setEnabled(False)
        self.progress.setVisible(False)

    def on_summary_clicked(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL.")
            return
        self.progress.setVisible(True)
        self.progress.setValue(20)
        try:
            # Get transcript (for demo, use subtitles if available)
            transcript = self.youtube_processor.get_transcript_from_subtitles(url)
            if not transcript:
                raise Exception("No transcript/subtitles found for this video.")
            self.progress.setValue(60)
            summary = self.summarizer.summarize(transcript, summary_type="default", engine="gemini")
            self.progress.setValue(90)
            self.summary_box.setPlainText(summary)
            self.result_tabs.setCurrentWidget(self.summary_tab)
            self.progress.setValue(100)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate summary:\n{str(e)}\n{traceback.format_exc()}")
        self.progress.setVisible(False)

    def on_ask_clicked(self):
        url = self.url_input.text().strip()
        question = self.question_input.text().strip()
        if not url or not question:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL and your question.")
            return
        self.qa_status.setText("Thinking...")
        self.qa_status.repaint()
        try:
            transcript = self.youtube_processor.get_transcript_from_subtitles(url)
            if not transcript:
                raise Exception("No transcript/subtitles found for this video.")
            video_id = self.youtube_processor.extract_video_id(url)
            persist_dir = f"Apps/cli/data/vectorstores/{video_id}/chroma_db"
            docs = self.rag_system.process_transcript(transcript)
            self.rag_system.create_vectorstore(docs, persist_directory=persist_dir)
            self.rag_system.create_qa_chain()
            answer = self.rag_system.answer_question(question)
            # Use .qa-card class for user and AI turns
            user_html = (
                "<div class='qa-card user-turn' style='margin-bottom:2px;'><span style='color:#007acc;font-weight:bold;'>You:</span> "
                f"<span style='color:#23272f;font-size:1.08em;'>{question}</span></div>"
            )
            ai_html = self.clean_and_format_answer(answer)
            self.chat_area.append(
                f"<div style='margin:0 0 18px 0; padding:0;'>"
                f"{user_html}"
                f"{ai_html}"
                f"</div>"
            )
            self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
            self.question_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to answer question:\n{str(e)}\n{traceback.format_exc()}")
        self.qa_status.setText("")
