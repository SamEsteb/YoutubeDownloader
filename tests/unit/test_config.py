"""
Tests para el gestor de configuración.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from core.config_manager import AppConfig, ConfigManager, ConfigError


class TestAppConfig:
    """Tests para AppConfig."""
    
    def test_default_values(self):
        """Valores por defecto deben ser correctos."""
        config = AppConfig()
        assert config.download_path == ""
        assert config.preferred_quality == "best"
        assert config.preferred_audio_quality == "320k"
        assert config.output_template == "%(title)s.%(ext)s"
        assert config.overwrite_files is False
        assert config.theme == "system"
        assert config.ffmpeg_path == ""
        assert config.max_concurrent_downloads == 1
        assert config.download_subtitles is False
        assert config.subtitles_language == "es"
    
    def test_custom_values(self):
        """Valores personalizados deben funcionar."""
        config = AppConfig(
            download_path="/custom/path",
            preferred_quality="1080p",
            theme="dark",
        )
        assert config.download_path == "/custom/path"
        assert config.preferred_quality == "1080p"
        assert config.theme == "dark"
    
    def test_to_dict(self):
        """to_dict debe retornar diccionario."""
        config = AppConfig(download_path="/test")
        d = config.to_dict()
        assert isinstance(d, dict)
        assert d["download_path"] == "/test"
    
    def test_from_dict(self):
        """from_dict debe crear instancia."""
        data = {
            "download_path": "/test",
            "preferred_quality": "720p",
            "preferred_audio_quality": "256k",
            "output_template": "%(title)s.%(ext)s",
            "overwrite_files": True,
            "theme": "light",
            "ffmpeg_path": "/ffmpeg",
            "max_concurrent_downloads": 2,
            "download_subtitles": True,
            "subtitles_language": "en",
        }
        config = AppConfig.from_dict(data)
        assert config.download_path == "/test"
        assert config.preferred_quality == "720p"
        assert config.overwrite_files is True
        assert config.theme == "light"


class TestConfigManager:
    """Tests para ConfigManager."""
    
    def test_config_file_path(self):
        """La ruta del archivo de config debe ser correcta."""
        manager = ConfigManager()
        # Debe terminar en config.json
        assert manager._config_path.name == "config.json"
    
    def test_default_download_path(self):
        """La ruta de descarga por defecto debe ser la carpeta Downloads."""
        manager = ConfigManager()
        # Si hay una carpeta Downloads, debe usarla
        downloads = Path.home() / "Downloads"
        if downloads.exists():
            assert manager.get_default_download_path() == str(downloads)
    
    def test_load_creates_default_config(self):
        """load debe crear config por defecto si no existe."""
        # Crear un manager temporal con ruta falsa
        manager = ConfigManager()
        
        # Reemplazar la ruta temporalmente
        original_path = manager._config_path
        with tempfile.TemporaryDirectory() as tmpdir:
            manager._config_path = Path(tmpdir) / "config.json"
            
            # Cargar
            config = manager.load()
            
            # Debe tener valores por defecto
            assert config.preferred_quality == "best"
            assert config.theme == "system"
            
            # Debe crear el archivo
            assert manager._config_path.exists()
        
        # Restaurar
        manager._config_path = original_path


class TestConfigIntegration:
    """Tests de integración para configuración."""
    
    def test_update_saves_config(self):
        """update debe guardar la configuración."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager()
            manager._config_path = Path(tmpdir) / "config.json"
            
            # Cargar config por defecto
            manager.load()
            
            # Actualizar
            manager.update(preferred_quality="720p", theme="dark")
            
            # Verificar que se guardó
            with open(manager._config_path) as f:
                data = json.load(f)
            
            assert data["preferred_quality"] == "720p"
            assert data["theme"] == "dark"
    
    def test_get_returns_current_config(self):
        """get debe retornar la configuración actual."""
        manager = ConfigManager()
        
        # Debe poder obtener config (usa la real o crea una)
        config = manager.get()
        assert isinstance(config, AppConfig)
