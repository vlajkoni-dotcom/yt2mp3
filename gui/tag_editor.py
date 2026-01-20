"""
GUI Module - Tag Editor Dialog
Modal dialog for editing MP3 tags after download
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QPushButton, QLabel, QSpinBox,
    QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from core.tag_manager import TagManager
from utils.file_utils import sanitize_filename


class TagEditorDialog(QDialog):
    """Dialog for editing audio file tags"""
    
    def __init__(self, file_path, metadata, track_number=None, parent=None):
        super().__init__(parent)
        self.file_path = Path(file_path)
        self.metadata = metadata.copy()
        self.track_number = track_number
        self.tag_manager = TagManager()
        self.final_path = self.file_path
        
        # Read existing tags from file (DON'T write, just read!)
        try:
            existing_tags = self.tag_manager.read_tags(self.file_path)
            if existing_tags:
                # Merge existing tags with provided metadata
                for key, value in existing_tags.items():
                    if value:
                        self.metadata[key] = value
        except Exception as e:
            print(f"Could not read existing tags: {e}")
            # Use provided metadata as-is
        
        self.setup_ui()
        self.populate_fields()
        self.connect_signals()
        
    def setup_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Audio Tags")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Edit Audio File Metadata")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title_label)
        
        # Current file info
        file_info = QLabel(f"File: {self.file_path.name}")
        file_info.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(file_info)
        
        # Form layout for metadata fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Artist field
        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("Enter artist name...")
        self.style_input(self.artist_input)
        form_layout.addRow("Artist:", self.artist_input)
        
        # Title field
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter song title...")
        self.style_input(self.title_input)
        form_layout.addRow("Title:", self.title_input)
        
        # Album field
        self.album_input = QLineEdit()
        self.album_input.setPlaceholderText("Enter album name...")
        self.style_input(self.album_input)
        form_layout.addRow("Album:", self.album_input)
        
        # Track number field
        self.track_spin = QSpinBox()
        self.track_spin.setMinimum(0)
        self.track_spin.setMaximum(999)
        self.track_spin.setSpecialValueText("Not set")
        self.style_input(self.track_spin)
        form_layout.addRow("Track #:", self.track_spin)
        
        layout.addLayout(form_layout)
        
        # Filename preview
        preview_label = QLabel("Filename Preview:")
        preview_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333; margin-top: 10px;")
        layout.addWidget(preview_label)
        
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.filename_preview.setWordWrap(True)
        layout.addWidget(self.filename_preview)
        
        # Rename checkbox
        self.rename_checkbox = QCheckBox("Rename file after save")
        self.rename_checkbox.setChecked(True)
        self.rename_checkbox.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.rename_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(100)
        self.style_button(self.cancel_btn, "#999")
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedWidth(100)
        self.save_btn.setDefault(True)
        self.style_button(self.save_btn, "#667eea")
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
    def style_input(self, widget):
        """Apply consistent styling to input widgets"""
        widget.setStyleSheet("""
            QLineEdit, QSpinBox {
                padding: 6px;
                font-size: 12px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #667eea;
            }
        """)
        
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
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """)
        
    def darken_color(self, hex_color, factor=0.9):
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        
        # Handle 3-char hex (#999 -> #999999)
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            # Fallback to original color if parsing fails
            return f"#{hex_color}"
        
    def populate_fields(self):
        """Populate fields with metadata"""
        self.artist_input.setText(self.metadata.get("artist", ""))
        self.title_input.setText(self.metadata.get("title", ""))
        self.album_input.setText(self.metadata.get("album", ""))
        
        if self.track_number:
            self.track_spin.setValue(self.track_number)
            
        self.update_filename_preview()
        
    def connect_signals(self):
        """Connect signals"""
        self.artist_input.textChanged.connect(self.update_filename_preview)
        self.title_input.textChanged.connect(self.update_filename_preview)
        self.save_btn.clicked.connect(self.save_tags)
        self.cancel_btn.clicked.connect(self.reject)
        
    def update_filename_preview(self):
        """Update filename preview based on current inputs"""
        artist = self.artist_input.text().strip()
        title = self.title_input.text().strip()
        
        # Generate filename
        if artist and title:
            filename = f"{artist} - {title}"
        elif title:
            filename = title
        elif artist:
            filename = artist
        else:
            filename = self.file_path.stem
            
        # Sanitize and add extension
        filename = sanitize_filename(filename)
        filename = f"{filename}{self.file_path.suffix}"
        
        self.filename_preview.setText(filename)
        
    def save_tags(self):
        """Save tags to file and optionally rename"""
        try:
            # Update metadata dictionary
            self.metadata["artist"] = self.artist_input.text().strip()
            self.metadata["title"] = self.title_input.text().strip()
            self.metadata["album"] = self.album_input.text().strip()
            
            track_num = self.track_spin.value()
            if track_num > 0:
                self.metadata["tracknumber"] = str(track_num)
            
            # Write tags using tag manager
            success = self.tag_manager.write_tags(self.file_path, self.metadata)
            
            if not success:
                QMessageBox.warning(self, "Error", "Failed to write tags to file")
                return
                
            # Rename file if checkbox is checked
            if self.rename_checkbox.isChecked():
                new_filename = self.filename_preview.text()
                new_path = self.file_path.parent / new_filename
                
                # Avoid overwriting existing files
                counter = 1
                while new_path.exists() and new_path != self.file_path:
                    stem = Path(new_filename).stem
                    ext = Path(new_filename).suffix
                    new_filename = f"{stem} ({counter}){ext}"
                    new_path = self.file_path.parent / new_filename
                    counter += 1
                
                # Rename
                if new_path != self.file_path:
                    try:
                        self.file_path.rename(new_path)
                        self.final_path = new_path
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "Rename Error",
                            f"Tags saved but file rename failed: {str(e)}"
                        )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save tags: {str(e)}"
            )
            
    def get_metadata(self):
        """Get updated metadata"""
        return self.metadata
        
    def get_final_path(self):
        """Get final file path (after potential rename)"""
        return self.final_path