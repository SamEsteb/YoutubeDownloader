"""
Validador de URLs para YouTube.

Este módulo proporciona funcionalidad para validar y analizar URLs de YouTube,
soportando diferentes formatos de URL.
"""

import re
from dataclasses import dataclass
from typing import Optional

from core.exceptions import InvalidURLError
from utils.logger import get_logger

logger = get_logger(__name__)


# Patrones de URL de YouTube
YOUTUBE_URL_PATTERNS = [
    # youtube.com/watch?v=...
    r"https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+",
    # youtu.be/...
    r"https?://(?:www\.)?youtu\.be/[\w-]+",
    # youtube.com/shorts/...
    r"https?://(?:www\.)?youtube\.com/shorts/[\w-]+",
    # youtube.com/playlist?list=...
    r"https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+",
    # youtube.com/channel/...
    r"https?://(?:www\.)?youtube\.com/channel/[\w-]+",
    # youtube.com/@...
    r"https?://(?:www\.)?youtube\.com/@[\w.-]+",
    # youtube.com/c/...
    r"https?://(?:www\.)?youtube\.com/c/[\w.-]+",
    # youtube.com/v/...
    r"https?://(?:www\.)?youtube\.com/v/[\w-]+",
    # youtube.com/embed/...
    r"https?://(?:www\.)?youtube\.com/embed/[\w-]+",
    # youtube.com/live/...
    r"https?://(?:www\.)?youtube\.com/live/[\w-]+",
    # Invidious instances (alternativas a YouTube)
    r"https?://[\w-]+\.invidious\.io/watch\?v=[\w-]+",
]


# Compilar patrón para mejor rendimiento
YOUTUBE_PATTERN = re.compile(
    "|".join(f"({pattern})" for pattern in YOUTUBE_URL_PATTERNS),
    re.IGNORECASE,
)


@dataclass
class YouTubeURL:
    """Representa una URL de YouTube parseada.
    
    Attributes:
        url: URL original.
        video_id: ID del video (si es un video individual).
        playlist_id: ID de la playlist (si es una playlist).
        is_playlist: True si es una playlist.
        is_video: True si es un video individual.
    """
    
    url: str
    video_id: Optional[str] = None
    playlist_id: Optional[str] = None
    is_playlist: bool = False
    is_video: bool = False
    
    def __str__(self) -> str:
        return self.url


class URLValidator:
    """Validador de URLs de YouTube.
    
    Proporciona métodos para validar URLs y extraer información
    de las mismas.
    """
    
    # Expresiones regulares para extraer IDs
    VIDEO_ID_PATTERN = re.compile(
        r"(?:v=|/v/|/embed/|/watch\?v=|youtu\.be/)([\w-]{11})"
    )
    
    PLAYLIST_ID_PATTERN = re.compile(r"list=([\w-]+)")
    
    def __init__(self) -> None:
        """Inicializa el validador."""
        self._logger = get_logger(__name__)
    
    def validate(self, url: str) -> bool:
        """
        Valida si una URL es de YouTube.
        
        Args:
            url: URL a validar.
        
        Returns:
            True si la URL es válida.
        
        Raises:
            InvalidURLError: Si la URL no es válida.
        """
        # Limpiar URL (quitar espacios)
        url = url.strip()
        
        if not url:
            raise InvalidURLError("")
        
        # Verificar con patrón compilado
        if YOUTUBE_PATTERN.match(url):
            self._logger.debug(f"URL válida detectada: {url}")
            return True
        
        raise InvalidURLError(url)
    
    def parse(self, url: str) -> YouTubeURL:
        """
        Parsea una URL de YouTube y extrae información.
        
        Args:
            url: URL a parsear.
        
        Returns:
            YouTubeURL con la información extraída.
        
        Raises:
            InvalidURLError: Si la URL no es válida.
        """
        # Validar primero
        self.validate(url)
        
        url = url.strip()
        
        # Extraer video ID
        video_id_match = self.VIDEO_ID_PATTERN.search(url)
        video_id = video_id_match.group(1) if video_id_match else None
        
        # Extraer playlist ID
        playlist_id_match = self.PLAYLIST_ID_PATTERN.search(url)
        playlist_id = playlist_id_match.group(1) if playlist_id_match else None
        
        # Determinar tipo
        is_playlist = playlist_id is not None
        is_video = video_id is not None and not is_playlist
        
        self._logger.debug(
            f"URL parseada - video_id: {video_id}, "
            f"playlist_id: {playlist_id}, is_playlist: {is_playlist}"
        )
        
        return YouTubeURL(
            url=url,
            video_id=video_id,
            playlist_id=playlist_id,
            is_playlist=is_playlist,
            is_video=is_video,
        )
    
    def is_video(self, url: str) -> bool:
        """
        Verifica si la URL corresponde a un video individual.
        
        Args:
            url: URL a verificar.
        
        Returns:
            True si es un video individual.
        """
        try:
            parsed = self.parse(url)
            return parsed.is_video
        except InvalidURLError:
            return False
    
    def is_playlist(self, url: str) -> bool:
        """
        Verifica si la URL corresponde a una playlist.
        
        Args:
            url: URL a verificar.
        
        Returns:
            True si es una playlist.
        """
        try:
            parsed = self.parse(url)
            return parsed.is_playlist
        except InvalidURLError:
            return False
    
    def get_video_id(self, url: str) -> Optional[str]:
        """
        Extrae el ID del video de una URL.
        
        Args:
            url: URL del video.
        
        Returns:
            ID del video o None si no es un video.
        """
        try:
            parsed = self.parse(url)
            return parsed.video_id
        except InvalidURLError:
            return None
    
    def get_playlist_id(self, url: str) -> Optional[str]:
        """
        Extrae el ID de la playlist de una URL.
        
        Args:
            url: URL de la playlist.
        
        Returns:
            ID de la playlist o None si no es una playlist.
        """
        try:
            parsed = self.parse(url)
            return parsed.playlist_id
        except InvalidURLError:
            return None


# Instancia global del validador
_validator: Optional[URLValidator] = None


def get_validator() -> URLValidator:
    """Obtiene la instancia global del validador.
    
    Returns:
        Instancia de URLValidator.
    """
    global _validator
    if _validator is None:
        _validator = URLValidator()
    return _validator


def validate_url(url: str) -> bool:
    """
    Valida una URL de YouTube (función de conveniencia).
    
    Args:
        url: URL a validar.
    
    Returns:
        True si es válida.
    
    Raises:
        InvalidURLError: Si no es válida.
    """
    return get_validator().validate(url)


def parse_url(url: str) -> YouTubeURL:
    """
    Parsea una URL de YouTube (función de conveniencia).
    
    Args:
        url: URL a parsear.
    
    Returns:
        YouTubeURL con información extraída.
    """
    return get_validator().parse(url)
