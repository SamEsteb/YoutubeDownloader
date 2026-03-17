# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for YouTube Downloader

import sys
from pathlib import Path

# Rutas del proyecto
src_dir = Path(SPECPATH) / "src"
app_dir = src_dir / "app"

block_cipher = None


a = Analysis(
    [src_dir / "main.py"],
    pathex=[
        str(src_dir),
        str(app_dir),
    ],
    binaries=[],
    datas=[
        (app_dir / "gui" / "theme.py", "app/gui"),
    ],
    hiddenimports=[
        # Core modules
        "core.validator",
        "core.exceptions",
        "core.config_manager",
        "core.downloader",
        # GUI modules
        "gui.theme",
        "gui.main_window",
        "gui.download_tab",
        "gui.settings_tab",
        # Utils
        "utils.logger",
        # Third party
        "yt_dlp",
        "customtkinter",
        "darkdetect",
        "PIL",
        "PIL.Image",
        # Tkinter es requerido por customtkinter
        "tkinter",
        "tkinter.ttk",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # No excluir tkinter - es necesario para customtkinter
        # "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "IPython",
        "jupyter",
        "pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="YouTubeDownloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="Assets/logo.ico",
    version="version_info.txt",
)
