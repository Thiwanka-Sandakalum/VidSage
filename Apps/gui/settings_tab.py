from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox, QHBoxLayout, QFileDialog, QLineEdit)
from PyQt6.QtCore import pyqtSignal

class SettingsTab(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Theme Selection
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Language
        lang_group = QGroupBox("Language")
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Sinhala"])
        lang_layout.addWidget(QLabel("Language:"))
        lang_layout.addWidget(self.lang_combo)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # Storage Preferences
        storage_group = QGroupBox("Storage Preferences")
        storage_layout = QHBoxLayout()
        self.folder_line = QLineEdit()
        self.folder_line.setPlaceholderText("Choose folder for saving summaries...")
        self.folder_btn = QPushButton("Browse")
        self.folder_btn.clicked.connect(self.browse_folder)
        self.clear_cache_btn = QPushButton("Clear Cache")
        storage_layout.addWidget(self.folder_line)
        storage_layout.addWidget(self.folder_btn)
        storage_layout.addWidget(self.clear_cache_btn)
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)

        # AI Model Settings
        ai_group = QGroupBox("AI Model Settings")
        ai_layout = QHBoxLayout()
        self.whisper_combo = QComboBox()
        self.whisper_combo.addItems(["Whisper Tiny", "Whisper Base", "Whisper Small", "Whisper Medium", "Whisper Large"])
        self.gpt_combo = QComboBox()
        self.gpt_combo.addItems(["GPT-3.5", "GPT-4", "GPT-4o"])
        self.embed_combo = QComboBox()
        self.embed_combo.addItems(["OpenAI", "Local", "Other"])
        ai_layout.addWidget(QLabel("Whisper:"))
        ai_layout.addWidget(self.whisper_combo)
        ai_layout.addWidget(QLabel("GPT:"))
        ai_layout.addWidget(self.gpt_combo)
        ai_layout.addWidget(QLabel("Embedding:"))
        ai_layout.addWidget(self.embed_combo)
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        layout.addStretch()

        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_line.setText(folder)

    def _on_theme_changed(self, theme):
        self.theme_changed.emit(theme)
