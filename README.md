# YouTube Downloader

Aplicación de escritorio para Windows desarrollada en Python que permite descargar videos y audio de YouTube de manera sencilla y eficiente.

## Tecnologías

### Entorno

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Lenguaje | Python | 3.11.x |
| Gestor de entornos | Conda | Latest |
| Plataforma | Windows | 10/11 |

### Dependencias Principales

| Paquete | Propósito | Versión |
|---------|-----------|---------|
| **yt-dlp** | Biblioteca principal para descarga de videos | ^2024.12.x |
| **FFmpeg** | Procesamiento de audio/video (requerido por yt-dlp) | Latest |
| **CustomTkinter** | Interfaz gráfica moderna (wrapper de Tkinter) | ^5.2.x |
| **PyInstaller** | Empaquetado para generar ejecutable .exe | ^6.x |

### Dependencias de Desarrollo

| Paquete | Propósito | Versión |
|---------|-----------|---------|
| **pytest** | Framework de testing | ^8.x |
| **pytest-cov** | Cobertura de tests | ^4.x |
| **pytest-asyncio** | Testing de código asíncrono | ^0.23.x |
| **black** | Formateo de código | ^24.x |
| **flake8** | Linting | ^7.x |
| **mypy** | Type checking | ^1.x |

## Ambiente Conda

### Crear ambiente

```bash
# Crear ambiente con Python 3.11
conda create -n youtube-downloader python=3.11 -y

# Activar ambiente
conda activate youtube-downloader
```

### Instalar dependencias

```bash
# Instalar yt-dlp
pip install yt-dlp

# Instalar interfaz gráfica
pip install customtkinter

# Instalar dependencias de desarrollo
pip install pytest pytest-cov pytest-asyncio black flake8 mypy pyinstaller
```

### FFmpeg

FFmpeg es **requerido** para el funcionamiento de yt-dlp (especialmente para merge de video+audio y conversión de formatos).

#### Instalación en Windows (Desarrollo)

1. Descargar FFmpeg desde: https://www.gyan.dev/ffmpeg/builds/
2. Extraer el archivo .zip
3. Agregar la carpeta `bin` al PATH de Windows
4. Verificar instalación: `ffmpeg -version`

#### Uso con el Ejecutable (.exe)

La aplicación busca FFmpeg en el siguiente orden:

1. **Ruta configurada** en Configuración
2. **PATH del sistema** (donde esté instalado)
3. **Carpeta del ejecutable** (misma carpeta que el .exe)
4. **Ubicaciones comunes** del usuario

##### Opción recomendada: Misma carpeta que el .exe

Para que el ejecutable funcione sin instalar nada:

1. Descarga FFmpeg desde https://www.gyan.dev/ffmpeg/builds/
2. Extrae el contenido
3. Copia los archivos `ffmpeg.exe` y `ffprobe.exe` (están en la carpeta `bin`)
4. Pégalos en la **misma carpeta** donde está el `YouTubeDownloader.exe`

```
YouTubeDownloader/
├── YouTubeDownloader.exe    ← Tu app
├── ffmpeg.exe              ← Copiado aquí
└── ffprobe.exe             ← Copiado aquí
```

Esta es la forma más fácil de distribuir la app - solo llevás esos 3 archivos y funciona en cualquier PC con Windows 10/11.

## Estructura del Proyecto

```
YoutubeDownloader/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   ├── app/
│   │   ├── __init__.py
│   │   ├── gui/                # Componentes de UI
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py
│   │   │   ├── download_tab.py
│   │   │   └── settings_tab.py
│   │   └── core/               # Lógica de negocio
│   │       ├── __init__.py
│   │       ├── downloader.py
│   │       └── validator.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_downloader.py
│   │   └── test_validator.py
│   └── integration/
│       ├── __init__.py
│       └── test_app.py
├── assets/
│   ├── logo.ico
│   └── logo2.ico
├── REQUERIMIENTOS.md
├── DISEÑO.md
├── environment.yml
└── README.md
```

## Uso

### Desarrollo

```bash
# Activar ambiente
conda activate youtube-downloader

# Ejecutar aplicación
python src/main.py
```

### Ejecutable

El archivo ejecutable se genera en la carpeta `dist/` después de ejecutar el script de build.

## Notas

- Esta aplicación es para uso personal/educativo. Respeta los Términos de Servicio de YouTube.
- No descargues contenido protegido por derechos de autor sin autorización.
