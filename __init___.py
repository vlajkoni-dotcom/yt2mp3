"""
__init__.py files for all packages
Create these files in their respective directories
"""

# gui/__init__.py
"""
GUI Package
Contains all user interface components
"""

from .main_window import MainWindow
from .tag_editor import TagEditorDialog

__all__ = ['MainWindow', 'TagEditorDialog']


# core/__init__.py  
"""
Core Package
Contains business logic and processing modules
"""

from .download_manager import DownloadManager
from .tag_manager import TagManager

__all__ = ['DownloadManager', 'TagManager']


# utils/__init__.py
"""
Utils Package
Contains utility functions and helpers
"""

from .file_utils import (
    sanitize_filename,
    remove_emojis,
    validate_filename,
    generate_unique_filename,
    get_safe_filename
)

__all__ = [
    'sanitize_filename',
    'remove_emojis',
    'validate_filename',
    'generate_unique_filename',
    'get_safe_filename'
]
