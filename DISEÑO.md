# Diseño Arquitectónico - YouTube Downloader

Este documento especifica la arquitectura de la aplicación, las decisiones de diseño y las mejores prácticas a seguir durante la implementación.

---

## 1. Visión General de la Arquitectura

### 1.1 Patrón de Arquitectura

La aplicación sigue el patrón **MVVM (Model-View-ViewModel)** adaptado para Python con CustomTkinter:

```
┌─────────────────────────────────────────────────────────────┐
│                        VISTA (GUI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ MainWindow  │  │ DownloadTab │  │    SettingsTab     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    VIEWMODEL (Lógica UI)                     │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ DownloadViewModel│  │SettingsViewModel│                  │
│  └────────┬────────┘  └────────┬────────┘                  │
└───────────┼─────────────────────┼───────────────────────────┘
            │                     │
            ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODELO (Lógica de Negocio)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Downloader │  │  Validator  │  │   ConfigManager     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Principios de Diseño

1. **Separación de Responsabilidades (SRP)**: Cada módulo tiene una única responsabilidad
2. **Inversión de Dependencias (DIP)**: Las capas superiores no dependen de las inferiores
3. **Alta Cohesión, Bajo Acoplamiento**: Componentes reutilizables y mantenibles
4. **Código para Humanos**: Nombres descriptivos, docstrings, tipos hints

---

## 2. Estructura de Capas

### 2.1 Capa de Presentación (GUI)

```
src/app/gui/
├── main_window.py      # Ventana principal, gestión de tabs
├── download_tab.py     # UI de descarga (entrada URL, progreso)
├── settings_tab.py     # UI de configuración
├── widgets/            # Componentes UI reutilizables
│   ├── __init__.py
│   ├── url_input.py    # Campo de entrada de URL con validación
│   ├── progress_bar.py # Barra de progreso personalizada
│   └── quality_selector.py # Selector de calidad
└── theme.py            # Configuración de tema CustomTkinter
```

**Responsabilidades:**

- Renderizar la interfaz de usuario
- Capturar eventos del usuario
- Delegar acciones al ViewModel
- Mostrar feedback visual

**Notas:**

- CustomTkinter permite crear interfaces modernas con tema oscuro/claro
- Usar **Frame** para agrupar widgets relacionados
- Evitar lógica de negocio en esta capa

---

### 2.2 Capa de ViewModel

```
src/app/viewmodel/
├── __init__.py
├── download_viewmodel.py   # Lógica de la pantalla de descarga
└── settings_viewmodel.py  # Lógica de configuración
```

**Responsabilidades:**

- Transformar datos del modelo para la vista
- Manejar el estado de la UI
- Procesar comandos del usuario
- Coordinar entre Vista y Modelo

---

### 2.3 Capa de Modelo (Core)

```
src/app/core/
├── __init__.py
├── downloader.py      # Lógica de descarga con yt-dlp
├── validator.py       # Validación de URLs
├── config_manager.py  # Gestión de configuración
├── history_manager.py # Historial de descargas
└── exceptions.py      # Excepciones personalizadas
```

**Responsabilidades:**

- Lógica de negocio pura
- Integración con bibliotecas externas (yt-dlp)
- Persistencia de datos
- Validaciones

---

### 2.4 Capa de Utilidades

```
src/utils/
├── __init__.py
├── logger.py          # Sistema de logging
├── file_utils.py      # Utilidades de manejo de archivos
└── path_utils.py      # Utilidades de rutas
```

---

## 3. Decisiones de Diseño

### 3.1 Biblioteca de Descarga: yt-dlp

**Decisión**: Usar `yt-dlp` en lugar de `pytube` o `youtube-dl`

**Justificación:**

| Biblioteca | Pros | Contras |
|------------|------|---------|
| yt-dlp | Actualizaciones frecuentes, mejor soporte, más formatos | Mayor consumo de memoria |
| pytube | Liviano | Actualizaciones lentas, muchos errores recientes |
| youtube-dl | Histórico | Abandonado, no funciona con YouTube actual |

**Conclusión**: yt-dlp es la única opción viable en 2024/2025 debido a las constantes cambios en la API de YouTube.

---

### 3.2 Interfaz Gráfica: CustomTkinter

**Decisión**: Usar `CustomTkinter` en lugar de PyQt6 o Tkinter puro

**Justificación:**

| Librería | Pros | Contras |
|----------|------|---------|
| CustomTkinter | Moderno, easy to use, tema oscuro integrado | Funcionalidad limitada vs PyQt |
| PyQt6 | Potente, profesional | Curva de aprendizaje alta, licenciamiento |
| Tkinter | Incluido con Python | Apariencia anticuada |

**Conclusión**: CustomTkinter ofrece el mejor balance entre facilidad de desarrollo y apariencia moderna para una aplicación de esta complejidad.

---

### 3.3 Concurrencia: asyncio

**Decisión**: Usar `asyncio` para operaciones de red

**Justificación:**

- Las descargas de yt-dlp son I/O-bound
- asyncio permite mantener la UI responsiva
- Compatible con pytest-asyncio para testing

**Alternativa considerada**: Threading con `threading.Thread`
- Más complejo de manejar
- Difícil de testear

---

### 3.4 Empaquetado: PyInstaller

**Decisión**: Usar PyInstaller en modo `--onedir` para producción

**Justificación:**

| Modo | Pros | Contras |
|------|------|---------|
| --onedir | Inicio más rápido, mejor detección de AV | Multiples archivos |
| --onefile | Un solo archivo | Inicio lento (extracción), más detecciones AV |

**Conclusión**: `--onedir` es mejor para distribución a usuarios reales.

---

## 4. Manejo de Configuración

### 4.1 Estructura de Configuración

```python
# config.json (ubicado en AppData/local/YouTubeDownloader/)
{
    "download_path": "C:/Users/{user}/Downloads",
    "preferred_quality": "1080p",
    "preferred_audio_quality": "320k",
    "output_template": "%(title)s.%(ext)s",
    "overwrite_files": false,
    "theme": "system"
}
```

### 4.2 Ubicaciones de Archivos

| Tipo | Ubicación |
|------|-----------|
| Configuración | `%APPDATA%/YouTubeDownloader/config.json` |
| Logs | `%APPDATA%/YouTubeDownloader/logs/` |
| Historial | `%APPDATA%/YouTubeDownloader/history.json` |
| Descargas | Definido por usuario (por defecto: Downloads) |

---

## 5. Manejo de Errores

### 5.1 Estrategia de Excepciones

```python
# src/app/core/exceptions.py

class YouTubeDownloaderError(Exception):
    """Excepción base para errores de la aplicación"""
    pass

class InvalidURLError(YouTubeDownloaderError):
    """URL inválida o no corresponde a YouTube"""
    pass

class VideoUnavailableError(YouTubeDownloaderError):
    """Video no disponible (eliminado, privado, etc.)"""
    pass

class FFmpegNotFoundError(YouTubeDownloaderError):
    """FFmpeg no encontrado en el sistema"""
    pass

class DownloadFailedError(YouTubeDownloaderError):
    """Error durante la descarga"""
    pass
```

### 5.2 Flujo de Manejo de Errores

```
┌────────────────┐
│   Usuario      │
│  introduce URL │
└───────┬────────┘
        ▼
┌────────────────┐     ┌─────────────────┐
│  Validar URL   │────▶│ Mostrar error   │
│  (Validator)   │     │ si es inválida  │
└───────┬────────┘     └─────────────────┘
        ▼
┌────────────────┐     ┌─────────────────┐
│  Obtener info  │────▶│ Mostrar error    │
│  del video     │     │ específico       │
└───────┬────────┘     └─────────────────┘
        ▼
┌────────────────┐     ┌─────────────────┐
│  Descargar     │────▶│ Registrar error  │
│  (Downloader)  │     │ y continuar      │
└───────┬────────┘     └─────────────────┘
        ▼
┌────────────────┐
│  Guardar en   │
│  historial    │
└───────────────┘
```

---

## 6. Testing

### 6.1 Estrategia de Testing

```
tests/
├── unit/                    # Tests unitarios
│   ├── test_downloader.py  # Lógica de descarga
│   ├── test_validator.py   # Validación de URLs
│   ├── test_config.py      # Gestión de configuración
│   └── test_file_utils.py  # Utilidades de archivo
├── integration/            # Tests de integración
│   ├── test_app.py         # Tests de la aplicación completa
│   └── test_download_flow.py # Flujo de descarga
└── fixtures/               # Datos de prueba
    ├── sample_urls.json
    └── mock_responses.py
```

### 6.2 Cobertura Objetivo

| Componente | Cobertura Mínima |
|------------|------------------|
| core/downloader.py | 80% |
| core/validator.py | 90% |
| core/config_manager.py | 85% |
| UI (eventos) | 60% |
| **Total** | **70%** |

### 6.3 Patrones de Testing

#### Test Unitario (Ejemplo)

```python
# tests/unit/test_validator.py
import pytest
from app.core.validator import URLValidator
from app.core.exceptions import InvalidURLError

class TestURLValidator:
    
    def test_valid_youtube_url_standard(self):
        """URL estándar de YouTube debe ser válida"""
        validator = URLValidator()
        result = validator.validate("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result is True
    
    def test_valid_youtube_short_url(self):
        """URL corta de YouTube debe ser válida"""
        validator = URLValidator()
        result = validator.validate("https://youtu.be/dQw4w9WgXcQ")
        assert result is True
    
    def test_invalid_url_raises_exception(self):
        """URL inválida debe lanzar excepción"""
        validator = URLValidator()
        with pytest.raises(InvalidURLError):
            validator.validate("not-a-url")
    
    def test_non_youtube_url_raises_exception(self):
        """URL que no es de YouTube debe lanzar excepción"""
        validator = URLValidator()
        with pytest.raises(InvalidURLError):
            validator.validate("https://vimeo.com/123456789")
```

#### Test con Mock (Ejemplo)

```python
# tests/unit/test_downloader.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.downloader import VideoDownloader
from app.core.exceptions import VideoUnavailableError

class TestVideoDownloader:
    
    @patch('app.core.downloader.YoutubeDL')
    def test_get_video_info_success(self, mock_ytdl):
        """Debe obtener información del video correctamente"""
        # Arrange
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            'id': 'dQw4w9WgXcQ',
            'title': 'Test Video',
            'duration': 180,
            'uploader': 'Test Channel'
        }
        mock_ytdl.return_value = mock_instance
        downloader = VideoDownloader()
        
        # Act
        info = downloader.get_video_info("https://youtube.com/watch?v=dQw4w9WgXcQ")
        
        # Assert
        assert info['title'] == 'Test Video'
        assert info['duration'] == 180
    
    @patch('app.core.downloader.YoutubeDL')
    def test_video_unavailable_raises_error(self, mock_ytdl):
        """Debe lanzar error si video no está disponible"""
        mock_instance = MagicMock()
        mock_instance.extract_info.side_effect = Exception("Video unavailable")
        mock_ytdl.return_value = mock_instance
        downloader = VideoDownloader()
        
        with pytest.raises(VideoUnavailableError):
            downloader.get_video_info("https://youtube.com/watch?v=invalid")
```

### 6.4 Ejecución de Tests

```bash
# Todos los tests con coverage
pytest --cov=src --cov-report=html --cov-report=term

# Tests unitarios solo
pytest tests/unit/ -v

# Tests con verbose
pytest tests/ -v --tb=short

# Tests que fallen primero
pytest tests/ -x

# Tests de un archivo específico
pytest tests/unit/test_downloader.py -v
```

---

## 7. Convenciones de Código

### 7.1 Estilo de Código

| Herrienta | Configuración |
|-----------|---------------|
| **Black** | Line length: 100, Python 3.11+ |
| **Flake8** | Max line length: 100, ignorar E203, W503 |
| **MyPy** | Strict mode, python_version 3.11 |

### 7.2 Estructura de Archivos

```python
"""
Módulo de ejemplo.

Descripción breve de qué hace el módulo.
"""

# Imports estándar
from typing import Optional
from pathlib import Path

# Imports de terceros
import customtkinter as ctk

# Imports locales
from app.core.exceptions import YouTubeDownloaderError
from app.utils.logger import get_logger


class ExampleClass:
    """
    Clase de ejemplo.
    
    Descripción más detallada de la clase.
    
    Attributes:
        attribute_1: Descripción del atributo.
    """
    
    def __init__(self, param_1: str, param_2: Optional[int] = None) -> None:
        """
        Inicializa la clase.
        
        Args:
            param_1: Descripción del parámetro.
            param_2: Descripción del parámetro opcional.
        """
        self.attribute_1 = param_1
        self._attribute_2 = param_2
    
    def public_method(self) -> str:
        """Método público con documentación."""
        return f"Result: {self.attribute_1}"
    
    def _private_method(self) -> None:
        """Método privado (internal use)."""
        pass
```

### 7.3 Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Clases | PascalCase | `VideoDownloader` |
| Funciones/Métodos | snake_case | `get_video_info()` |
| Constantes | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Variables | snake_case | `download_path` |
| Archivos Python | snake_case | `download_manager.py` |
| Tests | test_<module>.py | `test_downloader.py` |

---

## 8. Integración Continua (Futuro)

### 8.1 Pipeline Propuesto

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Conda
      uses: conda-incubator/setup-miniconda@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      shell: bash -l {0}
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    
    - name: Build executable
      run: pyinstaller build.spec
    
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: youtube-downloader
        path: dist/
```

---

## 9. Checklist de Implementación

- [ ] Estructura de proyecto creada
- [ ] Ambiente conda configurado
- [ ] Dependencias instaladas
- [ ] Logging configurado
- [ ] Excepciones personalizadas creadas
- [ ] Validator implementado y testeado
- [ ] Downloader implementado
- [ ] Config Manager implementado
- [ ] GUI básica (MainWindow)
- [ ] Download Tab implementada
- [ ] Settings Tab implementada
- [ ] Integración UI-Lógica
- [ ] Tests unitarios (>70% coverage)
- [ ] PyInstaller configurado
- [ ] Ejecutable generado y probado

---

## 10. Referencias

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp#readme)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Packaging Guide](https://packaging.python.org/)
