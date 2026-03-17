"""
Downloader de videos de YouTube usando yt-dlp.

Este módulo proporciona la funcionalidad principal para descargar videos
y audio de YouTube, manejando progreso, errores y configuraciones.
"""

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import yt_dlp as ytdl

from core.config_manager import get_config_manager
from core.exceptions import (
    DownloadFailedError,
    FFmpegNotFoundError,
    VideoUnavailableError,
    NetworkError,
)
from core.validator import get_validator
from utils.logger import get_logger

logger = get_logger(__name__)


# Tipos de calidad disponibles
VIDEO_QUALITIES = [
    ("best", "Mejor disponible"),
    ("2160p", "4K - 2160p"),
    ("1440p", "HD - 1440p"),
    ("1080p", "Full HD - 1080p"),
    ("720p", "HD - 720p"),
    ("480p", "SD - 480p"),
    ("360p", "Baja - 360p"),
    ("worst", "Peor calidad"),
]

AUDIO_QUALITIES = [
    ("320k", "320 kbps (Mejor)"),
    ("256k", "256 kbps"),
    ("192k", "192 kbps"),
    ("128k", "128 kbps (Por defecto)"),
]


@dataclass
class VideoInfo:
    """Información de un video de YouTube.
    
    Attributes:
        id: ID del video.
        title: Título del video.
        uploader: Nombre del creador.
        duration: Duración en segundos.
        thumbnail: URL de la miniatura.
        description: Descripción del video.
        upload_date: Fecha de subida.
        view_count: Número de vistas.
        like_count: Número de likes.
        categories: Categorías.
        tags: Etiquetas.
        is_live: Si es un video en vivo.
    """
    
    id: str
    title: str
    uploader: str
    duration: int
    thumbnail: str
    description: str
    upload_date: str
    view_count: int
    like_count: int
    categories: list[str]
    tags: list[str]
    is_live: bool
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VideoInfo":
        """Crea una instancia desde el diccionario de yt-dlp."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", "Sin título"),
            uploader=data.get("uploader", "Desconocido"),
            duration=data.get("duration", 0),
            thumbnail=data.get("thumbnail", ""),
            description=data.get("description", ""),
            upload_date=data.get("upload_date", ""),
            view_count=data.get("view_count", 0),
            like_count=data.get("like_count", 0),
            categories=data.get("categories", []),
            tags=data.get("tags", []),
            is_live=data.get("is_live", False) or data.get("live_status") == "is_live",
        )


@dataclass
class DownloadProgress:
    """Progreso de una descarga.
    
    Attributes:
        percent: Porcentaje completado (0-100).
        speed: Velocidad de descarga (bytes/s).
        eta: Tiempo restante estimado (segundos).
        total_bytes: Tamaño total (bytes).
        downloaded_bytes: Bytes descargados.
        filename: Nombre del archivo.
        status: Estado actual (downloading, finished, error).
    """
    
    percent: float = 0.0
    speed: float = 0.0
    eta: int = 0
    total_bytes: int = 0
    downloaded_bytes: int = 0
    filename: str = ""
    status: str = "downloading"
    error: Optional[str] = None


class VideoDownloader:
    """Downloader de videos de YouTube.
    
    Maneja la descarga de videos y audio, con soporte para:
    - Diferentes calidades de video
    - Extracción de audio (MP3)
    - Playlists
    - Progress callbacks
    """
    
    def __init__(
        self,
        ffmpeg_path: Optional[str] = None,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
    ) -> None:
        """
        Inicializa el downloader.
        
        Args:
            ffmpeg_path: Ruta personalizada a FFmpeg (None = usar PATH).
            progress_callback: Función a llamar con el progreso de descarga.
        """
        self._logger = get_logger(__name__)
        self._progress_callback = progress_callback
        # Primero cargar config, luego buscar FFmpeg
        self._config = get_config_manager().get()
        self._ffmpeg_path = ffmpeg_path or self._find_ffmpeg()
        
        if not self._ffmpeg_path:
            self._logger.warning(
                "FFmpeg no encontrado. Algunas funciones pueden no estar disponibles."
            )
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Busca FFmpeg en el sistema."""
        # Primero verificar si hay una ruta configurada
        if self._config.ffmpeg_path:
            ffmpeg_path = Path(self._config.ffmpeg_path)
            if ffmpeg_path.exists():
                # Si es un directorio, buscar ffmpeg.exe dentro
                if ffmpeg_path.is_dir():
                    ffmpeg_exe = ffmpeg_path / "bin" / "ffmpeg.exe"
                    if ffmpeg_exe.exists():
                        self._logger.info(f"FFmpeg encontrado en ruta configurada: {ffmpeg_exe}")
                        return str(ffmpeg_exe)
                # Si es el archivo directo
                ffmpeg_exe = ffmpeg_path / "ffmpeg.exe"
                if ffmpeg_exe.exists():
                    self._logger.info(f"FFmpeg encontrado en ruta configurada: {ffmpeg_exe}")
                    return str(ffmpeg_exe)
        
        # Verificar en PATH usando where (Windows)
        try:
            result = subprocess.run(
                ["where", "ffmpeg"],
                capture_output=True,
                text=True,
                shell=True,
            )
            if result.returncode == 0:
                ffmpeg_path = result.stdout.strip().split("\n")[0]
                self._logger.info(f"FFmpeg encontrado en PATH: {ffmpeg_path}")
                return ffmpeg_path
        except FileNotFoundError:
            pass
        
        # Verificar ubicación del usuario común
        user_ffmpeg_paths = [
            Path("C:/Users/samue/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe",
        ]
        
        for ffmpeg_path in user_ffmpeg_paths:
            if ffmpeg_path.exists():
                self._logger.info(f"FFmpeg encontrado en: {ffmpeg_path}")
                return str(ffmpeg_path)
        
        return None
    
    def check_ffmpeg(self) -> bool:
        """
        Verifica si FFmpeg está disponible.
        
        Returns:
            True si FFmpeg está disponible.
        
        Raises:
            FFmpegNotFoundError: Si FFmpeg no está disponible.
        """
        if self._ffmpeg_path:
            return True
        
        # Intentar encontrarlo de nuevo
        self._ffmpeg_path = self._find_ffmpeg()
        if self._ffmpeg_path:
            return True
        
        raise FFmpegNotFoundError()
    
    def _get_ydl_opts(
        self,
        output_path: str,
        quality: str = "best",
        audio_only: bool = False,
        audio_quality: str = "320k",
        format_spec: Optional[str] = None,
    ) -> dict[str, Any]:
        """Genera las opciones para yt-dlp."""
        
        # Determinar formato
        if audio_only:
            # Extraer solo audio
            if format_spec:
                # Formato específico proporcionado
                format_str = format_spec
            else:
                # Por defecto: mejor audio, convertir a MP3
                format_str = "bestaudio/best"
        else:
            # Descargar video
            if format_spec:
                format_str = format_spec
            elif quality == "best":
                format_str = "bestvideo+bestaudio/best"
            elif quality == "worst":
                format_str = "worstvideo+worstaudio/worst"
            else:
                # Calidad específica
                format_str = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        
        opts = {
            "format": format_str,
            "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
            "quiet": False,
            "no_warnings": False,
            "extract_flat": False,
            "writethumbnail": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "merge_output_format": "mp4" if not audio_only else "mp3",
            "postprocessors": [],
        }
        
        # Agregar post-procesador para audio
        if audio_only:
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": audio_quality.replace("k", ""),
                }
            ]
        
        # Agregar ruta de FFmpeg si está configurada
        if self._ffmpeg_path:
            opts["ffmpeg_location"] = os.path.dirname(self._ffmpeg_path)
        
        # No agregar el ID al nombre del archivo - usar solo el título
        # La configuración de overwrite se maneja en otro lado
        
        return opts
    
    def _progress_hook(self, d: dict[str, Any]) -> None:
        """Hook para actualizar el progreso de descarga."""
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            
            percent = (downloaded / total * 100) if total > 0 else 0
            
            progress = DownloadProgress(
                percent=percent,
                speed=d.get("speed", 0),
                eta=d.get("eta", 0),
                total_bytes=total,
                downloaded_bytes=downloaded,
                filename=d.get("filename", ""),
                status="downloading",
            )
            
            if self._progress_callback:
                self._progress_callback(progress)
        
        elif d["status"] == "finished":
            progress = DownloadProgress(
                percent=100.0,
                status="finished",
                filename=d.get("filename", ""),
            )
            
            if self._progress_callback:
                self._progress_callback(progress)
    
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Obtiene información de un video.
        
        Args:
            url: URL del video.
        
        Returns:
            VideoInfo con la información del video.
        
        Raises:
            VideoUnavailableError: Si el video no está disponible.
            InvalidURLError: Si la URL es inválida.
        """
        validator = get_validator()
        validator.validate(url)
        
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        
        if self._ffmpeg_path:
            ydl_opts["ffmpeg_location"] = os.path.dirname(self._ffmpeg_path)
        
        try:
            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise VideoUnavailableError(
                        validator.get_video_id(url) or url,
                        "No se pudo obtener información del video"
                    )
                
                return VideoInfo.from_dict(info)
        
        except ytdl.utils.DownloadError as e:
            error_msg = str(e).lower()
            
            if "unavailable" in error_msg or "private" in error_msg:
                raise VideoUnavailableError(
                    validator.get_video_id(url) or url,
                    str(e)
                )
            elif "geo" in error_msg or "region" in error_msg:
                raise VideoUnavailableError(
                    validator.get_video_id(url) or url,
                    "Video no disponible en tu región"
                )
            elif "age" in error_msg:
                raise VideoUnavailableError(
                    validator.get_video_id(url) or url,
                    "El video tiene restricciones de edad"
                )
            else:
                raise VideoUnavailableError(
                    validator.get_video_id(url) or url,
                    str(e)
                )
        
        except Exception as e:
            self._logger.error(f"Error al obtener info del video: {e}")
            raise VideoUnavailableError(
                validator.get_video_id(url) or url,
                str(e)
            )
    
    def get_available_formats(self, url: str) -> list[dict[str, Any]]:
        """
        Obtiene los formatos disponibles para un video.
        
        Args:
            url: URL del video.
        
        Returns:
            Lista de diccionarios con información de formatos.
        """
        validator = get_validator()
        validator.validate(url)
        
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        
        if self._ffmpeg_path:
            ydl_opts["ffmpeg_location"] = os.path.dirname(self._ffmpeg_path)
        
        try:
            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return []
                
                formats = info.get("formats", [])
                
                # Filtrar y ordenar por calidad
                result = []
                seen = set()
                
                for f in formats:
                    height = f.get("height", 0)
                    if height and height not in seen:
                        seen.add(height)
                        result.append({
                            "format_id": f.get("format_id"),
                            "ext": f.get("ext"),
                            "height": height,
                            "filesize": f.get("filesize") or f.get("filesize_estimate", 0),
                            "quality": f"{height}p",
                        })
                
                # Ordenar por resolución
                result.sort(key=lambda x: x["height"], reverse=True)
                
                return result
        
        except Exception as e:
            self._logger.error(f"Error al obtener formatos: {e}")
            return []
    
    def download(
        self,
        url: str,
        output_path: Optional[str] = None,
        quality: str = "best",
        audio_only: bool = False,
        audio_quality: str = "320k",
        format_spec: Optional[str] = None,
    ) -> str:
        """
        Descarga un video o audio de YouTube.
        
        Args:
            url: URL del video.
            output_path: Ruta de descarga (None = usar configuración).
            quality: Calidad del video (best, 1080p, 720p, etc.).
            audio_only: Si True, descarga solo audio.
            audio_quality: Calidad del audio (128k, 192k, 320k).
            format_spec: Formato específico de yt-dlp.
        
        Returns:
            Ruta del archivo descargado.
        
        Raises:
            VideoUnavailableError: Si el video no está disponible.
            DownloadFailedError: Si la descarga falla.
            FFmpegNotFoundError: Si FFmpeg no está disponible (para audio).
        """
        validator = get_validator()
        validator.validate(url)
        
        # Usar ruta de configuración si no se especifica
        if output_path is None:
            output_path = self._config.download_path
        
        # Crear directorio si no existe
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # Verificar FFmpeg para audio
        if audio_only and not self.check_ffmpeg():
            raise FFmpegNotFoundError()
        
        ydl_opts = self._get_ydl_opts(
            output_path=output_path,
            quality=quality,
            audio_only=audio_only,
            audio_quality=audio_quality,
            format_spec=format_spec,
        )
        
        # Agregar hook de progreso
        ydl_opts["progress_hooks"] = [self._progress_hook]
        
        try:
            self._logger.info(f"Iniciando descarga: {url}")
            
            with ytdl.YoutubeDL(ydl_opts) as ydl:
                # Extraer información primero
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    raise DownloadFailedError(url, "No se pudo descargar el video")
                
                # Obtener la ruta del archivo descargado
                filename = ydl.prepare_filename(info)
                
                # Si es audio, ajustar extensión
                if audio_only:
                    base, _ = os.path.splitext(filename)
                    filename = base + ".mp3"
                
                self._logger.info(f"Descarga completada: {filename}")
                
                return filename
        
        except ytdl.utils.DownloadError as e:
            error_msg = str(e).lower()
            
            if "unavailable" in error_msg:
                raise VideoUnavailableError(
                    validator.get_video_id(url) or url,
                    str(e)
                )
            else:
                raise DownloadFailedError(url, str(e))
        
        except Exception as e:
            self._logger.error(f"Error en descarga: {e}")
            raise DownloadFailedError(url, str(e))
    
    def cancel_download(self) -> None:
        """Cancela la descarga actual (si hay alguna en progreso)."""
        # yt-dlp no tiene soporte directo para cancelación,
        # pero podemos marcar una bandera para detener el progreso
        # Esto se implementaría con threading en una versión futura
        pass
