"""
Core Module - Download Manager with thumbnail support
"""

import os
import time
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread
import yt_dlp

from utils.file_utils import sanitize_filename
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC
from mutagen.mp4 import MP4, MP4Cover


class DownloadWorker(QObject):
    """Worker thread for downloading audio"""
    
    started = Signal(str)
    progress = Signal(float)
    completed = Signal(str, dict, object)
    error = Signal(str)
    playlist_progress = Signal(int, int)
    file_exists_check = Signal(str, str, dict, object)
    
    def __init__(self, url, audio_format, download_folder, download_type="auto", selected_indices=None):
        super().__init__()
        self.url = url
        self.audio_format = audio_format
        self.music_dir = Path(download_folder)
        self.download_type = download_type
        self.selected_indices = selected_indices
        self.is_playlist = False
        self.total_videos = 0
        self.current_video = 0
        
    def run(self):
        """Execute download"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.music_dir / '%(title)s.%(ext)s'),
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.audio_format,
                        'preferredquality': '192',
                    },
                    {
                        'key': 'EmbedThumbnail',
                        'already_have_thumbnail': False,
                    }
                ],
                'writethumbnail': True,  # Will create separate .jpg/.png
                'embedthumbnail': True,  # Also tries to embed, but doesn't always work
                'add_metadata': False,
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'sleep_interval': 2,
                'max_sleep_interval': 5,
            }

            effective_url = self.url

            if self.download_type == "single":
                if "list=" in effective_url and "&noplaylist=1" not in effective_url:
                    effective_url += "&noplaylist=1"
                ydl_opts['yes_playlist'] = False

            elif self.download_type == "playlist":
                effective_url = effective_url.replace("&noplaylist=1", "")
                ydl_opts['yes_playlist'] = True

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(effective_url, download=False)
                
                if not info:
                    self.error.emit("Failed to extract video information")
                    return
                
                # Proveri dostupnost za single video
                if self.download_type == "single":
                    if info.get('availability', '') == 'private':
                        self.error.emit("This video is private. You need to sign in to access it.")
                        return
                    if 'unavailable' in str(info.get('title', '')).lower() or 'terminated' in str(info.get('uploader', '')).lower():
                        self.error.emit("This video is no longer available.")
                        return
                
                is_playlist_detected = 'entries' in info
                if self.download_type == "single":
                    is_playlist_detected = False

                if is_playlist_detected:
                    self.is_playlist = True
                    entries = [e for e in info['entries'] if e is not None]
                    
                    if self.selected_indices is not None:
                        entries = [entries[i] for i in self.selected_indices if i < len(entries)]
                    
                    self.total_videos = len(entries)
                    
                    for idx, entry in enumerate(entries, 1):
                        self.current_video = idx
                        self.playlist_progress.emit(idx, self.total_videos)
                        
                        try:
                            self.download_single_video(entry, ydl, idx)
                            time.sleep(2)
                        except Exception as e:
                            error_msg = str(e)
                            if "rate-limited" in error_msg.lower():
                                self.error.emit("YouTube rate limit reached. Please wait and try again later.")
                                break
                            self.error.emit(f"Skipped '{entry.get('title', 'Unknown')}': {str(e)}")
                            continue
                else:
                    self.download_single_video(info, ydl)
                    
        except Exception as e:
            self.error.emit(f"Download failed: {str(e)}")
            
    def download_single_video(self, info, ydl, track_number=None):
        """Download a single video"""
        title = info.get('title', 'Unknown')
        self.started.emit(title)
        
        metadata = self.extract_metadata(info)
        potential_path = self.generate_filename(metadata, title)
        
        if potential_path.exists():
            self.file_exists_check.emit(
                potential_path.name,
                str(potential_path),
                metadata,
                track_number
            )
            return
        
        try:
            ydl.download([info['webpage_url'] if 'webpage_url' in info else info['id']])
        except Exception as e:
            if "rate-limited" in str(e).lower():
                raise Exception("Rate limited by YouTube")
            raise e
        
        file_path = self.find_downloaded_file(title)
        
        if file_path:
            # Cleanup thumbnails
            self.cleanup_thumbnails(file_path)
            
            # Embed thumbnail into the audio file
            self.embed_thumbnail_into_file(file_path, info)
            
            self.completed.emit(str(file_path), metadata, track_number)
        else:
            self.error.emit(f"Downloaded file not found for: {title}")
    
    def cleanup_thumbnails(self, audio_file):
        """Remove leftover thumbnail files"""
        audio_path = Path(audio_file)
        thumb_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        for ext in thumb_extensions:
            thumb_file = audio_path.parent / f"{audio_path.stem}{ext}"
            if thumb_file.exists():
                try:
                    thumb_file.unlink()
                except:
                    pass
    
    def embed_thumbnail_into_file(self, file_path, info):
        """Embed thumbnail into the audio file using mutagen"""
        try:
            # Find thumbnail file
            thumb_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            audio_path = Path(file_path)
            
            thumb_file = None
            for ext in thumb_extensions:
                candidate = audio_path.parent / f"{audio_path.stem}{ext}"
                if candidate.exists():
                    thumb_file = candidate
                    break
            
            if not thumb_file:
                return  # No thumbnail to embed
            
            # Read thumbnail data
            with open(thumb_file, 'rb') as f:
                thumb_data = f.read()
            
            # Get MIME type
            mime_type = "image/jpeg"
            if thumb_file.suffix.lower() == ".png":
                mime_type = "image/png"
            elif thumb_file.suffix.lower() == ".webp":
                mime_type = "image/webp"
            
            # Embed into MP3 or M4A
            if file_path.suffix.lower() == ".mp3":
                audio = MP3(file_path, ID3=ID3)
                if not audio.tags:
                    audio.add_tags()
                audio.tags.add(
                    APIC(
                        encoding=3,  # UTF-8
                        mime=mime_type,
                        type=3,  # Cover art
                        desc='Cover',
                        data=thumb_data
                    )
                )
                audio.save()
                
            elif file_path.suffix.lower() == ".m4a":
                audio = MP4(file_path)
                cover = MP4Cover(thumb_data, imageformat=MP4Cover.FORMAT_JPEG if mime_type == "image/jpeg" else MP4Cover.FORMAT_PNG)
                audio["covr"] = [cover]
                audio.save()
            
            # Delete temporary thumbnail file
            thumb_file.unlink()
            
        except Exception as e:
            print(f"Failed to embed thumbnail: {str(e)}")
    
    def generate_filename(self, metadata, fallback_title):
        """Generate expected filename based on metadata"""
        artist = metadata.get('artist', '')
        title = metadata.get('title', fallback_title)
        
        if artist and title:
            filename = f"{artist} - {title}"
        elif title:
            filename = title
        else:
            filename = fallback_title
            
        filename = sanitize_filename(filename)
        return self.music_dir / f"{filename}.{self.audio_format}"
            
    def extract_metadata(self, info):
        """Extract metadata from video info with improved parsing"""
        metadata = {}
        
        title = info.get('title', '')
        
        if ' - ' in title:
            parts = title.split(' - ', 1)
            artist = parts[0].strip()
            song_title = parts[1].strip()
            song_title = self.clean_title(song_title)
            metadata['artist'] = artist
            metadata['title'] = song_title
        elif ': ' in title:
            parts = title.split(': ', 1)
            artist = parts[0].strip()
            song_title = self.clean_title(parts[1].strip())
            metadata['artist'] = artist
            metadata['title'] = song_title
        else:
            cleaned = self.clean_title(title)
            metadata['title'] = cleaned
            metadata['artist'] = info.get('uploader', info.get('channel', ''))
        
        metadata['album'] = info.get('album', info.get('playlist_title', ''))
        
        return metadata
    
    def clean_title(self, title):
        """Remove extra info from title - keep artist names in parentheses"""
        import re
        
        remove_terms = [
            'official video', 'official music video', 'official audio', 'official',
            'lyrics', 'lyric video', 'with lyrics', 'letra', 'paroles',
            'hd', 'hq', '4k', 'uhd', '1080p', '720p', '480p',
            'audio', 'video', 'music video', 'visualizer', 'remaster', 'remastered',
            'full album', 'full', 'explicit', 'clean version', 'radio edit',
            'extended', 'remix', 'live', 'acoustic', 'unplugged'
        ]
        
        year_pattern = r'\(?(?:19|20)\d{2}\)?'
        title = re.sub(year_pattern, '', title)
        
        def process_bracket_content(match):
            content = match.group(1).strip()
            content_lower = content.lower()
            
            for term in remove_terms:
                if term in content_lower:
                    return ''
            
            if any(word in content_lower for word in ['feat', 'ft', 'featuring', 'with', '&', 'x']):
                return match.group(0)
            
            if len(content) < 30:
                return match.group(0)
            
            return ''
        
        title = re.sub(r'\(([^)]+)\)', process_bracket_content, title)
        title = re.sub(r'\[([^\]]+)\]', process_bracket_content, title)
        
        title_lower = title.lower().strip()
        for term in remove_terms:
            if title_lower.endswith(term):
                title = title[:-(len(term))].strip()
                title_lower = title.lower().strip()
        
        title = re.sub(r'\s+', ' ', title)
        title = re.sub(r'\s*[-_|]+\s*$', '', title)
        
        return title.strip()
        
    def find_downloaded_file(self, title):
        """Find the downloaded file by title"""
        sanitized = sanitize_filename(title)
        time.sleep(0.5)
        
        for file in self.music_dir.glob(f"*.{self.audio_format}"):
            if sanitized.lower() in file.stem.lower():
                return file
                
        possible_path = self.music_dir / f"{sanitized}.{self.audio_format}"
        if possible_path.exists():
            return possible_path
            
        files = list(self.music_dir.glob(f"*.{self.audio_format}"))
        if files:
            return max(files, key=lambda p: p.stat().st_mtime)
            
        return None
        
    def progress_hook(self, d):
        """Handle download progress updates"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress.emit(percent)
            elif 'total_bytes_estimate' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                self.progress.emit(percent)
        elif d['status'] == 'finished':
            self.progress.emit(100)


class DownloadManager(QObject):
    """Manages download operations"""
    
    download_started = Signal(str)
    progress_updated = Signal(float)
    download_completed = Signal(str, dict, object)
    playlist_progress = Signal(int, int)
    error_occurred = Signal(str)
    all_downloads_finished = Signal()
    file_exists = Signal(str, str, dict, object)
    
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.download_folder = Path.home() / "Music"
        
    def set_download_folder(self, folder):
        """Set download folder"""
        self.download_folder = Path(folder)
        
    def start_download(self, url, audio_format, download_type="auto", selected_indices=None):
        """Start download in background thread"""
        try:
            if self.thread and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()
        except RuntimeError:
            # Thread already deleted, continue
            pass
        
        self.thread = QThread()
        self.worker = DownloadWorker(url, audio_format, self.download_folder, download_type, selected_indices)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.started.connect(self.download_started)
        self.worker.progress.connect(self.progress_updated)
        self.worker.completed.connect(self.download_completed)
        self.worker.playlist_progress.connect(self.playlist_progress)
        self.worker.error.connect(self.error_occurred)
        self.worker.file_exists_check.connect(self.file_exists)
        
        self.worker.completed.connect(self.check_if_finished)
        self.worker.error.connect(self.check_if_finished)
        self.worker.file_exists_check.connect(self.check_if_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
        
    def check_if_finished(self):
        """Check if all downloads are finished"""
        if self.worker and self.worker.is_playlist:
            if self.worker.current_video >= self.worker.total_videos:
                self.cleanup()
        else:
            self.cleanup()
            
    def cleanup(self):
        """Clean up thread"""
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.all_downloads_finished.emit()