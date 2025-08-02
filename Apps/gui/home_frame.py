# HomeFrame for YT Insight GUI
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

class HomeFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomeFrame")
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Top Bar
        top_bar = QHBoxLayout()
        title = QLabel("<b>YT Insight</b>")
        title.setStyleSheet("font-size: 22px;")
        top_bar.addWidget(title)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # URL Input Section
        url_group = QGroupBox()
        url_layout = QHBoxLayout()
        url_label = QLabel("🔗 Paste YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube video URL…")
        self.analyze_btn = QPushButton("Analyze")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.analyze_btn)
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)

        # Summary Output Section
        summary_group = QGroupBox("📄 Summary Output")
        summary_layout = QVBoxLayout()
        self.summary_output = QTextEdit()
        self.summary_output.setReadOnly(True)
        self.summary_output.setPlaceholderText("Summary will appear here…")
        self.summary_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        summary_layout.addWidget(self.summary_output)
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)

        # Ask Question Section
        qa_group = QGroupBox()
        qa_layout = QVBoxLayout()
        ask_row = QHBoxLayout()
        ask_label = QLabel("❓ Ask a Question:")
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Type your question about the video…")
        self.ask_btn = QPushButton("Ask")
        self.clear_chat_btn = QPushButton("Clear Chat")
        ask_row.addWidget(ask_label)
        ask_row.addWidget(self.question_input)
        ask_row.addWidget(self.ask_btn)
        ask_row.addWidget(self.clear_chat_btn)
        qa_layout.addLayout(ask_row)
        # Answer Output
        answer_label = QLabel("💬 Answer Output:")
        self.answer_output = QTextEdit()
        self.answer_output.setReadOnly(True)
        self.answer_output.setPlaceholderText("Answer will appear here…")
        qa_layout.addWidget(answer_label)
        qa_layout.addWidget(self.answer_output)
        qa_group.setLayout(qa_layout)
        main_layout.addWidget(qa_group)

        # Status/Loading Indicator (slim line, no percent)
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("QLabel { min-height: 2px; max-height: 2px; background: #2196F3; border-radius: 1px; }")
        self.status_label.hide()
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()

        # Connect clear chat button
        self.clear_chat_btn.clicked.connect(self.clear_chat)
        # Connect URL input to auto-clear outputs
        self.url_input.textChanged.connect(self.clear_outputs_on_url)

    def clear_chat(self):
        self.answer_output.clear()
        self.question_input.clear()

    def clear_outputs_on_url(self):
        self.summary_output.clear()
        self.answer_output.clear()
        self.question_input.clear()

    def show_loader(self, show=True):
        if show:
            self.status_label.show()
        else:
            self.status_label.hide()
