"""
Gestor de configuración para YouTube Downloader.

Este módulo maneja la persistencia y carga de configuración de la aplicación.
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Optional

from core.exceptions import ConfigError
from utils.logger import get_logger

logger = get_logger(__name__)


# Valores por defecto
DEFAULT_CONFIG = {
    "download_path": "",  # Se establece dinámicamente
    "preferred_quality": "best",
    "preferred_audio_quality": "320k",
    "output_template": "%(title)s.%(ext)s",
    "overwrite_files": False,
    "theme": "system",
    "max_concurrent_downloads": 1,
    "download_subtitles": False,
    "subtitles_language": "es",
}


@dataclass
class AppConfig:
    """Configuración de la aplicación.
    
    Attributes:
        download_path: Ruta donde se guardan las descargas.
        preferred_quality: Calidad preferida de video (best, 1080p, 720p, etc.).
        preferred_audio_quality: Calidad de audio en kbps (128k, 192k, 320k).
        output_template: Plantilla para el nombre del archivo.
        overwrite_files: Si True, sobrescribe archivos existentes.
        theme: Tema de la interfaz (system, light, dark).
        max_concurrent_downloads: Máximo de descargas simultáneas.
        download_subtitles: Si True, descarga subtítulos.
        subtitles_language: Idioma de subtítulos.
    """
    
    download_path: str = ""
    preferred_quality: str = "best"
    preferred_audio_quality: str = "320k"
    output_template: str = "%(title)s.%(ext)s"
    overwrite_files: bool = False
    theme: str = "system"
    max_concurrent_downloads: int = 1
    download_subtitles: bool = False
    subtitles_language: str = "es"
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        """Crea una instancia desde un diccionario filtrando claves obsoletas."""
        import dataclasses
        valid_keys = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


class ConfigManager:
    """Gestor de configuración de la aplicación.
    
    Maneja la lectura, escritura y validación de la configuración.
    """
    
    CONFIG_FILE_NAME = "config.json"
    
    def __init__(self) -> None:
        """Inicializa el gestor de configuración."""
        self._logger = get_logger(__name__)
        self._config: Optional[AppConfig] = None
        self._config_path = self._get_config_path()
    
    def _get_config_path(self) -> Path:
        """Obtiene la ruta del archivo de configuración."""
        config_dir = self._get_app_data_dir()
        return config_dir / self.CONFIG_FILE_NAME
    
    def _get_app_data_dir(self) -> Path:
        """Obtiene el directorio de datos de la aplicación."""
        app_data = os.environ.get("APPDATA")
        if app_data:
            app_dir = Path(app_data) / "YouTubeDownloader"
        else:
            app_dir = Path.home() / ".config" / "youtube-downloader"
        
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
    
    def get_default_download_path(self) -> str:
        """Obtiene la ruta de descarga por defecto (carpeta Downloads del usuario)."""
        home = Path.home()
        downloads = home / "Downloads"
        if downloads.exists():
            return str(downloads)
        return str(home)
    
    def load(self) -> AppConfig:
        """
        Carga la configuración desde el archivo.
        
        Returns:
            Configuración cargada.
        
        Raises:
            ConfigError: Si hay un error al cargar.
        """
        try:
            if self._config_path.exists():
                with open(self._config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Combinar con valores por defecto
                config_data = DEFAULT_CONFIG.copy()
                config_data.update(data)
                
                self._config = AppConfig.from_dict(config_data)
                self._logger.info(f"Configuración cargada desde {self._config_path}")
            else:
                # Crear configuración por defecto
                self._config = AppConfig()
                self._set_default_download_path()
                self.save()
                self._logger.info("Configuración por defecto creada")
            
            return self._config
        
        except json.JSONDecodeError as e:
            self._logger.error(f"Error al parsear configuración: {e}")
            raise ConfigError(f"Archivo de configuración corrupto: {e}")
        except Exception as e:
            self._logger.error(f"Error al cargar configuración: {e}")
            raise ConfigError(f"No se pudo cargar la configuración: {e}")
    
    def _set_default_download_path(self) -> None:
        """Establece la ruta de descarga por defecto."""
        if not self._config:
            return
        
        if not self._config.download_path:
            self._config.download_path = self.get_default_download_path()
    
    def save(self, config: Optional[AppConfig] = None) -> None:
        """
        Guarda la configuración al archivo.
        
        Args:
            config: Configuración a guardar. Si es None, guarda la actual.
        
        Raises:
            ConfigError: Si hay un error al guardar.
        """
        try:
            if config is not None:
                self._config = config
            elif self._config is None:
                self._config = AppConfig()
            
            self._set_default_download_path()
            
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._config.to_dict(), f, indent=4, ensure_ascii=False)
            
            self._logger.info(f"Configuración guardada en {self._config_path}")
        
        except Exception as e:
            self._logger.error(f"Error al guardar configuración: {e}")
            raise ConfigError(f"No se pudo guardar la configuración: {e}")
    
    def get(self) -> AppConfig:
        """
        Obtiene la configuración actual.
        
        Returns:
            Configuración actual.
        """
        if self._config is None:
            self.load()
        return self._config
    
    def update(self, **kwargs: Any) -> AppConfig:
        """
        Actualiza valores específicos de la configuración.
        
        Args:
            **kwargs: Claves y valores a actualizar.
        
        Returns:
            Configuración actualizada.
        """
        config = self.get()
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                self._logger.warning(f"Clave de configuración desconocida: {key}")
        
        self.save(config)
        return config


# Instancia global del gestor de configuración
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Obtiene la instancia global del gestor de configuración."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Obtiene la configuración actual (función de conveniencia)."""
    return get_config_manager().get()
