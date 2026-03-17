"""
Sistema de logging para la aplicación YouTube Downloader.

Este módulo proporciona una configuración centralizada de logging con:
- Archivos de log rotativos
- Consola con colores
- Distintos niveles de log
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


# Ruta base del proyecto (se determina dinámicamente)
def get_app_data_dir() -> Path:
    """Obtiene el directorio de datos de la aplicación.
    
    En Windows: %APPDATA%/YouTubeDownloader
    
    Returns:
        Path al directorio de datos de la aplicación.
    """
    import os
    
    app_data = os.environ.get("APPDATA")
    if app_data:
        app_dir = Path(app_data) / "YouTubeDownloader"
    else:
        # Fallback para Linux/Mac
        app_dir = Path.home() / ".config" / "youtube-downloader"
    
    # Crear directorio si no existe
    app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir


def get_log_dir() -> Path:
    """Obtiene el directorio de logs.
    
    Returns:
        Path al directorio de logs.
    """
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger(
    name: str = "youtube-downloader",
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Configura y retorna un logger con las opciones especificadas.
    
    Args:
        name: Nombre del logger.
        level: Nivel de logging.
        log_to_file: Si True, escribe logs a archivo.
        log_to_console: Si True, escribe logs a consola.
    
    Returns:
        Logger configurado.
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formato para los logs
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s",
    )
    
    # Handler para archivo (rotativo)
    if log_to_file:
        log_file = get_log_dir() / f"youtube-downloader-{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Handler para consola
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Agregar colores según el nivel
        class ColoredConsoleHandler(logging.StreamHandler):
            COLORS = {
                logging.DEBUG: "\033[36m",      # Cyan
                logging.INFO: "\033[32m",       # Green
                logging.WARNING: "\033[33m",    # Yellow
                logging.ERROR: "\033[31m",      # Red
                logging.CRITICAL: "\033[35m",   # Magenta
            }
            RESET = "\033[0m"
            
            def emit(self, record: logging.LogRecord) -> None:
                try:
                    color = self.COLORS.get(record.levelno, "")
                    message = self.format(record)
                    self.stream.write(f"{color}{message}{self.RESET}\n")
                    self.flush()
                except Exception:
                    self.handleError(record)
        
        colored_console = ColoredConsoleHandler()
        colored_console.setFormatter(console_formatter)
        logger.addHandler(colored_console)
    
    return logger


# Logger global de la aplicación
app_logger = setup_logger()


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Obtiene un logger para el módulo específico.
    
    Args:
        name: Nombre del módulo (opcional). Si es None, retorna el logger global.
    
    Returns:
        Logger configurado.
    """
    if name:
        return logging.getLogger(f"youtube-downloader.{name}")
    return app_logger
