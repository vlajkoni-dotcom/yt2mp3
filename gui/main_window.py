"""
GUI Module - Ultimate Main Window
Klik na pesmu = Edit Tags
Play dugme = Pusti pesmu
Sve funkcije kompletne
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QProgressBar, QTableWidget,
    QTableWidgetItem, QLabel, QComboBox, QMessageBox,
    QHeaderView, QFileDialog, QAbstractItemView
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QFont, QDesktopServices, QIcon
from pathlib import Path
import subprocess
import yt_dlp
import sys
import traceback

from core.download_manager import DownloadManager
from gui.tag_editor import TagEditorDialog
from gui.playlist_selector import PlaylistSelectorDialog


# Debug: catch all unhandled exceptions
def excepthook(exc_type, exc_value, exc_traceback):
    print("❌ Unhandled exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = excepthook


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.download_manager = DownloadManager()
        self.download_folder = Path.home() / "Music"
        self.download_folder.mkdir(parents=True, exist_ok=True)
        self.downloaded_files = []  # Store file paths
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Yt 2 Mp3 - v1.0")
        self.setMinimumSize(1100, 750)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_header(main_layout)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        self.create_url_section(content_layout)
        self.create_folder_section(content_layout)
        self.create_progress_section(content_layout)
        self.create_files_table(content_layout)
        
        main_layout.addWidget(content_widget)
        
        # Footer
        self.create_footer(main_layout)
        
    def create_header(self, layout):
        """Create header section"""
        header_container = QWidget()
        header_container.setFixedHeight(80)
        header_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-bottom: 3px solid #5568d3;
            }
        """)
        
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("🎵 Yt 2 Mp3")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        subtitle = QLabel("YouTube to MP3 Converter • v1.0")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.95);
                font-size: 13px;
                background: transparent;
                font-weight: 500;
            }
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_container)
    
    def create_footer(self, layout):
        """Create footer with credits"""
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 2px solid #e0e0e0;
            }
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        
        credits_label = QLabel("Created by Vladimir Jevtić & Claude AI © 2026")
        credits_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
                background: transparent;
            }
        """)
        footer_layout.addWidget(credits_label)
        
        footer_layout.addStretch()
        
        version_label = QLabel("Version 1.0")
        version_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
                background: transparent;
                font-weight: bold;
            }
        """)
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer)
        
    def create_ad_section(self, layout):
        """Legacy method - replaced by create_header"""
        pass
        
    def create_url_section(self, layout):
        """Create URL input and download controls"""
        title_label = QLabel("📥 Download Audio from YouTube")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title_label)
        
        input_layout = QHBoxLayout()
        
        url_label = QLabel("URL:")
        url_label.setFixedWidth(50)
        url_label.setStyleSheet("font-weight: bold;")
        input_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Unesi YouTube URL (video ili playlista)...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        input_layout.addWidget(self.url_input)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "m4a"])
        self.format_combo.setFixedWidth(80)
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
            }
        """)
        input_layout.addWidget(self.format_combo)
        
        # Type selector (Single/Playlist only)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Single", "Playlist"])  # ⬅️ Samo ova dva
        self.type_combo.setFixedWidth(90)
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
            }
        """)
        input_layout.addWidget(self.type_combo)
        
        self.download_btn = QPushButton("⬇️ Download")
        self.download_btn.setFixedWidth(130)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
            QPushButton:pressed {
                background-color: #4c5fc7;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        input_layout.addWidget(self.download_btn)
        
        layout.addLayout(input_layout)
        
    def create_folder_section(self, layout):
        """Create folder selection section"""
        folder_layout = QHBoxLayout()
        
        folder_icon = QLabel("📁")
        folder_icon.setFixedWidth(30)
        folder_icon.setStyleSheet("font-size: 18px;")
        folder_layout.addWidget(folder_icon)
        
        self.folder_display = QLabel(str(self.download_folder))
        self.folder_display.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f8f9fa;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 12px;
                color: #495057;
            }
        """)
        folder_layout.addWidget(self.folder_display)
        
        self.browse_btn = QPushButton("📂 Browse")
        self.browse_btn.setFixedWidth(100)
        self.browse_btn.clicked.connect(self.browse_folder)
        self.style_small_button(self.browse_btn, "#764ba2")
        folder_layout.addWidget(self.browse_btn)
        
        self.open_folder_btn = QPushButton("🗂️ Open Folder")
        self.open_folder_btn.setFixedWidth(120)
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        self.style_small_button(self.open_folder_btn, "#28a745")
        folder_layout.addWidget(self.open_folder_btn)
        
        layout.addLayout(folder_layout)
        
    def style_small_button(self, button, color):
        """Style for small utility buttons"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """)
        
    def create_progress_section(self, layout):
        """Create progress indicators"""
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        
        self.track_label = QLabel("✅ Spremno za download")
        self.track_label.setStyleSheet("font-size: 12px; color: #28a745; font-weight: bold;")
        progress_layout.addWidget(self.track_label)
        
        self.track_progress = QProgressBar()
        self.track_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 6px;
                text-align: center;
                height: 24px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #667eea;
                border-radius: 4px;
            }
        """)
        self.track_progress.setVisible(False)
        progress_layout.addWidget(self.track_progress)
        
        self.playlist_label = QLabel("")
        self.playlist_label.setStyleSheet("font-size: 12px; color: #764ba2; font-weight: bold;")
        self.playlist_label.setVisible(False)
        progress_layout.addWidget(self.playlist_label)
        
        self.playlist_progress = QProgressBar()
        self.playlist_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 6px;
                text-align: center;
                height: 24px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #764ba2;
                border-radius: 4px;
            }
        """)
        self.playlist_progress.setVisible(False)
        progress_layout.addWidget(self.playlist_progress)
        
        layout.addWidget(progress_widget)
        
    def create_files_table(self, layout):
        """Create downloaded files table with play button"""
        # Header with buttons
        header_layout = QHBoxLayout()
        
        table_label = QLabel("🎵 Downloaded Files")
        table_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        header_layout.addWidget(table_label)
        
        header_layout.addStretch()
        
        self.edit_btn = QPushButton("✏️ Edit Tags")
        self.edit_btn.setFixedWidth(110)
        self.edit_btn.clicked.connect(self.edit_selected_tags)
        self.edit_btn.setEnabled(False)
        self.style_action_button(self.edit_btn, "#667eea")
        header_layout.addWidget(self.edit_btn)
        
        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.setFixedWidth(90)
        self.play_btn.clicked.connect(self.play_selected)
        self.play_btn.setEnabled(False)
        self.style_action_button(self.play_btn, "#28a745")
        header_layout.addWidget(self.play_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(4)
        self.files_table.setHorizontalHeaderLabels(["Artist", "Title", "Album", "Filename"])
        
        self.files_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ddd;
                border-radius: 6px;
                gridline-color: #e0e0e0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #ddd;
                font-weight: bold;
                color: #495057;
            }
        """)
        
        header = self.files_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.files_table.setColumnWidth(0, 200)
        self.files_table.setColumnWidth(1, 250)
        self.files_table.setColumnWidth(2, 180)
        
        self.files_table.setAlternatingRowColors(True)
        self.files_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.files_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.files_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Double-click to edit tags
        self.files_table.cellDoubleClicked.connect(self.on_table_double_click)
        self.files_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.files_table)
        
    def style_action_button(self, button, color):
        """Style for action buttons"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 6px 12px;
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
        
    def connect_signals(self):
        """Connect signals and slots"""
        self.download_btn.clicked.connect(self.start_download)
        self.url_input.returnPressed.connect(self.start_download)
        
        self.download_manager.download_started.connect(self.on_download_started)
        self.download_manager.progress_updated.connect(self.on_progress_updated)
        self.download_manager.download_completed.connect(self.on_download_completed)
        self.download_manager.playlist_progress.connect(self.on_playlist_progress)
        self.download_manager.error_occurred.connect(self.on_error)
        self.download_manager.all_downloads_finished.connect(self.on_all_finished)
        self.download_manager.file_exists.connect(self.on_file_exists)
        
    def browse_folder(self):
        """Browse for download folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Izaberi folder za download",
            str(self.download_folder)
        )
        
        if folder:
            self.download_folder = Path(folder)
            self.folder_display.setText(str(self.download_folder))
            self.download_manager.set_download_folder(self.download_folder)
                
    def open_download_folder(self):
        """Open download folder in file explorer"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.download_folder)))
        
    def is_video_available(self, url):
        """Proveri da li je video dostupan bez download-a"""
        try:
            ydl_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return False
                # Proveri da li je dostupan
                if info.get('availability', '') == 'private':
                    return False
                if 'unavailable' in str(info.get('title', '')).lower():
                    return False
                if 'terminated' in str(info.get('uploader', '')).lower():
                    return False
                return True
        except:
            return False
        
    def start_download(self):
        """Start download process"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Input Required", "Molim te unesi URL")
            return
            
        if not ("youtube.com" in url or "youtu.be" in url):
            QMessageBox.warning(self, "Invalid URL", "Molim te unesi validan YouTube URL")
            return
        
        type_choice = self.type_combo.currentText()
        audio_format = self.format_combo.currentText()
        selected_indices = None
        
        if type_choice == "Single":
            # Ako URL sadrži &list=, izdvoji samo v=
            if "&list=" in url:
                # Izdvoji v= parametar
                v_part = url.split("v=")[1].split("&")[0]
                clean_url = f"https://www.youtube.com/watch?v={v_part}"
                url = clean_url
            
            # Proveri da li je video dostupan
            if not self.is_video_available(url):
                QMessageBox.critical(self, "Video Nedostupan", "Ovaj video nije dostupan za download.\n\nMolim te izaberi drugi URL ili koristi 'Playlist' režim.")
                return
                
            mode = "single"
            self._start_download_with_mode(url, audio_format, mode, None)
            
        elif type_choice == "Playlist":
            dialog = PlaylistSelectorDialog(url, self)
            if dialog.exec():
                selected_indices = dialog.get_selected_indices()
                if selected_indices:
                    self._start_download_with_mode(url, audio_format, "playlist", selected_indices)
                else:
                    QMessageBox.information(self, "No Selection", "Nema izabranih pesama.")
            else:
                self.track_label.setText("✅ Spremno za download")
                
    def _start_download_with_mode(self, url, audio_format, mode, selected_indices):
        """Helper to start download with proper UI state"""
        self.download_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.type_combo.setEnabled(False)
        self.browse_btn.setEnabled(False)
    
        self.track_progress.setVisible(True)
        self.track_progress.setValue(0)
        self.track_label.setText("⏳ Starting download...")
    
        try:
            self.download_manager.start_download(url, audio_format, mode, selected_indices)
        except Exception as e:
            import traceback
            print("❌ ERROR IN START DOWNLOAD:")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.on_all_finished()
        
    def on_download_started(self, title):
        """Handle download started signal"""
        self.track_label.setText(f"⬇ Downloading: {title}")
        
    def on_progress_updated(self, progress):
        """Update progress bar"""
        self.track_progress.setValue(int(progress))
        
    def on_playlist_progress(self, current, total):
        """Update playlist progress"""
        self.playlist_label.setText(f"📋 Playlist: {current} od {total}")
        self.playlist_label.setVisible(True)
        self.playlist_progress.setVisible(True)
        self.playlist_progress.setMaximum(total)
        self.playlist_progress.setValue(current)
        
    def on_download_completed(self, file_path, metadata, track_number):
        """Handle completed download - add to table WITHOUT touching tags"""
        self.track_label.setText(f"✅ Kompletno: {Path(file_path).name}")
        self.track_progress.setValue(100)
        self.add_file_to_table(metadata, file_path)
            
    def on_file_exists(self, filename, filepath, metadata, track_number):
        """Handle file already exists"""
        reply = QMessageBox.question(
            self,
            "Fajl Već Postoji",
            f"Fajl '{filename}' već postoji u folderu.\n\nŽeliš da ga preskoči?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.No:
            self.add_file_to_table(metadata, filepath)
        
    def on_error(self, error_msg):
        """Handle error"""
        if "rate" in error_msg.lower() and "limit" in error_msg.lower():
            QMessageBox.critical(
                self, 
                "YouTube Rate Limit", 
                "YouTube je ograničio preuzimanja. Sačekaj 30-60 minuta i probaj ponovo.\n\n" + error_msg
            )
            self.on_all_finished()
        elif not error_msg.startswith("Skipped"):
            self.track_label.setText(f"❌ Greška: {error_msg}")
        else:
            self.track_label.setText(error_msg)
        
    def on_all_finished(self):
        """Handle all downloads finished"""
        self.track_label.setText("✅ Svi download-i završeni!")
        self.track_progress.setVisible(False)
        self.playlist_label.setVisible(False)
        self.playlist_progress.setVisible(False)
        
        self.download_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.type_combo.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.url_input.clear()
        
    def add_file_to_table(self, metadata, file_path):
        """Add downloaded file to table"""
        row = self.files_table.rowCount()
        self.files_table.insertRow(row)
        
        artist = metadata.get("artist", "")
        title = metadata.get("title", "")
        album = metadata.get("album", "")
        filename = Path(file_path).name
        
        self.files_table.setItem(row, 0, QTableWidgetItem(artist))
        self.files_table.setItem(row, 1, QTableWidgetItem(title))
        self.files_table.setItem(row, 2, QTableWidgetItem(album))
        self.files_table.setItem(row, 3, QTableWidgetItem(filename))
        
        self.downloaded_files.append(Path(file_path))
        
    def on_table_double_click(self, row, column):
        """Handle double-click on table - edit tags"""
        if row < len(self.downloaded_files):
            file_path = self.downloaded_files[row]
            if file_path.exists():
                self.edit_tags(row, file_path)
            else:
                QMessageBox.warning(self, "File Not Found", f"Fajl nije pronađen: {file_path.name}")
                
    def on_selection_changed(self):
        """Enable/disable buttons based on selection"""
        has_selection = len(self.files_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.play_btn.setEnabled(has_selection)
        
    def edit_selected_tags(self):
        """Edit tags for selected row"""
        current_row = self.files_table.currentRow()
        if current_row >= 0 and current_row < len(self.downloaded_files):
            file_path = self.downloaded_files[current_row]
            if file_path.exists():
                self.edit_tags(current_row, file_path)
            else:
                QMessageBox.warning(self, "File Not Found", f"Fajl nije pronađen: {file_path.name}")
                
    def edit_tags(self, row, file_path):
        """Open tag editor for a file"""
        metadata = {
            'artist': self.files_table.item(row, 0).text() if self.files_table.item(row, 0) else "",
            'title': self.files_table.item(row, 1).text() if self.files_table.item(row, 1) else "",
            'album': self.files_table.item(row, 2).text() if self.files_table.item(row, 2) else "",
        }
        
        dialog = TagEditorDialog(str(file_path), metadata, None, self)
        if dialog.exec():
            updated_metadata = dialog.get_metadata()
            final_path = dialog.get_final_path()
            
            self.files_table.item(row, 0).setText(updated_metadata.get("artist", ""))
            self.files_table.item(row, 1).setText(updated_metadata.get("title", ""))
            self.files_table.item(row, 2).setText(updated_metadata.get("album", ""))
            self.files_table.item(row, 3).setText(Path(final_path).name)
            self.downloaded_files[row] = Path(final_path)
            
    def play_selected(self):
        """Play selected audio file"""
        current_row = self.files_table.currentRow()
        if current_row >= 0 and current_row < len(self.downloaded_files):
            file_path = self.downloaded_files[current_row]
            if file_path.exists():
                try:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_path)))
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Nije moguće pustiti pesmu: {str(e)}")
            else:
                QMessageBox.warning(self, "File Not Found", f"Fajl nije pronađen: {file_path.name}")