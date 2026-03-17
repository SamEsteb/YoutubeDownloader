"""
Tests para las excepciones personalizadas.
"""

import pytest

from core.exceptions import (
    YouTubeDownloaderError,
    InvalidURLError,
    VideoUnavailableError,
    FFmpegNotFoundError,
    DownloadFailedError,
    ConfigError,
    NetworkError,
    PlaylistError,
)


class TestYouTubeDownloaderError:
    """Tests para la excepción base."""
    
    def test_base_exception(self):
        """La excepción base debe funcionar."""
        with pytest.raises(YouTubeDownloaderError):
            raise YouTubeDownloaderError("Test error")
    
    def test_error_message(self):
        """El mensaje debe ser correcto."""
        with pytest.raises(YouTubeDownloaderError) as exc_info:
            raise YouTubeDownloaderError("Error específico")
        assert str(exc_info.value) == "Error específico"


class TestInvalidURLError:
    """Tests para InvalidURLError."""
    
    def test_invalid_url_error(self):
        """Debe crearse con la URL."""
        with pytest.raises(InvalidURLError) as exc_info:
            raise InvalidURLError("https://example.com")
        assert "https://example.com" in str(exc_info.value)
        assert "inválida" in str(exc_info.value).lower()


class TestVideoUnavailableError:
    """Tests para VideoUnavailableError."""
    
    def test_video_unavailable_with_id(self):
        """Debe incluir el ID del video."""
        with pytest.raises(VideoUnavailableError) as exc_info:
            raise VideoUnavailableError("abc123")
        assert "abc123" in str(exc_info.value)
    
    def test_video_unavailable_with_reason(self):
        """Debe incluir la razón."""
        with pytest.raises(VideoUnavailableError) as exc_info:
            raise VideoUnavailableError("abc123", "Video privado")
        assert "abc123" in str(exc_info.value)
        assert "privado" in str(exc_info.value)


class TestFFmpegNotFoundError:
    """Tests para FFmpegNotFoundError."""
    
    def test_ffmpeg_error_message(self):
        """El mensaje debe indicar cómo resolver."""
        with pytest.raises(FFmpegNotFoundError) as exc_info:
            raise FFmpegNotFoundError()
        assert "FFmpeg" in str(exc_info.value)
        assert "instala" in str(exc_info.value).lower() or "instalar" in str(exc_info.value).lower()


class TestDownloadFailedError:
    """Tests para DownloadFailedError."""
    
    def test_download_failed_with_url(self):
        """Debe incluir la URL."""
        with pytest.raises(DownloadFailedError) as exc_info:
            raise DownloadFailedError("https://youtube.com/watch?v=abc")
        assert "https://youtube.com/watch?v=abc" in str(exc_info.value)
    
    def test_download_failed_with_reason(self):
        """Debe incluir la razón."""
        with pytest.raises(DownloadFailedError) as exc_info:
            raise DownloadFailedError("url", "Sin conexión")
        assert "Sin conexión" in str(exc_info.value)


class TestConfigError:
    """Tests para ConfigError."""
    
    def test_config_error(self):
        """Debe incluir el motivo."""
        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Archivo corrupto")
        assert "Archivo corrupto" in str(exc_info.value)
        assert "configuración" in str(exc_info.value).lower()


class TestNetworkError:
    """Tests para NetworkError."""
    
    def test_network_error(self):
        """Debe funcionar."""
        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError()
        assert "internet" in str(exc_info.value).lower()
    
    def test_network_error_with_reason(self):
        """Debe incluir la razón."""
        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError("Timeout")
        assert "Timeout" in str(exc_info.value)


class TestPlaylistError:
    """Tests para PlaylistError."""
    
    def test_playlist_error(self):
        """Debe incluir el ID de la playlist."""
        with pytest.raises(PlaylistError) as exc_info:
            raise PlaylistError("PL123")
        assert "PL123" in str(exc_info.value)
    
    def test_playlist_error_with_reason(self):
        """Debe incluir la razón."""
        with pytest.raises(PlaylistError) as exc_info:
            raise PlaylistError("PL123", "No encontrada")
        assert "PL123" in str(exc_info.value)
        assert "No encontrada" in str(exc_info.value)
