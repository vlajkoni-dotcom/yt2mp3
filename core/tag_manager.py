"""
Core Module - Tag Manager
Handles MP3/M4A metadata operations using mutagen, PRESERVING existing cover art
"""

from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, APIC


class TagManager:
    """Manages audio file metadata tags while preserving existing cover art"""
    
    def __init__(self):
        pass
        
    def write_tags(self, file_path, metadata, cover_path=None):
        """
        Write metadata tags to audio file.
        If cover_path is None, preserves existing cover art.
        """
        file_path = Path(file_path)
        
        try:
            if file_path.suffix.lower() == '.mp3':
                return self._write_mp3_tags(file_path, metadata, cover_path)
            elif file_path.suffix.lower() == '.m4a':
                return self._write_m4a_tags(file_path, metadata, cover_path)
            else:
                return False
        except Exception as e:
            print(f"Error writing tags: {e}")
            return False
            
    def _write_mp3_tags(self, file_path, metadata, cover_path=None):
        """Write tags to MP3 file, preserving or replacing cover art"""
        try:
            audio = MP3(file_path, ID3=ID3)
            
            if audio.tags is None:
                audio.add_tags()

            # Sačuvaj postojeći cover art ako ne dodeljujemo novi
            existing_cover = None
            if cover_path is None and 'APIC:' in audio.tags:
                existing_cover = audio.tags['APIC:']

            # Obriši samo osnovne frejmove
            for frame in ['TIT2', 'TPE1', 'TALB', 'TRCK']:
                if frame in audio.tags:
                    del audio.tags[frame]

            # Postavi osnovne tagove
            if metadata.get('title') and metadata['title'].strip():
                audio.tags.add(TIT2(encoding=3, text=metadata['title'].strip()))
            if metadata.get('artist') and metadata['artist'].strip():
                audio.tags.add(TPE1(encoding=3, text=metadata['artist'].strip()))
            if metadata.get('album') and metadata['album'].strip():
                audio.tags.add(TALB(encoding=3, text=metadata['album'].strip()))
            if metadata.get('tracknumber'):
                try:
                    track_num = str(int(metadata['tracknumber']))
                    audio.tags.add(TRCK(encoding=3, text=track_num))
                except (ValueError, TypeError):
                    pass

            # Rukuj cover art-om
            if cover_path and Path(cover_path).exists():
                try:
                    with open(cover_path, "rb") as img_file:
                        cover_data = img_file.read()
                    mime = "image/jpeg"
                    if cover_path.lower().endswith(".png"):
                        mime = "image/png"
                    audio.tags.add(APIC(
                        encoding=3,
                        mime=mime,
                        type=3,  # Front cover
                        desc='Cover',
                        data=cover_data
                    ))
                except Exception as e:
                    print(f"Warning: Could not embed new cover art: {e}")
            elif existing_cover:
                # Vrati sačuvani cover art
                audio.tags.add(existing_cover)

            audio.save()
            return True

        except Exception as e:
            print(f"Error writing MP3 tags: {e}")
            return False
            
    def _write_m4a_tags(self, file_path, metadata, cover_path=None):
        """Write tags to M4A file, preserving or replacing cover art"""
        try:
            audio = MP4(file_path)
            
            # Sačuvaj postojeći cover
            existing_cover = None
            if cover_path is None and 'covr' in audio:
                existing_cover = audio['covr']

            # Osnovni tagovi
            if metadata.get('title') and metadata['title'].strip():
                audio['\xa9nam'] = [metadata['title'].strip()]
            if metadata.get('artist') and metadata['artist'].strip():
                audio['\xa9ART'] = [metadata['artist'].strip()]
            if metadata.get('album') and metadata['album'].strip():
                audio['\xa9alb'] = [metadata['album'].strip()]
            if metadata.get('tracknumber'):
                try:
                    track_num = int(metadata['tracknumber'])
                    audio['trkn'] = [(track_num, 0)]
                except (ValueError, TypeError):
                    pass

            # Cover art
            if cover_path and Path(cover_path).exists():
                try:
                    with open(cover_path, "rb") as img_file:
                        cover_data = img_file.read()
                    from mutagen.mp4 import MP4Cover
                    fmt = MP4Cover.FORMAT_JPEG
                    if cover_path.lower().endswith(".png"):
                        fmt = MP4Cover.FORMAT_PNG
                    audio['covr'] = [MP4Cover(cover_data, imageformat=fmt)]
                except Exception as e:
                    print(f"Warning: Could not embed new cover art in M4A: {e}")
            elif existing_cover:
                audio['covr'] = existing_cover

            audio.save()
            return True

        except Exception as e:
            print(f"Error writing M4A tags: {e}")
            return False
            
    def read_tags(self, file_path):
        """Read basic metadata (no cover art)"""
        file_path = Path(file_path)
        metadata = {}
        
        try:
            if file_path.suffix.lower() == '.mp3':
                from mutagen.easyid3 import EasyID3
                audio = EasyID3(file_path)
                for key in ['title', 'artist', 'album', 'tracknumber']:
                    if key in audio:
                        metadata[key] = audio[key][0]
            elif file_path.suffix.lower() == '.m4a':
                audio = MP4(file_path)
                if '\xa9nam' in audio:
                    metadata['title'] = audio['\xa9nam'][0]
                if '\xa9ART' in audio:
                    metadata['artist'] = audio['\xa9ART'][0]
                if '\xa9alb' in audio:
                    metadata['album'] = audio['\xa9alb'][0]
                if 'trkn' in audio:
                    metadata['tracknumber'] = str(audio['trkn'][0][0])
        except Exception as e:
            print(f"Info: Could not read existing tags: {e}")
            
        return metadata