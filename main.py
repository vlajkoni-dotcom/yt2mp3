"""
Audio Downloader - Production Desktop Application
Main entry point and application initialization
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow


def setup_application():
    """Initialize application settings and paths"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application instance
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Downloader")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AudioDownloader")
    
    # Ensure music directory exists
    music_dir = Path.home() / "Music"
    music_dir.mkdir(parents=True, exist_ok=True)
    
    return app


def main():
    """Main application entry point"""
    app = setup_application()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()