"""
Pestaña de descarga de videos.

Este módulo contiene la interfaz para descargar videos de YouTube.
"""

import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from core import (
    DownloadProgress,
    DownloadFailedError,
    FFmpegNotFoundError,
    InvalidURLError,
    VideoInfo,
    VideoUnavailableError,
    VideoDownloader,
    get_config_manager,
)
from gui.theme import Fonts, get_current_colors


class DownloadTab(ctk.CTkFrame):
    """Pestaña principal de descarga de videos."""
    
    def __init__(self, master: ctk.CTk, **kwargs):
        super().__init__(master, **kwargs)
        
        self._config = get_config_manager().get()
        self._downloader: VideoDownloader | None = None
        self._is_downloading = False
        self._current_video_info: VideoInfo | None = None
        self._colors = get_current_colors()
        
        self._setup_ui()
    
    def _get_colors(self) -> dict:
        """Obtiene los colores actuales según el tema."""
        return get_current_colors()
    
    def _setup_ui(self) -> None:
        """Configura la interfaz de usuario."""
        self._colors = self._get_colors()
        self.configure(fg_color="transparent")
        
        # Frame principal sin padding extra
        self.pack(fill="both", expand=True)
        
        # Título
        ctk.CTkLabel(
            self,
            text="⬇️ YouTube Downloader",
            font=Fonts.TITLE,
            text_color=self._colors["text"],
        ).pack(pady=(20, 15))
        
        # === Input URL ===
        self._url_entry = ctk.CTkEntry(
            self,
            placeholder_text="Pega la URL de YouTube aquí...",
            font=Fonts.DEFAULT,
            height=45,
            border_color=self._colors["border"],
            fg_color=self._colors["bg_secondary"],
        )
        self._url_entry.pack(fill="x", padx=25, pady=(0, 10))
        self._url_entry.bind("<Return>", lambda e: self._on_get_info())
        
        # Botón obtener info
        self._get_info_button = ctk.CTkButton(
            self,
            text="🔍 Obtener info",
            command=self._on_get_info,
            font=Fonts.DEFAULT,
            height=35,
            fg_color=self._colors["button"],
            hover_color=self._colors["button_hover"],
            text_color=self._colors["text"],
            border_width=0,
        )
        self._get_info_button.pack(fill="x", padx=25, pady=(0, 15))
        
        # === Info del video (se muestra después de buscar) ===
        self._info_card = ctk.CTkFrame(
            self,
            fg_color=self._colors["bg_secondary"],
            border_color=self._colors["border"],
            border_width=1,
        )
        self._info_card.pack(fill="x", padx=25, pady=(0, 15))
        self._info_card.pack_forget()  # Oculto inicialmente
        
        self._title_label = ctk.CTkLabel(
            self._info_card,
            text="",
            font=Fonts.HEADER,
            text_color=self._colors["text"],
            wraplength=420,
        )
        self._title_label.pack(padx=15, pady=(15, 5))
        
        self._info_text = ctk.CTkLabel(
            self._info_card,
            text="",
            font=Fonts.SMALL,
            text_color=self._colors["text_secondary"],
        )
        self._info_text.pack(padx=15, pady=(0, 15))
        
        # === Opciones en grid ===
        options_card = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        options_card.pack(fill="x", padx=25, pady=(0, 15))
        
        # Fila 1: Tipo + Calidad Video
        row1 = ctk.CTkFrame(options_card, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))
        
        # Tipo de descarga
        ctk.CTkLabel(
            row1,
            text="Tipo:",
            font=Fonts.SMALL,
            text_color=self._colors["text_secondary"],
            width=80,
        ).pack(side="left")
        
        self._download_type = ctk.CTkSegmentedButton(
            row1,
            values=["Video", "Audio"],
            command=self._on_download_type_changed,
            fg_color=self._colors["bg_secondary"],
            selected_color=self._colors["accent"],
            selected_hover_color=self._colors["accent_hover"],
        )
        self._download_type.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._download_type.set("Video")
        
        # Calidad (cambia según el tipo)
        ctk.CTkLabel(
            row1,
            text="Calidad:",
            font=Fonts.SMALL,
            text_color=self._colors["text_secondary"],
            width=60,
        ).pack(side="left")
        
        # Opciones de calidad para video
        self._video_qualities = ["best", "1080p", "720p", "480p", "360p"]
        self._audio_qualities = ["320k", "256k", "192k", "128k"]
        
        self._quality_combo = ctk.CTkComboBox(
            row1,
            values=self._video_qualities,
            state="readonly",
            fg_color=self._colors["bg_secondary"],
            border_color=self._colors["border"],
        )
        self._quality_combo.pack(side="left", fill="x", expand=True)
        self._quality_combo.set("best")
        
        # Fila 2: Carpeta
        row2 = ctk.CTkFrame(options_card, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            row2,
            text="Carpeta:",
            font=Fonts.SMALL,
            text_color=self._colors["text_secondary"],
            width=80,
        ).pack(side="left")
        
        folder_name = Path(self._config.download_path).name if self._config.download_path else "Downloads"
        
        self._path_button = ctk.CTkButton(
            row2,
            text=f"📁 {folder_name}",
            command=self._on_browse,
            font=Fonts.SMALL,
            height=30,
            fg_color=self._colors["bg_secondary"],
            hover_color=self._colors["fg_secondary"],
            border_color=self._colors["border"],
            text_color=self._colors["text"],
        )
        self._path_button.pack(side="left", fill="x", expand=True)
        
        # === Botón descargar con progress bar ===
        self._download_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._download_frame.pack(fill="x", padx=25, pady=(10, 15))
        
        # Botón de descarga
        self._download_button = ctk.CTkButton(
            self._download_frame,
            text="⬇️ DESCARGAR",
            command=self._on_download,
            font=Fonts.HEADER,
            height=50,
            fg_color=self._colors["accent"],
            hover_color=self._colors["accent_hover"],
            text_color="#FFFFFF",
            border_width=0,
        )
        self._download_button.pack(fill="x")
        
        # Progress bar integrada (invisible inicialmente)
        self._button_progress = ctk.CTkProgressBar(
            self._download_frame,
            progress_color="#4CAF50",
            height=4,
        )
        self._button_progress.pack(fill="x", pady=(0, 0))
        self._button_progress.set(0)
        self._button_progress.pack_forget()
        
        # === Progreso ===
        self._progress_card = ctk.CTkFrame(
            self,
            fg_color=self._colors["bg_secondary"],
            border_color=self._colors["border"],
            border_width=1,
        )
        self._progress_card.pack(fill="x", padx=25, pady=(0, 15))
        self._progress_card.pack_forget()
        
        self._progress_bar = ctk.CTkProgressBar(
            self._progress_card,
            progress_color=self._colors["accent"],
        )
        self._progress_bar.pack(fill="x", padx=15, pady=(15, 5))
        self._progress_bar.set(0)
        
        self._progress_label = ctk.CTkLabel(
            self._progress_card,
            text="",
            font=Fonts.SMALL,
            text_color=self._colors["text_secondary"],
        )
        self._progress_label.pack(padx=15, pady=(0, 15))
    
    def _on_download_type_changed(self, value: str) -> None:
        """Maneja el cambio de tipo de descarga."""
        if value == "Video":
            # Cambiar a calidades de video
            self._quality_combo.configure(values=self._video_qualities)
            self._quality_combo.set("best")
        else:
            # Cambiar a calidades de audio
            self._quality_combo.configure(values=self._audio_qualities)
            self._quality_combo.set("320k")
    
    def _on_browse(self) -> None:
        """Abre el dialog para seleccionar carpeta."""
        folder = filedialog.askdirectory(
            initialdir=self._config.download_path,
            title="Seleccionar carpeta",
        )
        
        if folder:
            folder_name = Path(folder).name
            self._path_button.configure(text=f"📁 {folder_name[:20]}")
            get_config_manager().update(download_path=folder)
    
    def _on_get_info(self) -> None:
        """Obtiene información del video."""
        url = self._url_entry.get().strip()
        
        if not url:
            self._show_error("Ingresa una URL de YouTube")
            return
        
        self._get_info_button.configure(state="disabled", text="Buscando...")
        
        def get_info():
            try:
                downloader = VideoDownloader()
                info = downloader.get_video_info(url)
                self._current_video_info = info
                
                duration = info.duration
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
                
                self.after(0, lambda: self._title_label.configure(
                    text=info.title[:55] + "..." if len(info.title) > 55 else info.title
                ))
                self.after(0, lambda: self._info_text.configure(
                    text=f"📺 {info.uploader}  ⏱️ {duration_str}  👁️ {info.view_count:,}"
                ))
                self.after(0, lambda: self._info_card.pack(fill="x", pady=(0, 15)))
                
            except (InvalidURLError, VideoUnavailableError) as e:
                self.after(0, lambda: self._show_error(str(e)))
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Error: {str(e)}"))
            finally:
                self.after(0, lambda: self._get_info_button.configure(
                    state="normal", text="🔍 Obtener info"
                ))
        
        thread = threading.Thread(target=get_info, daemon=True)
        thread.start()
    
    def _on_download(self) -> None:
        """Inicia la descarga."""
        if self._is_downloading:
            return
        
        url = self._url_entry.get().strip()
        
        if not url:
            self._show_error("Ingresa una URL de YouTube")
            return
        
        audio_only = self._download_type.get() == "Audio"
        quality = self._quality_combo.get()
        output_path = get_config_manager().get().download_path
        
        if not output_path:
            self._show_error("Selecciona una carpeta de descarga")
            return
        
        # Mostrar progreso
        self._progress_card.pack(fill="x", pady=(0, 15))
        self._progress_bar.set(0)
        self._progress_label.configure(text="Iniciando...")
        
        # Mostrar progress bar en el botón
        self._button_progress.pack(fill="x", pady=(0, 0))
        self._button_progress.set(0)
        
        self._download_button.configure(state="disabled", text="⬇️ Descargando... 0%")
        self._is_downloading = True
        
        def download():
            try:
                downloader = VideoDownloader(progress_callback=self._update_progress)
                
                filename = downloader.download(
                    url=url,
                    output_path=output_path,
                    quality=quality,
                    audio_only=audio_only,
                    audio_quality=quality,
                )
                
                self.after(0, lambda f=filename: self._download_complete(f))
            
            except (InvalidURLError, VideoUnavailableError, FFmpegNotFoundError, DownloadFailedError) as e:
                self.after(0, lambda msg=str(e): self._show_error(msg))
            except Exception as e:
                self.after(0, lambda msg=str(e): self._show_error(f"Error: {msg}"))
            finally:
                self.after(0, self._download_finished)
        
        thread = threading.Thread(target=download, daemon=True)
        thread.start()
    
    def _update_progress(self, progress: DownloadProgress) -> None:
        """Actualiza la barra de progreso."""
        if progress.status == "downloading":
            percent = progress.percent / 100
            self._progress_bar.set(percent)
            
            # Actualizar progress bar del botón
            self._button_progress.set(percent)
            
            speed_kb = progress.speed / 1024 if progress.speed else 0
            speed_str = f"{speed_kb:.0f} KB/s" if speed_kb < 1024 else f"{speed_kb/1024:.1f} MB/s"
            
            # Actualizar texto del botón con progreso
            self.after(0, lambda p=progress.percent: self._download_button.configure(
                text=f"⬇️ Descargando... {p:.0f}%"
            ))
            
            self.after(0, lambda: self._progress_label.configure(
                text=f"{progress.percent:.0f}% • {speed_str}"
            ))
    
    def _download_complete(self, filename: str) -> None:
        """Maneja la descarga completada."""
        self._progress_bar.set(1)
        self._button_progress.set(1)
        self._progress_label.configure(text="✅ Completado!")
        self._download_button.configure(text="✅ Descargado!")
        
        self._show_success(f"✅ {Path(filename).name}", filename)
    
    def _download_finished(self) -> None:
        """Limpia el estado después de la descarga."""
        self._is_downloading = False
        self._download_button.configure(state="normal", text="⬇️ DESCARGAR")
        self._button_progress.set(0)
        self._button_progress.pack_forget()
        self._progress_bar.set(0)
    
    def _show_error(self, message: str) -> None:
        """Muestra un mensaje de error."""
        self._colors = self._get_colors()
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Error")
        dialog.geometry("400x140")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="❌ Error",
            font=Fonts.HEADER,
            text_color="#E57373",
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text=message[:100] + "..." if len(message) > 100 else message,
            wraplength=350,
        ).pack(pady=5)
        
        ctk.CTkButton(
            dialog,
            text="Aceptar",
            command=dialog.destroy,
            fg_color=self._colors["button"],
        ).pack(pady=10)
    
    def _show_success(self, message: str, filename: str = "") -> None:
        """Muestra un mensaje de éxito."""
        self._colors = self._get_colors()
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Éxito")
        dialog.geometry("420x160")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="✅ ¡Listo!",
            font=Fonts.HEADER,
            text_color=self._colors["accent"],
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text=message[:60] + "..." if len(message) > 60 else message,
            wraplength=380,
        ).pack(pady=5)
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=15)
        
        def open_folder():
            if filename:
                import subprocess
                subprocess.Popen(f'explorer "{Path(filename).parent}"')
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text="📂 Abrir carpeta",
            command=open_folder,
            fg_color=self._colors["button"],
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cerrar",
            command=dialog.destroy,
        ).pack(side="left", padx=5)
