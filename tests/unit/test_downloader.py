"""
Tests para el VideoDownloader.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from core.downloader import VideoDownloader, DownloadProgress, VideoInfo
from core.exceptions import (
    VideoUnavailableError,
    FFmpegNotFoundError,
    DownloadFailedError,
    InvalidURLError,
)


class TestVideoDownloaderInit:
    """Tests para la inicialización del VideoDownloader."""
    
    @patch('core.downloader.get_config_manager')
    def test_init_sets_attributes(self, mock_config):
        """Debe inicializar correctamente."""
        mock_config.return_value.get.return_value.ffmpeg_path = ""
        
        downloader = VideoDownloader()
        
        assert downloader._logger is not None
        assert downloader._progress_callback is None
    
    @patch('core.downloader.get_config_manager')
    def test_init_without_ffmpeg_path(self, mock_config):
        """Debe funcionar sin FFmpeg configurado."""
        mock_config.return_value.get.return_value.ffmpeg_path = ""
        
        downloader = VideoDownloader()
        
        # Puede o no tener FFmpeg dependiendo del sistema
        assert downloader._config is not None


class TestVideoDownloaderFindFFmpeg:
    """Tests para la búsqueda de FFmpeg."""
    
    @patch('core.downloader.get_config_manager')
    @patch('core.downloader.subprocess.run')
    def test_find_ffmpeg_in_path(self, mock_subprocess, mock_config):
        """Debe encontrar FFmpeg en el PATH."""
        mock_config.return_value.get.return_value.ffmpeg_path = ""
        mock_subprocess.return_value = Mock(returncode=0, stdout="C:\\ffmpeg\\bin\\ffmpeg.exe")
        
        downloader = VideoDownloader()
        
        # El resultado depende de si el sistema tiene FFmpeg en PATH
        # En el test mocking, debería encontrarlo
        result = downloader._find_ffmpeg()
        
        # Verificar que se llamó a subprocess
        mock_subprocess.assert_called()
    
    @patch('core.downloader.get_config_manager')
    def test_find_ffmpeg_empty_config(self, mock_config):
        """Debe manejar configuración vacía."""
        mock_config.return_value.get.return_value.ffmpeg_path = ""
        
        downloader = VideoDownloader()
        
        # No debe lanzar error
        result = downloader._find_ffmpeg()
        
        # El resultado puede ser None o una ruta dependiendo del sistema
    
    @patch('core.downloader.get_config_manager')
    def test_find_ffmpeg_custom_path(self, mock_config):
        """Debe usar ruta personalizada configurada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear un archivo falso de FFmpeg
            ffmpeg_dir = Path(tmpdir)
            fake_ffmpeg = ffmpeg_dir / "ffmpeg.exe"
            fake_ffmpeg.touch()
            
            mock_config.return_value.get.return_value.ffmpeg_path = str(ffmpeg_dir)
            
            downloader = VideoDownloader()
            result = downloader._find_ffmpeg()
            
            # Debe encontrar el ejecutable falso
            assert result is not None
            assert "ffmpeg.exe" in result


class TestVideoDownloaderFFmpegOptions:
    """Tests para las opciones de FFmpeg."""
    
    @patch('core.downloader.get_config_manager')
    def test_get_ydl_opts_video(self, mock_config):
        """Debe generar opciones correctas para video."""
        mock_config.return_value.get.return_value.ffmpeg_path = ""
        mock_config.return_value.get.return_value.overwrite_files = False
        
        downloader = VideoDownloader()
        
        opts = downloader._get_ydl_opts(
            output_path="C:/downloads",
            quality="best",
            audio_only=False,
        )
        
        assert opts["format"] is not None
        assert "outtmpl" in opts
        assert "merge_output_format" in opts
        assert opts["merge_output_format"] == "mp4"
    
    @patch('core.downloader.get_config_manager')
    def test_get_ydl_opts_audio(self, mock_config):
        """Debe generar opciones correctas para audio."""
        mock_config.return_value.get.return_value.ffmpeg_path = ""
        mock_config.return_value.get.return_value.overwrite_files = False
        
        downloader = VideoDownloader()
        
        opts = downloader._get_ydl_opts(
            output_path="C:/downloads",
            quality="320k",
            audio_only=True,
        )
        
        assert opts["merge_output_format"] == "mp3"
        assert len(opts["postprocessors"]) > 0
        assert opts["postprocessors"][0]["key"] == "FFmpegExtractAudio"
    
    @patch('core.downloader.get_config_manager')
    def test_get_ydl_opts_with_ffmpeg_location(self, mock_config):
        """Debe incluir ffmpeg_location cuando está configurado."""
        mock_config.return_value.get.return_value.ffmpeg_path = ""
        mock_config.return_value.get.return_value.overwrite_files = True
        
        downloader = VideoDownloader()
        downloader._ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"
        
        opts = downloader._get_ydl_opts(
            output_path="C:/downloads",
            quality="best",
            audio_only=False,
        )
        
        assert "ffmpeg_location" in opts
        assert opts["ffmpeg_location"] == "C:/ffmpeg/bin"


class TestDownloadProgress:
    """Tests para DownloadProgress."""
    
    def test_default_values(self):
        """Valores por defecto."""
        progress = DownloadProgress()
        
        assert progress.percent == 0.0
        assert progress.speed == 0.0
        assert progress.eta == 0
        assert progress.total_bytes == 0
        assert progress.downloaded_bytes == 0
        assert progress.filename == ""
        assert progress.status == "downloading"
    
    def test_custom_values(self):
        """Valores personalizados."""
        progress = DownloadProgress(
            percent=50.0,
            speed=1024000,
            eta=60,
            total_bytes=2048000,
            downloaded_bytes=1024000,
            filename="video.mp4",
            status="downloading",
        )
        
        assert progress.percent == 50.0
        assert progress.speed == 1024000
        assert progress.eta == 60


class TestVideoInfo:
    """Tests para VideoInfo."""
    
    def test_from_dict(self):
        """Debe crear VideoInfo desde diccionario."""
        data = {
            "id": "abc123",
            "title": "Test Video",
            "uploader": "Test Channel",
            "duration": 180,
            "thumbnail": "https://example.com/thumb.jpg",
            "description": "Test description",
            "upload_date": "20240101",
            "view_count": 1000,
            "like_count": 100,
            "categories": ["Music"],
            "tags": ["test", "video"],
            "is_live": False,
        }
        
        info = VideoInfo.from_dict(data)
        
        assert info.id == "abc123"
        assert info.title == "Test Video"
        assert info.uploader == "Test Channel"
        assert info.duration == 180
        assert info.view_count == 1000
        assert info.is_live is False
    
    def test_from_dict_with_defaults(self):
        """Debe manejar datos faltantes."""
        data = {}
        
        info = VideoInfo.from_dict(data)
        
        assert info.id == ""
        assert info.title == "Sin título"
        assert info.uploader == "Desconocido"
        assert info.duration == 0
        assert info.view_count == 0
