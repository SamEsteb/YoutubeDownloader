"""
Core package - Lógica de negocio de YouTube Downloader.

Este paquete contiene los módulos principales:
- downloader: Manejo de descargas con yt-dlp
- validator: Validación de URLs
- config_manager: Gestión de configuración
- exceptions: Excepciones personalizadas
"""

from core.config_manager import (
    AppConfig,
    ConfigManager,
    get_config,
    get_config_manager,
)
from core.downloader import (
    DownloadProgress,
    VideoDownloader,
    VideoInfo,
)
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
from core.validator import (
    URLValidator,
    YouTubeURL,
    get_validator,
    parse_url,
    validate_url,
)

__all__ = [
    "AppConfig",
    "ConfigManager",
    "get_config",
    "get_config_manager",
    "VideoDownloader",
    "VideoInfo",
    "DownloadProgress",
    "URLValidator",
    "YouTubeURL",
    "get_validator",
    "validate_url",
    "parse_url",
    "YouTubeDownloaderError",
    "InvalidURLError",
    "VideoUnavailableError",
    "FFmpegNotFoundError",
    "DownloadFailedError",
    "ConfigError",
    "NetworkError",
    "PlaylistError",
]
