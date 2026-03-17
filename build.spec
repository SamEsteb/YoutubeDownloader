# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for YouTube Downloader
# Generated for PyInstaller 6.x

import sys
from pathlib import Path

# Agregar el directorio src al path
src_dir = Path(SPECPATH) / "src"

block_cipher = None


# Archivos de datos (recursos)
datas = [
    (src_dir / "app" / "gui" / "theme.py", "app/gui"),
]


a = Analysis(
    [src_dir / "main.py"],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "yt_dlp",
        "customtkinter",
        "darkdetect",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "IPython",
        "jupyter",
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
    console=False,  # False = GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="Assets/logo.ico",  # Usar el icono existente
    version="version_info.txt",  # Crear archivo de versión
)
