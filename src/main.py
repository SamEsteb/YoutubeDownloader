"""
Punto de entrada de la aplicación YouTube Downloader.

Este archivo es el punto de entrada principal de la aplicación.
"""

import sys
import os
from pathlib import Path

# Determinar si estamos ejecutando como script o como ejecutable
if getattr(sys, 'frozen', False):
    # Ejecutable empaqueado (PyInstaller)
    base_path = Path(sys._MEIPASS)
else:
    # Ejecución normal como script
    base_path = Path(__file__).parent

# Agregar rutas al path
src_path = base_path
app_path = src_path / "app"

paths_to_add = [
    str(src_path),
    str(app_path),
]

for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

# Imports de la aplicación
from utils.logger import setup_logger, get_logger
from gui.main_window import run_app


def main() -> None:
    """Función principal de la aplicación."""
    # Configurar logging
    logger = setup_logger(
        name="youtube-downloader",
        level="INFO",
        log_to_file=True,
        log_to_console=True,
    )
    
    logger.info("=" * 50)
    logger.info("YouTube Downloader iniciado")
    logger.info("=" * 50)
    
    try:
        # Iniciar aplicación
        run_app()
    
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
        sys.exit(0)
    
    except Exception as e:
        logger.exception(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
