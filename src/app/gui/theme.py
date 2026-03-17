"""
Tema y configuración de la interfaz gráfica.

Este módulo define los colores, fuentes y estilos de la aplicación.
"""

import customtkinter as ctk


# Paletas de colores personalizadas
class Colors:
    """Colores del tema."""
    
    # Tema oscuro - paleta estilo YouTube
    DARK = {
        "bg": "#202020",           # Fondo principal (gris muy oscuro/negro)
        "bg_secondary": "#313131", # Fondo secundario (tarjetas, paneles)
        "fg": "#272727",           # Elementos foreground
        "fg_secondary": "#3F3F3F", # Elementos secundarios y lineas
        "text": "#F1F1F1",         # Texto principal (blanco casi puro)
        "text_secondary": "#AAAAAA", # Texto secundario (gris)
        "accent": "#FF0000",       # Acento principal (Rojo YouTube)
        "accent_hover": "#CC0000", # Acento hover (Rojo oscuro)
        "success": "#2BA640",      # Verde success
        "warning": "#F1A42F",      # Naranja warning
        "error": "#FF4E4E",        # Rojo error
        "border": "#3D3D3D",       # Bordes
        "button": "#272727",       # Botones secundarios
        "button_hover": "#3F3F3F", # Botones secundarios hover
    }
    
    # Tema claro - paleta estilo YouTube
    LIGHT = {
        "bg": "#FFFFFF",           # Fondo principal (blanco)
        "bg_secondary": "#F2F2F2", # Fondo secundario (gris muy claro)
        "fg": "#E5E5E5",           # Elementos foreground
        "fg_secondary": "#CCCCCC", # Elementos secundarios
        "text": "#0F0F0F",         # Texto principal (casi negro)
        "text_secondary": "#606060", # Texto secundario (gris medio)
        "accent": "#FF0000",       # Acento principal (Rojo YouTube)
        "accent_hover": "#CC0000", # Acento hover (Rojo oscuro)
        "success": "#2BA640",      # Verde success
        "warning": "#F1A42F",      # Naranja warning
        "error": "#FF4E4E",        # Rojo error
        "border": "#E5E5E5",       # Bordes
        "button": "#E5E5E5",       # Botones secundarios
        "button_hover": "#CCCCCC", # Botones secundarios hover
    }


# Configuración de fuentes
class Fonts:
    """Fuentes de la aplicación."""
    
    DEFAULT = ("Segoe UI", 14)
    TITLE = ("Segoe UI", 24, "bold")
    HEADER = ("Segoe UI", 16, "bold")
    SMALL = ("Segoe UI", 12)
    MONO = ("Consolas", 12)


# Configuración de la aplicación
APP_CONFIG = {
    "title": "YouTube Downloader",
    "min_width": 500,
    "min_height": 500,
    "default_theme": "system",
    "default_color": "dark-blue",  # Color base para CustomTkinter
}


def get_appearance_mode() -> str:
    """Obtiene el modo de apariencia del sistema."""
    return ctk.get_appearance_mode()


def get_current_colors() -> dict:
    """Obtiene los colores como tuplas (claro, oscuro) para que CustomTkinter las cambie dinámicamente."""
    colors = {}
    for key in Colors.LIGHT:
        colors[key] = (Colors.LIGHT[key], Colors.DARK[key])
    return colors


def set_appearance_mode(mode: str) -> None:
    """Establece el modo de apariencia."""
    ctk.set_appearance_mode(mode)


def set_default_color_theme(color: str) -> None:
    """Establece el tema de color por defecto."""
    ctk.set_default_color_theme(color)


def apply_custom_theme() -> None:
    """Aplica el tema personalizado a CustomTkinter."""
    mode = ctk.get_appearance_mode().lower()
    
    if mode == "dark":
        ctk.set_appearance_mode("dark")
        # Colores CustomTkinter para modo oscuro
        ctk.set_default_color_theme("dark-blue")
    else:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
