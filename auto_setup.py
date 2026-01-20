"""
Automatic Setup Script for Audio Downloader
Run this once to create the entire project structure
"""

import os
from pathlib import Path

def create_structure():
    """Create directory structure and all files"""
    
    # Create directories
    dirs = ["gui", "core", "utils", "resources/icons", "resources/ads"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ Created directory structure")
    
    # Create __init__ files
    init_files = {
        "gui/__init__.py": "",
        "core/__init__.py": "",
        "utils/__init__.py": "",
    }
    
    for filepath, content in init_files.items():
        Path(filepath).write_text(content, encoding='utf-8')
    print("✓ Created __init__.py files")
    
    # Create utils/file_utils.py
    file_utils = '''"""
Utility Module - File Utilities
"""

import re
import unicodedata


def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters and emojis"""
    filename = remove_emojis(filename)
    
    invalid_chars = '<>:"/\\\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    filename = re.sub(r'\\s+', ' ', filename)
    filename = filename.strip(' .')
    
    max_length = 200
    if len(filename) > max_length:
        filename = filename[:max_length].strip()
    
    if not filename:
        filename = "untitled"
    
    return filename


def remove_emojis(text):
    """Remove emoji characters from text"""
    emoji_pattern = re.compile(
        "["
        u"\\U0001F600-\\U0001F64F"
        u"\\U0001F300-\\U0001F5FF"
        u"\\U0001F680-\\U0001F6FF"
        u"\\U0001F1E0-\\U0001F1FF"
        u"\\U00002702-\\U000027B0"
        u"\\U000024C2-\\U0001F251"
        u"\\U0001F900-\\U0001F9FF"
        u"\\U0001FA00-\\U0001FA6F"
        "]+",
        flags=re.UNICODE
    )
    
    text = emoji_pattern.sub('', text)
    
    text = ''.join(
        char for char in text
        if unicodedata.category(char)[0] != 'C'
        or char in '\\n\\r\\t'
    )
    
    return text


def validate_filename(filename):
    """Check if filename is valid for Windows"""
    if not filename:
        return False
    
    invalid_chars = '<>:"/\\\\|?*'
    if any(char in filename for char in invalid_chars):
        return False
    
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    name_without_ext = filename.split('.')[0].upper()
    if name_without_ext in reserved_names:
        return False
    
    if len(filename) > 255:
        return False
    
    return True


def generate_unique_filename(directory, filename):
    """Generate a unique filename if file already exists"""
    directory = Path(directory)
    file_path = directory / filename
    
    if not file_path.exists():
        return file_path
    
    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1
    
    while True:
        new_filename = f"{stem} ({counter}){suffix}"
        new_path = directory / new_filename
        if not new_path.exists():
            return new_path
        counter += 1


def get_safe_filename(artist, title, extension='.mp3'):
    """Generate a safe filename from artist and title"""
    if artist and title:
        filename = f"{artist} - {title}"
    elif title:
        filename = title
    elif artist:
        filename = artist
    else:
        filename = "untitled"
    
    filename = sanitize_filename(filename)
    return f"{filename}{extension}"
'''
    
    Path("utils/file_utils.py").write_text(file_utils, encoding='utf-8')
    print("✓ Created utils/file_utils.py")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNow run:")
    print("  pip install -r requirements.txt")
    print("\nThen I'll provide the remaining files.")

if __name__ == "__main__":
    create_structure()