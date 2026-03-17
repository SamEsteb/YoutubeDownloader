"""
Excepciones personalizadas para la aplicación YouTube Downloader.

Este módulo define las excepciones específicas de la aplicación para manejar
diferentes tipos de errores de manera consistente.
"""


class YouTubeDownloaderError(Exception):
    """Excepción base para todos los errores de la aplicación.
    
    Attributes:
        message: Mensaje descriptivo del error.
    """
    
    def __init__(self, message: str = "Error desconocido en YouTube Downloader") -> None:
        self.message = message
        super().__init__(self.message)


class InvalidURLError(YouTubeDownloaderError):
    """Excepción lanzada cuando la URL proporcionada es inválida o no corresponde a YouTube.
    
    Attributes:
        url: La URL que causó el error.
    """
    
    def __init__(self, url: str) -> None:
        self.url = url
        message = f"URL inválida: '{url}'. Proporciona una URL válida de YouTube."
        super().__init__(message)


class VideoUnavailableError(YouTubeDownloaderError):
    """Excepción lanzada cuando el video no está disponible.
    
    Puede ser por:
    - Video eliminado
    - Video privado
    - Video con restricciones de edad
    - Video no disponible en la región
    
    Attributes:
        video_id: ID del video que no está disponible.
        reason: Razón por la que no está disponible (si se conoce).
    """
    
    def __init__(self, video_id: str, reason: str | None = None) -> None:
        self.video_id = video_id
        self.reason = reason
        message = f"Video no disponible: '{video_id}'"
        if reason:
            message += f". Razón: {reason}"
        super().__init__(message)


class FFmpegNotFoundError(YouTubeDownloaderError):
    """Excepción lanzada cuando FFmpeg no se encuentra en el sistema.
    
    FFmpeg es requerido para:
    - Merge de video y audio
    - Conversión de formatos
    - Extracción de audio
    """
    
    def __init__(self) -> None:
        message = (
            "FFmpeg no encontrado en el sistema. "
            "FFmpeg es requerido para procesar videos y audio. "
            "Por favor, instala FFmpeg y asegúrate de que esté en el PATH "
            "o configura la ubicación en la configuración de la aplicación."
        )
        super().__init__(message)


class DownloadFailedError(YouTubeDownloaderError):
    """Excepción lançada cuando la descarga falla por un error de red o del servidor.
    
    Attributes:
        url: URL del video que se intentaba descargar.
        reason: Razón específica del fallo.
    """
    
    def __init__(self, url: str, reason: str | None = None) -> None:
        self.url = url
        self.reason = reason
        message = f"Descarga fallida para: '{url}'"
        if reason:
            message += f". Error: {reason}"
        super().__init__(message)


class ConfigError(YouTubeDownloaderError):
    """Excepción lanzada cuando hay un error en la configuración.
    
    Puede ser por:
    - Archivo de configuración corrupto
    - Valores inválidos en la configuración
    - Permisos insuficientes
    """
    
    def __init__(self, reason: str) -> None:
        message = f"Error de configuración: {reason}"
        super().__init__(message)


class NetworkError(YouTubeDownloaderError):
    """Excepción lanzada cuando hay problemas de conexión a internet.
    
    Attributes:
        reason: Razón específica del error de red.
    """
    
    def __init__(self, reason: str | None = None) -> None:
        message = "Error de conexión a internet"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class PlaylistError(YouTubeDownloaderError):
    """Excepción lanzada cuando hay problemas al procesar una playlist.
    
    Attributes:
        playlist_id: ID de la playlist.
        reason: Razón específica del error.
    """
    
    def __init__(self, playlist_id: str, reason: str | None = None) -> None:
        self.playlist_id = playlist_id
        message = f"Error al procesar playlist: '{playlist_id}'"
        if reason:
            message += f". Error: {reason}"
        super().__init__(message)
