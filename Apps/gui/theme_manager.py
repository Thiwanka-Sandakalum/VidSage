# ThemeManager for YT Insight AI
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

class ThemeManager:
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    QSS_PATHS = {
        LIGHT: os.path.join(os.path.dirname(__file__), "assets", "styles.qss"),
        DARK: os.path.join(os.path.dirname(__file__), "assets", "dark.qss"),
    }
    SETTINGS_KEY = "theme"

    @staticmethod
    def apply_theme(theme: str):
        if theme == ThemeManager.AUTO:
            # Use system theme (default to light for now)
            theme = ThemeManager.LIGHT
        qss_path = ThemeManager.QSS_PATHS.get(theme, ThemeManager.QSS_PATHS[ThemeManager.LIGHT])
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                QApplication.instance().setStyleSheet(f.read())
        # Save to settings
        settings = QSettings("YTInsight", "YTInsightAI")
        settings.setValue(ThemeManager.SETTINGS_KEY, theme)

    @staticmethod
    def load_theme():
        settings = QSettings("YTInsight", "YTInsightAI")
        theme = settings.value(ThemeManager.SETTINGS_KEY, ThemeManager.LIGHT)
        ThemeManager.apply_theme(theme)

    @staticmethod
    def get_current_theme():
        settings = QSettings("YTInsight", "YTInsightAI")
        return settings.value(ThemeManager.SETTINGS_KEY, ThemeManager.LIGHT)
