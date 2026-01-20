"""
PyInstaller Spec File
Advanced configuration for creating Windows executable
"""

# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Project root directory
ROOT = Path(SPECPATH)

block_cipher = None

# Collect all necessary data files
datas = [
    # Add any resource files here
    # ('resources', 'resources'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'mutagen.mp3',
    'mutagen.mp4',
    'mutagen.id3',
    'mutagen.easyid3',
]

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[str(ROOT)],
    binaries=[
        # Add yt-dlp and ffmpeg executables
        # ('yt-dlp.exe', '.'),
        # ('ffmpeg.exe', '.'),
    ],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ (Python zip archive)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# EXE (Executable)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AudioDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='resources/icons/app.ico',  # Add your app icon
)

# For one-folder distribution, use this instead:
"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AudioDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AudioDownloader',
)
"""
