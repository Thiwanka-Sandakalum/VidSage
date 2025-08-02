# MainWindow for YT Insight GUI
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QStackedWidget
from PyQt6.QtCore import Qt
from home_frame import HomeFrame

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Insight - Video Analyzer")
        self.setMinimumSize(900, 700)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.vlayout = QVBoxLayout()
        self.central_widget.setLayout(self.vlayout)

        # Stacked widget for navigation
        self.stacked = QStackedWidget()
        self.vlayout.addWidget(self.stacked)

        # Home page
        self.home_frame = HomeFrame()
        self.stacked.addWidget(self.home_frame)
        self.stacked.setCurrentWidget(self.home_frame)
