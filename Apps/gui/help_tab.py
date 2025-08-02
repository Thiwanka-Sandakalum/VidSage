from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QGroupBox, QHBoxLayout, QLineEdit)

class HelpTab(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # How to Use
        howto_group = QGroupBox("How to Use")
        howto_layout = QVBoxLayout()
        self.howto_text = QTextEdit()
        self.howto_text.setReadOnly(True)
        self.howto_text.setPlainText("""
1. Paste a YouTube URL on the Home tab.
2. Click 'Analyze' to process the video.
3. View the summary and ask questions in the Home tab.
4. Review past analyses in the History tab.
5. Adjust preferences in the Settings tab.
""")
        howto_layout.addWidget(self.howto_text)
        howto_group.setLayout(howto_layout)
        layout.addWidget(howto_group)

        # Troubleshooting
        trouble_group = QGroupBox("Troubleshooting")
        trouble_layout = QVBoxLayout()
        self.trouble_text = QTextEdit()
        self.trouble_text.setReadOnly(True)
        self.trouble_text.setPlainText("""
- If analysis fails, check your internet connection.
- Ensure the YouTube URL is valid.
- For persistent issues, restart the app or contact support.
""")
        trouble_layout.addWidget(self.trouble_text)
        trouble_group.setLayout(trouble_layout)
        layout.addWidget(trouble_group)

        # Contact
        contact_group = QGroupBox("Contact")
        contact_layout = QHBoxLayout()
        self.contact_line = QLineEdit()
        self.contact_line.setPlaceholderText("Your email or message...")
        self.contact_btn = QPushButton("Send Feedback")
        contact_layout.addWidget(self.contact_line)
        contact_layout.addWidget(self.contact_btn)
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)

        # About App
        about_group = QGroupBox("About App")
        about_layout = QVBoxLayout()
        self.about_label = QLabel("YT Insight AI v1.0\n© 2025 Your Name. All rights reserved.")
        about_layout.addWidget(self.about_label)
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)

        layout.addStretch()
