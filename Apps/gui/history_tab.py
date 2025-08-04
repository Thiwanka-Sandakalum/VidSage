# HistoryTab for YT Insight AI
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QSplitter, QListWidgetItem
)
from PyQt6.QtCore import Qt
from typing import Dict, List, Optional
import os
import json
from PyQt6.QtGui import QPixmap

class HistoryTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.video_infos: List[Dict[str, str]] = []
        self._build_ui()
        self._populate_history()
        self.history_list.currentItemChanged.connect(self._on_history_selected)
        self.search_input.textChanged.connect(self._on_search)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Search Bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history…")
        search_row.addWidget(QLabel("🔍"))
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        # Splitter for List and Details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        # History List
        self.history_list = QListWidget()
        splitter.addWidget(self.history_list)
        # Details View
        details = QWidget()
        details_layout = QVBoxLayout(details)
        self.detail_title = QLabel("Title: -")
        self.detail_thumb = QLabel()
        self.detail_thumb.setFixedSize(120, 68)
        self.detail_summary = QTextEdit()
        self.detail_summary.setReadOnly(True)
        self.detail_summary.setPlaceholderText("Summary…")
        self.detail_export = QPushButton("Export/Share")
        details_layout.addWidget(self.detail_title)
        details_layout.addWidget(self.detail_thumb)
        details_layout.addWidget(self.detail_summary)
        details_layout.addWidget(self.detail_export)
        splitter.addWidget(details)
        splitter.setSizes([200, 400])
        layout.addWidget(splitter)

    def _populate_history(self) -> None:
        # Find all *_info.json files in the GUI data directory
        data_dir = os.path.expanduser("~/Documents/learn/VidSage/Apps/gui/Apps/gui/data")
        # Create data directory and subdirectories if they don't exist
        for subdir in ["audio", "info", "subtitles", "thumbnails", "video", "summaries"]:
            os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)
            
        self.video_infos = []
        if not os.path.exists(data_dir):
            return
            
        for folder in os.listdir(data_dir):
            folder_path = os.path.join(data_dir, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith("_info.json"):
                        info_path = os.path.join(folder_path, file)
                        try:
                            with open(info_path, "r", encoding="utf-8") as f:
                                info = json.load(f)
                                self.video_infos.append(info)
                        except Exception:
                            continue
        self._refresh_history_list()

    def _refresh_history_list(self, filter_text: str = "") -> None:
        self.history_list.clear()
        for info in self.video_infos:
            if filter_text.lower() in info.get("title", "").lower():
                self.history_list.addItem(f"{info.get('title', '-')}")

    def _on_search(self, text: str) -> None:
        self._refresh_history_list(text)

    def _on_history_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        if not current:
            return
        title = current.text()
        info = next((v for v in self.video_infos if v.get("title", "") == title), None)
        if not info:
            return
        self.detail_title.setText(f"Title: {info.get('title', '-')}")
        # Thumbnail
        thumb_path = os.path.expanduser(f"~/Documents/learn/VidSage/Apps/gui/Apps/gui/data/thumbnails/{info['id']}.jpg")
        if os.path.exists(thumb_path):
            pixmap = QPixmap(thumb_path)
            self.detail_thumb.setPixmap(pixmap.scaled(self.detail_thumb.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            # Try to download if not present
            from core.youtube_processor import YouTubeProcessor
            try:
                yt = YouTubeProcessor()
                thumb_path, _ = yt.download_thumbnail(f"https://www.youtube.com/watch?v={info['id']}", thumb_path)
                pixmap = QPixmap(thumb_path)
                self.detail_thumb.setPixmap(pixmap.scaled(self.detail_thumb.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except Exception:
                self.detail_thumb.clear()
        # Summary
        summary_path = os.path.expanduser(f"~/Documents/learn/VidSage/Apps/gui/Apps/gui/data/summaries/{info['id']}/{info['id']}_default.txt")
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                self.detail_summary.setPlainText(f.read())
        else:
            self.detail_summary.setPlainText("No summary available.")
