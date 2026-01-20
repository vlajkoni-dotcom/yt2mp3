"""
Utility Module - File Utilities
File name sanitization and validation
"""

import re
import unicodedata


def sanitize_filename(filename):
    """
    Sanitize filename by removing invalid characters and emojis
    Normalize Serbian Latin to ASCII
    """
    # Normalize Serbian characters
    filename = normalize_serbian(filename)
    
    # Remove emojis and other non-standard unicode
    filename = remove_emojis(filename)
    
    # Remove or replace invalid Windows filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length (Windows has 255 char limit for filenames)
    max_length = 200
    if len(filename) > max_length:
        filename = filename[:max_length].strip()
    
    # If filename is empty after sanitization, use a default
    if not filename:
        filename = "untitled"
    
    return filename


def normalize_serbian(text):
    """
    Normalize Serbian characters to ASCII
    č -> c, ć -> c, š -> s, ž -> z, đ -> dj
    """
    replacements = {
        'č': 'c', 'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'dj',
        'Č': 'C', 'Ć': 'C', 'Š': 'S', 'Ž': 'Z', 'Đ': 'Dj',
    }
    
    for serbian, latin in replacements.items():
        text = text.replace(serbian, latin)
    
    return text


def remove_emojis(text):
    """
    Remove emoji characters from text
    
    Args:
        text: Input text string
        
    Returns:
        str: Text with emojis removed
    """
    # Remove emoji characters
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U0001FA00-\U0001FA6F"  # chess symbols
        "]+",
        flags=re.UNICODE
    )
    
    text = emoji_pattern.sub('', text)
    
    # Remove other problematic unicode categories
    text = ''.join(
        char for char in text
        if unicodedata.category(char)[0] != 'C'  # Control characters
        or char in '\n\r\t'  # Keep common whitespace
    )
    
    return text


def validate_filename(filename):
    """
    Check if filename is valid for Windows
    
    Args:
        filename: Filename to validate
        
    Returns:
        bool: True if valid
    """
    if not filename:
        return False
    
    # Check for invalid characters
    invalid_chars = '<>:"/\\|?*'
    if any(char in filename for char in invalid_chars):
        return False
    
    # Check for reserved names
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    name_without_ext = filename.split('.')[0].upper()
    if name_without_ext in reserved_names:
        return False
    
    # Check length
    if len(filename) > 255:
        return False
    
    return True


def generate_unique_filename(directory, filename):
    """
    Generate a unique filename if file already exists
    
    Args:
        directory: Directory path (Path object)
        filename: Desired filename
        
    Returns:
        Path: Unique file path
    """
    from pathlib import Path
    
    directory = Path(directory)
    file_path = directory / filename
    
    if not file_path.exists():
        return file_path
    
    # File exists, add counter
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
    """
    Generate a safe filename from artist and title
    
    Args:
        artist: Artist name
        title: Song title
        extension: File extension (including dot)
        
    Returns:
        str: Safe filename
    """
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