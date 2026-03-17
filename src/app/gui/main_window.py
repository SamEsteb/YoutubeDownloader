"""
Ventana principal de la aplicación.

Este módulo contiene la ventana principal y la navegación entre pestañas.
"""

import sys
from pathlib import Path

import customtkinter as ctk

from core import get_config_manager
from gui.download_tab import DownloadTab
from gui.settings_tab import SettingsTab
from gui.theme import APP_CONFIG, set_appearance_mode, get_current_colors
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(ctk.CTk):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        
        # Cargar configuración
        self._config = get_config_manager().get()
        self._colors = get_current_colors()
        
        # Configurar ventana
        self._setup_window()
        
        # Configurar tema
        self._setup_theme()
        
        # Crear interfaz
        self._create_ui()
        
        logger.info("Aplicación iniciada")
    
    def _setup_window(self) -> None:
        """Configura las propiedades de la ventana."""
        self.title(APP_CONFIG["title"])
        self.minsize(APP_CONFIG["min_width"], APP_CONFIG["min_height"])
        
        # Centrar ventana
        self._center_window()
        
        # Manejar cierre
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _center_window(self) -> None:
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_theme(self) -> None:
        """Configura el tema de la aplicación."""
        theme = self._config.theme
        set_appearance_mode(theme)
    
    def _create_ui(self) -> None:
        """Crea la interfaz de usuario."""
        self._colors = get_current_colors()
        
        # Configurar la ventana principal para usar nuestro color de fondo
        self.configure(fg_color=self._colors["bg"])
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Crear tabs sin bordes extras
        self._tabview = ctk.CTkTabview(
            self,
            fg_color=self._colors["bg"],
        )
        self._tabview.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        # Configurar tabs
        self._tabview._segmented_button.configure(
            fg_color=self._colors["bg_secondary"],
            selected_color=self._colors["accent"],
        )
        
        # Añadir pestañas
        self._download_tab = self._tabview.add("⬇️ Descargar")
        self._download_tab.configure(fg_color=self._colors["bg"])
        
        self._settings_tab = self._tabview.add("⚙️ Configuración")
        self._settings_tab.configure(fg_color=self._colors["bg"])
        
        # Seleccionar pestaña por defecto
        self._tabview.set("⬇️ Descargar")
        
        # Crear contenido de cada pestaña
        self._download_content = DownloadTab(self._download_tab)
        
        self._settings_content = SettingsTab(self._settings_tab)
        self._settings_content.pack(fill="both", expand=True)
        
        # Verificar FFmpeg al iniciar
        self.after(500, self._check_ffmpeg)
    
    def _check_ffmpeg(self) -> None:
        """Verifica si FFmpeg está disponible."""
        try:
            from core import VideoDownloader
            
            downloader = VideoDownloader()
            downloader.check_ffmpeg()
        except Exception:
            # FFmpeg no encontrado
            pass
    
    def _on_close(self) -> None:
        """Maneja el cierre de la aplicación."""
        logger.info("Aplicación cerrada")
        self.destroy()
        sys.exit(0)


def run_app() -> None:
    """Inicia la aplicación."""
    app = MainWindow()
    app.mainloop()
