# Audio Downloader

A professional Windows desktop application for downloading and managing audio content from YouTube with automatic metadata tagging.

## Features

### Core Functionality
- ✅ Download single videos or entire playlists
- ✅ Automatic audio extraction (MP3 or M4A)
- ✅ Smart metadata extraction from video titles
- ✅ Interactive tag editor after each download
- ✅ Automatic file renaming based on metadata
- ✅ Downloaded files tracking table

### User Experience
- 🎨 Modern, clean PySide6 interface
- 📊 Real-time download progress tracking
- 📋 Playlist progress indicator
- 🏷️ Immediate tag editing after download
- 📁 Direct save to Windows Music folder
- 💰 Integrated advertisement space

### Technical Excellence
- 🧵 Non-blocking threaded downloads
- 🛡️ Robust error handling
- 📝 Comprehensive logging
- 🔄 Graceful failure recovery
- 🎯 Production-ready code quality

## Installation

### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- ffmpeg (bundled in distribution)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd audio_downloader
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download ffmpeg**
- Download from: https://ffmpeg.org/download.html
- Extract and place `ffmpeg.exe` in project root or system PATH

4. **Run the application**
```bash
python main.py
```

## Usage

### Downloading Audio

1. **Enter URL**
   - Paste a YouTube video or playlist URL
   - Application auto-detects the type

2. **Select Format**
   - Choose MP3 (default) or M4A
   - Both formats support full metadata

3. **Start Download**
   - Click "Download" or press Enter
   - Watch progress in real-time

4. **Edit Tags**
   - Tag editor opens automatically after download
   - Edit: Artist, Title, Album, Track Number
   - Preview filename before saving
   - Optionally rename file

5. **View Downloaded Files**
   - All files appear in the table
   - Columns: Artist, Title, Album, Filename

### File Naming

**Primary Format**: `Artist - Title.mp3`

**Fallback Rules**:
- If artist missing → Use video title
- If title missing → Use video title
- Invalid characters → Automatically removed
- Emojis → Automatically removed

### Output Location

All files are saved to:
```
C:\Users\<YourUsername>\Music\
```

## Project Structure

```
audio_downloader/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── gui/
│   ├── main_window.py     # Main UI
│   └── tag_editor.py      # Tag editor dialog
├── core/
│   ├── download_manager.py # Download logic
│   └── tag_manager.py     # Metadata handling
└── utils/
    └── file_utils.py      # File operations
```

## Building Distributable

### Using PyInstaller

1. **Install PyInstaller**
```bash
pip install pyinstaller
```

2. **Create executable**
```bash
pyinstaller --windowed --onefile ^
  --add-binary "yt-dlp.exe;." ^
  --add-binary "ffmpeg.exe;." ^
  --name "AudioDownloader" ^
  main.py
```

3. **Find executable**
- Location: `dist/AudioDownloader.exe`
- Single file, no installation required

### Distribution Checklist

- ✅ Bundle yt-dlp executable
- ✅ Bundle ffmpeg executable
- ✅ Include Qt WebEngine resources
- ✅ Test on clean Windows installation
- ✅ Verify Music folder creation
- ✅ Test single video download
- ✅ Test playlist download
- ✅ Test tag editing and renaming

## Monetization

### Google Ads Integration

The application includes a dedicated advertisement space:
- **Size**: 728x90 (Leaderboard) or 970x90 (Large Leaderboard)
- **Location**: Top of window, full width
- **Technology**: Qt WebEngine (Chromium-based)

**To add your ads**:

1. Edit `gui/main_window.py`
2. Replace placeholder HTML in `create_ad_section()`
3. Insert your Google AdSense code

Example:
```python
ad_html = """
<!DOCTYPE html>
<html>
<head>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXX"
     crossorigin="anonymous"></script>
</head>
<body>
    <ins class="adsbygoogle"
         style="display:inline-block;width:728px;height:90px"
         data-ad-client="ca-pub-XXXXXXXX"
         data-ad-slot="YYYYYYYYYY"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</body>
</html>
"""
```

## Technical Details

### Architecture

- **GUI Layer**: PySide6 (Qt for Python)
- **Download Engine**: yt-dlp with ffmpeg
- **Metadata**: mutagen library
- **Threading**: QThread for non-blocking operations

### Threading Model

```
Main Thread (GUI)
    ↓
QThread (Download Worker)
    ↓
yt-dlp → ffmpeg → File
    ↓
Signal → Main Thread → Update UI
```

### Error Handling

- Network failures → Retry with user notification
- Missing videos in playlist → Skip and continue
- Tag write failures → Notify, keep file intact
- File conflicts → Automatic unique naming
- Invalid URLs → Pre-validation with helpful messages

### Supported Formats

**Audio Output**:
- MP3 (192 kbps)
- M4A (AAC)

**Metadata Tags**:
- Title (TIT2 / ©nam)
- Artist (TPE1 / ©ART)
- Album (TALB / ©alb)
- Track Number (TRCK / trkn)

## Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Check all dependencies are installed
- Verify ffmpeg is accessible

### Downloads fail immediately
- Check internet connection
- Verify YouTube URL is valid
- Update yt-dlp: `pip install --upgrade yt-dlp`

### Tag editor doesn't open
- Check file was successfully downloaded
- Verify file exists in Music folder
- Check file permissions

### File rename fails
- Ensure file isn't open in another program
- Check filename doesn't exceed 255 characters
- Verify no invalid characters in filename

### Playlist downloads stop
- Normal behavior: Skips unavailable videos
- Check error messages for specific issues
- Some videos may have download restrictions

## Development

### Running in Development

```bash
# Install in editable mode
pip install -e .

# Run with debug output
python main.py
```

### Code Style

- PEP 8 compliant
- Type hints where applicable
- Comprehensive docstrings
- Separation of concerns (MVC pattern)

### Testing

```bash
# Test single video download
# Test playlist download
# Test tag editing
# Test file renaming
# Test error conditions
```

## License

This software is for personal use only. Respect copyright laws and terms of service of content platforms.

## Disclaimer

This application is a personal content management tool. Users are responsible for ensuring they have the right to download and store content. The developers do not condone piracy or copyright infringement.

## Support

For issues, questions, or feature requests:
- Check troubleshooting section
- Review error messages carefully
- Ensure all dependencies are up to date

## Credits

- **PySide6**: Qt Company
- **yt-dlp**: yt-dlp developers
- **ffmpeg**: FFmpeg developers
- **mutagen**: mutagen developers

---

**Version**: 1.0.0  
**Platform**: Windows 10/11  
**Python**: 3.8+
