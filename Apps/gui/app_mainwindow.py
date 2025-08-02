# YT Insight AI - MainWindow (Professional PyQt6 UI Skeleton)
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QMenu
)
from PyQt6.QtGui import QAction
from home_tab import HomeTab
from history_tab import HistoryTab
from settings_tab import SettingsTab
from help_tab import HelpTab
from theme_manager import ThemeManager

class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Insight AI")
        self.setMinimumSize(1100, 750)
        ThemeManager.load_theme()  # Apply theme on startup
        self._build_menu()
        self._build_tabs()

    def _build_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # File Menu
        file_menu = QMenu("&File", self)
        menubar.addMenu(file_menu)
        file_menu.addAction(QAction("New Session", self))
        file_menu.addAction(QAction("Open History", self))
        file_menu.addAction(QAction("Export Summary", self))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self))

        # Edit Menu
        edit_menu = QMenu("&Edit", self)
        menubar.addMenu(edit_menu)
        edit_menu.addAction(QAction("Clear Input", self))
        edit_menu.addAction(QAction("Preferences", self))

        # View Menu
        view_menu = QMenu("&View", self)
        menubar.addMenu(view_menu)
        view_menu.addAction(QAction("Toggle Sidebar", self))
        view_menu.addAction(QAction("Developer Console", self))

        # Help Menu
        help_menu = QMenu("&Help", self)
        menubar.addMenu(help_menu)
        help_menu.addAction(QAction("How it Works", self))
        help_menu.addAction(QAction("About", self))
        help_menu.addAction(QAction("Contact / Feedback", self))

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)
        self.setCentralWidget(self.tabs)

        # Add main tabs
        self.home_tab = HomeTab()
        self.history_tab = HistoryTab()
        self.settings_tab = SettingsTab()
        self.help_tab = HelpTab()
        self.tabs.addTab(self.home_tab, "🏠 Home")
        self.tabs.addTab(self.history_tab, "🕘 History")
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")
        self.tabs.addTab(self.help_tab, "❓ Help")

        # Connect theme change
        self.settings_tab.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name):
        theme_map = {"Light": ThemeManager.LIGHT, "Dark": ThemeManager.DARK, "Auto": ThemeManager.AUTO}
        ThemeManager.apply_theme(theme_map.get(theme_name, ThemeManager.LIGHT))
