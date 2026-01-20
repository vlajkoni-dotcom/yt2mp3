# gui/playlist_selector.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QProgressBar,
    QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
import yt_dlp


class PlaylistInfoWorker(QObject):
    """Worker to fetch playlist information"""
    
    finished = Signal(list)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        """Fetch playlist info"""
        try:
            self.progress.emit("Fetching playlist information...")
            
            ydl_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'playlistend': 50,  # Limit to first 50 videos
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if 'entries' in info:
                    entries = []
                    for entry in info['entries']:
                        if entry:
                            entries.append({
                                'title': entry.get('title', 'Unknown'),
                                'duration': entry.get('duration', 0),
                                'id': entry.get('id', ''),
                                'availability': entry.get('availability', ''),
                            })
                        if len(entries) >= 50:
                            break
                    
                    if len(entries) == 50:
                        self.progress.emit("Limited to first 50 videos...")
                    
                    self.finished.emit(entries)
                else:
                    # Try to force playlist detection
                    if "list=" in self.url:
                        # Extract list ID
                        list_id = self.url.split("list=")[1].split("&")[0]
                        forced_url = f"https://www.youtube.com/playlist?list={list_id}"
                        self.progress.emit(f"Trying playlist URL: {forced_url}")
                        info = ydl.extract_info(forced_url, download=False)
                        if 'entries' in info:
                            entries = []
                            for entry in info['entries']:
                                if entry:
                                    entries.append({
                                        'title': entry.get('title', 'Unknown'),
                                        'duration': entry.get('duration', 0),
                                        'id': entry.get('id', ''),
                                        'availability': entry.get('availability', ''),
                                    })
                            self.finished.emit(entries)
                        else:
                            self.error.emit("Not a playlist URL")
                    else:
                        self.error.emit("Not a playlist URL")
                    
        except Exception as e:
            self.error.emit(f"Failed to fetch playlist: {str(e)}")


class PlaylistSelectorDialog(QDialog):
    """Dialog for selecting videos from a playlist"""
    
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.selected_indices = []
        self.videos = []
        
        self.setup_ui()
        self.fetch_playlist_info()
        
    def setup_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Select Videos to Download")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Select Videos from Playlist")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title_label)
        
        # Status label
        self.status_label = QLabel("Loading playlist...")
        self.status_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Video list
        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
        """)
        self.video_list.setVisible(False)
        layout.addWidget(self.video_list)
        
        # Selection buttons
        select_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setVisible(False)
        select_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        self.deselect_all_btn.setVisible(False)
        select_layout.addWidget(self.deselect_all_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 11px; color: #666;")
        self.info_label.setVisible(False)
        layout.addWidget(self.info_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        self.style_button(self.cancel_btn, "#999")
        button_layout.addWidget(self.cancel_btn)
        
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.setFixedWidth(150)
        self.download_btn.clicked.connect(self.accept_selection)
        self.download_btn.setEnabled(False)
        self.style_button(self.download_btn, "#667eea")
        button_layout.addWidget(self.download_btn)
        
        layout.addLayout(button_layout)
        
    def style_button(self, button, color):
        """Apply button styling"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:disabled {{
                background-color: #ccc;
            }}
        """)
        
    def fetch_playlist_info(self):
        """Fetch playlist information in background"""
        self.thread = QThread()
        self.worker = PlaylistInfoWorker(self.url)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_playlist_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.progress.connect(self.on_progress)
        
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
        
    def on_progress(self, message):
        """Update progress message"""
        self.status_label.setText(message)
        
    def on_playlist_loaded(self, videos):
        """Handle playlist info loaded"""
        self.videos = videos
        
        # Hide progress
        self.progress_bar.setVisible(False)
        
        status_text = f"Pronađeno {len(videos)} pesama"
        if len(videos) == 50:
            status_text += " (Ograničeno na prvih 50)"
        self.status_label.setText(status_text)
        
        # Show video list
        self.video_list.setVisible(True)
        self.select_all_btn.setVisible(True)
        self.deselect_all_btn.setVisible(True)
        self.info_label.setVisible(True)
        
        # Populate list
        for idx, video in enumerate(videos):
            duration = self.format_duration(video['duration'])
            item_text = f"{idx + 1}. {video['title']} ({duration})"
            
            item = QListWidgetItem(item_text)
            
            # Check if video is available
            is_available = video.get('id') and video.get('availability', '') != 'private'
            
            if is_available:
                # Available - checkbox enabled
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
            else:
                # Unavailable - strikethrough and disabled
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
                item.setForeground(Qt.GlobalColor.gray)
                item_text = f"{idx + 1}. ❌ {video['title']} (Nedostupno)"
                item.setText(item_text)
                
            self.video_list.addItem(item)
            
        self.update_selection_info()
        self.download_btn.setEnabled(True)
        
        # Connect selection change
        self.video_list.itemChanged.connect(self.update_selection_info)
        
        # Cleanup thread
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
            
    def on_error(self, error_msg):
        """Handle error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error loading playlist")
        QMessageBox.critical(self, "Error", error_msg)
        self.reject()
        
    def format_duration(self, seconds):
        """Format duration in seconds to MM:SS"""
        if not seconds or seconds == 0:
            return "Unknown"
        try:
            seconds = int(seconds)
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins:02d}:{secs:02d}"
        except:
            return "Unknown"
        
    def select_all(self):
        """Select all available videos"""
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            # Only check if checkable (available videos)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Checked)
            
    def deselect_all(self):
        """Deselect all available videos"""
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            # Only uncheck if checkable (available videos)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Unchecked)
            
    def update_selection_info(self):
        """Update selection count"""
        total_available = sum(1 for i in range(self.video_list.count()) 
                             if self.video_list.item(i).flags() & Qt.ItemFlag.ItemIsUserCheckable)
        count = sum(1 for i in range(self.video_list.count()) 
                   if self.video_list.item(i).flags() & Qt.ItemFlag.ItemIsUserCheckable
                   and self.video_list.item(i).checkState() == Qt.CheckState.Checked)
        unavailable = len(self.videos) - total_available
        
        info_text = f"Odabrano: {count} od {total_available} dostupnih"
        if unavailable > 0:
            info_text += f" ({unavailable} nedostupno)"
        self.info_label.setText(info_text)
        self.download_btn.setEnabled(count > 0)
        
    def accept_selection(self):
        """Accept and return selected indices"""
        self.selected_indices = []
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            # Only include checked and available items
            if (item.flags() & Qt.ItemFlag.ItemIsUserCheckable and 
                item.checkState() == Qt.CheckState.Checked):
                self.selected_indices.append(i)
                
        if not self.selected_indices:
            QMessageBox.warning(self, "Nema Odabira", "Molim te odaberi bar jednu pesmu")
            return
            
        self.accept()
        
    def get_selected_indices(self):
        """Get list of selected video indices"""
        return self.selected_indices