"""
Pestaña de configuración.

Este módulo contiene la interfaz para configurar la aplicación.
"""

from tkinter import filedialog

import customtkinter as ctk

from core import get_config_manager
from gui.theme import Fonts, get_current_colors


class SettingsTab(ctk.CTkFrame):
    """Pestaña de configuración de la aplicación."""
    
    def __init__(self, master: ctk.CTk, **kwargs):
        super().__init__(master, **kwargs)
        
        self._config_manager = get_config_manager()
        self._config = self._config_manager.get()
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configura la interfaz de usuario."""
        self._colors = get_current_colors()
        self.configure(fg_color="transparent")
        
        # Frame scrolleable
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            label_text="Configuración",
            label_font=Fonts.HEADER,
            fg_color="transparent",
        )
        self._scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Sección: General ===
        general_frame = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        general_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            general_frame,
            text="General",
            font=Fonts.HEADER,
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tema
        theme_row = ctk.CTkFrame(general_frame, fg_color="transparent")
        theme_row.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            theme_row,
            text="Tema:",
            width=120,
            anchor="w",
        ).pack(side="left")
        
        self._theme_combo = ctk.CTkComboBox(
            theme_row,
            values=["System", "Light", "Dark"],
            state="readonly",
            command=self._on_theme_changed,
        )
        self._theme_combo.pack(side="left", fill="x", expand=True)
        self._theme_combo.set(self._config.theme.capitalize())
        
        # === Sección: Descarga ===
        download_frame = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        download_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            download_frame,
            text="Descarga",
            font=Fonts.HEADER,
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Carpeta por defecto
        path_row = ctk.CTkFrame(download_frame, fg_color="transparent")
        path_row.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            path_row,
            text="Carpeta:",
            width=120,
            anchor="w",
        ).pack(side="left")
        
        folder_name = Path(self._config.download_path).name if self._config.download_path else "No configurada"
        
        self._default_path_label = ctk.CTkLabel(
            path_row,
            text=folder_name[:30] + "..." if len(folder_name) > 30 else folder_name,
        )
        self._default_path_label.pack(side="left")
        
        ctk.CTkButton(
            path_row,
            text="📁",
            command=self._on_change_default_path,
            width=35,
            height=28,
        ).pack(side="left", padx=(10, 0))
        
        # Calidad de video
        quality_row = ctk.CTkFrame(download_frame, fg_color="transparent")
        quality_row.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            quality_row,
            text="Calidad video:",
            width=120,
            anchor="w",
        ).pack(side="left")
        
        self._default_quality_combo = ctk.CTkComboBox(
            quality_row,
            values=["best", "2160p", "1440p", "1080p", "720p", "480p", "360p"],
            state="readonly",
        )
        self._default_quality_combo.pack(side="left", fill="x", expand=True)
        self._default_quality_combo.set(self._config.preferred_quality)
        self._default_quality_combo.bind("<<ComboboxSelected>>", self._on_quality_changed)
        
        # Calidad de audio
        audio_row = ctk.CTkFrame(download_frame, fg_color="transparent")
        audio_row.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            audio_row,
            text="Calidad audio:",
            width=120,
            anchor="w",
        ).pack(side="left")
        
        self._default_audio_quality_combo = ctk.CTkComboBox(
            audio_row,
            values=["320k", "256k", "192k", "128k"],
            state="readonly",
        )
        self._default_audio_quality_combo.pack(side="left", fill="x", expand=True)
        self._default_audio_quality_combo.set(self._config.preferred_audio_quality)
        self._default_audio_quality_combo.bind("<<ComboboxSelected>>", self._on_audio_quality_changed)
        
        # Sobrescribir
        self._overwrite_var = ctk.BooleanVar(value=self._config.overwrite_files)
        self._overwrite_checkbox = ctk.CTkCheckBox(
            download_frame,
            text="Sobrescribir archivos existentes",
            variable=self._overwrite_var,
            command=self._on_overwrite_changed,
        )
        self._overwrite_checkbox.pack(anchor="w", padx=15, pady=10)
        

    
    def _on_theme_changed(self, value: str) -> None:
        """Maneja el cambio de tema."""
        theme = value.lower()
        self._config_manager.update(theme=theme)
        
        from gui.theme import set_appearance_mode
        set_appearance_mode(theme)
    
    def _on_change_default_path(self) -> None:
        """Cambia la carpeta de descarga por defecto."""
        folder = filedialog.askdirectory(
            initialdir=self._config.download_path,
            title="Seleccionar carpeta",
        )
        
        if folder:
            self._config_manager.update(download_path=folder)
            folder_name = Path(folder).name
            self._default_path_label.configure(
                text=folder_name[:30] + "..." if len(folder_name) > 30 else folder_name
            )
    
    def _on_quality_changed(self, event=None) -> None:
        """Maneja el cambio de calidad de video."""
        quality = self._default_quality_combo.get()
        self._config_manager.update(preferred_quality=quality)
    
    def _on_audio_quality_changed(self, event=None) -> None:
        """Maneja el cambio de calidad de audio."""
        quality = self._default_audio_quality_combo.get()
        self._config_manager.update(preferred_audio_quality=quality)
    
    def _on_overwrite_changed(self) -> None:
        """Maneja el cambio de sobrescribir archivos."""
        overwrite = self._overwrite_var.get()
        self._config_manager.update(overwrite_files=overwrite)
    

    
    def _show_message(self, message: str) -> None:
        """Muestra un mensaje."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Info")
        dialog.geometry("250x100")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=message).pack(pady=20)
        ctk.CTkButton(dialog, text="Aceptar", command=dialog.destroy).pack(pady=10)


# Necesario para Path
from pathlib import Path
