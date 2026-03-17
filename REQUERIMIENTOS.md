# Requisitos del Sistema - YouTube Downloader

Este documento especifica los requisitos funcionales y no funcionales de la aplicación YouTube Downloader, presentados como historias de usuario con sus criterios de aceptación.

---

## Historias de Usuario

### HU-001: Descarga de Video Individual

**Como** usuario de la aplicación,
**Quiero** descargar un video de YouTube proporcionando una URL,
**Para** poder verlo offline en mi computadora.

**Criterios de Aceptación:**

- [ ] La aplicación acepta una URL válida de YouTube (youtube.com/watch?v=..., youtu.be/..., youtube.com/shorts/...)
- [ ] La aplicación muestra un mensaje de error claro si la URL es inválida o está vacía
- [ ] El usuario puede seleccionar la calidad/tamaño del video antes de descargar
- [ ] La descarga muestra progreso en tiempo real (porcentaje, velocidad, tiempo estimado)
- [ ] El video se guarda en la ubicación seleccionada por el usuario
- [ ] El nombre del archivo descargado corresponde al título del video (sanitizado)
- [ ] Si la descarga se interrumpe, el usuario puede reanudar o reiniciar

---

### HU-002: Extracción de Audio

**Como** usuario que quiere escuchar música de YouTube,
**Quiero** extraer solo el audio de un video,
**Para** obtener un archivo de audio (MP3) sin el video.

**Criterios de Aceptación:**

- [ ] El usuario puede seleccionar "Solo audio" como opción de descarga
- [ ] El formato de salida por defecto es MP3
- [ ] La calidad de audio seleccionada es configurable (128k, 192k, 320k)
- [ ] El archivo de audio se guarda correctamente con extensión .mp3
- [ ] El proceso incluye etiquetado básico (título, artista) si está disponible

---

### HU-003: Selección de Calidad

**Como** usuario con limitaciones de almacenamiento,
**Quiero** elegir la calidad del video a descargar,
**Para** gestionar el espacio en disco.

**Criterios de Aceptación:**

- [ ] Antes de descargar, la aplicación muestra las calidades disponibles
- [ ] El usuario puede seleccionar: 1080p, 720p, 480p, 360p, o la mejor disponible
- [ ] La selección de calidad es persistente entre sesiones
- [ ] Si el usuario no selecciona calidad, se descarga la mejor disponible

---

### HU-004: Descarga de Playlist

**Como** usuario que quiere ver una lista de videos,
**Quiero** descargar todos los videos de una playlist de YouTube,
**Para** tener toda la colección disponible offline.

**Criterios de Aceptación:**

- [ ] La aplicación detecta si la URL es una playlist
- [ ] El usuario puede elegir descargar toda la playlist o un rango específico (ej: videos 1-10)
- [ ] Cada video de la playlist se descarga secuencialmente
- [ ] El progreso muestra qué video se está descargando y el total (ej: "Video 3 de 25")
- [ ] Si un video falla, la descarga continúa con los siguientes
- [ ] Al final se muestra un resumen de descargas exitosas y fallidas

---

### HU-005: Selección de Carpeta de Destino

**Como** usuario organizado,
**Quiero** elegir dónde se guardan los archivos,
**Para** mantener mis descargas organizadas.

**Criterios de Aceptación:**

- [ ] La aplicación tiene un botón para seleccionar carpeta de destino
- [ ] Se abre un dialog nativo de selección de carpeta de Windows
- [ ] La ruta seleccionada se muestra en la interfaz
- [ ] La selección de carpeta es persistente entre sesiones
- [ ] Si la carpeta no existe, se crea automáticamente

---

### HU-006: Configuración de Descarga

**Como** usuario con preferencias específicas,
**Quiero** configurar opciones de descarga,
**Para** personalizar el comportamiento de la aplicación.

**Criterios de Aceptación:**

- [ ] Existe una pestaña de configuración accesible desde la interfaz
- [ ] Opciones configurables:
  - [ ] Carpeta de descarga por defecto
  - [ ] Calidad de video preferida
  - [ ] Calidad de audio preferida
  - [ ] Nombre del archivo (plantilla)
  - [ ] ¿Sobrescribir archivos existentes?
- [ ] Los cambios se guardan automáticamente
- [ ] Las configuraciones se cargan al iniciar la aplicación

---

### HU-007: Interfaz Responsive

**Como** usuario de Windows,
**Quiero** una interfaz que responda correctamente,
**Para** tener una experiencia de usuario fluida.

**Criterios de Aceptación:**

- [ ] La ventana principal tiene un tamaño mínimo razonable (800x600)
- [ ] La ventana se puede maximizar y restaurar
- [ ] Los elementos de la interfaz no se superponen al redimensionar
- [ ] La interfaz funciona correctamente en Windows 10 y 11
- [ ] Los botones y elementos interactivos tienen feedback visual

---

### HU-008: Manejo de Errores

**Como** usuario que encuentra problemas,
**Quiero** recibir mensajes de error claros,
**Para** entender qué salió mal y cómo solucionarlo.

**Criterios de Aceptación:**

- [ ] Si el video no existe o está eliminado, se muestra mensaje claro
- [ ] Si no hay conexión a internet, se avisa al usuario
- [ ] Si FFmpeg no está instalado, se muestra instructions de instalación
- [ ] Si el video tiene restricciones (edad, región), se informa al usuario
- [ ] Los errores se muestran en un dialog modal, no como crash
- [ ] Los errores se registran en un archivo de log para diagnóstico

---

### HU-009: Historial de Descargas

**Como** usuario que quiere recordar qué descargó,
**Quiero** ver un historial de descargas,
**Para** encontrar fácilmente archivos descargados previamente.

**Criterios de Aceptación:**

- [ ] La aplicación guarda un registro de descargas recientes
- [ ] El historial muestra: fecha, título, URL, estado (éxito/fallo)
- [ ] El usuario puede abrir la carpeta donde se guardó el archivo
- [ ] El historial es navegable y muestra los últimos 50 items
- [ ] El usuario puede limpiar el historial

---

### HU-010: Ejecutable Independiente

**Como** usuario que no tiene Python instalado,
**Quiero** poder ejecutar la aplicación como un .exe,
**Para** usar la herramienta sin configurar un entorno de desarrollo.

**Criterios de Aceptación:**

- [ ] La aplicación se distribuye como un archivo .exe ejecutable
- [ ] El ejecutable funciona en Windows 10/11 sin Python instalado
- [ ] El ejecutable incluye todos los recursos necesarios (ícono, etc.)
- [ ] El ejecutable muestra un ícono personalizado en el taskbar
- [ ] El tiempo de inicio del ejecutable es razonable (<10 segundos)

---

## Requisitos No Funcionales

### RNF-001: Rendimiento

| Métrica | Criterio |
|---------|----------|
| Tiempo de inicio | < 3 segundos |
| Respuesta de UI | < 100ms para interacciones básicas |
| Descarga | Velocidad limitada solo por ancho de banda |

**Criterios de Aceptación:**

- [ ] La interfaz no se congela durante las descargas
- [ ] Las operaciones de red son asíncronas
- [ ] El uso de memoria es < 500MB durante operación normal

---

### RNF-002: Compatibilidad

| Componente | Requisito |
|------------|------------|
| Sistema Operativo | Windows 10, Windows 11 |
| Python | 3.11.x |
| FFmpeg | Requerido (external) |

**Criterios de Aceptación:**

- [ ] La aplicación funciona en Windows 10 (build 1903+)
- [ ] La aplicación funciona en Windows 11
- [ ] Se detectan y avisa si FFmpeg no está disponible

---

### RNF-003: Mantenibilidad

| Métrica | Criterio |
|---------|----------|
| Cobertura de tests | > 70% |
| Complejidad ciclomática | < 10 por función |

**Criterios de Aceptación:**

- [ ] El código sigue una estructura de capas (UI/Lógica/Datos)
- [ ] Las funciones tienen docstrings descriptivos
- [ ] Existe configuración para linters (flake8, black)
- [ ] Los tests unitarios cubren la lógica de negocio principal

---

### RNF-004: Usabilidad

| Aspecto | Requisito |
|---------|-----------|
| Idioma | Español (interfaz) |
| Accesibilidad | N/A (versión inicial) |
| Tema | Claro/Oscuro según sistema |

**Criterios de Aceptación:**

- [ ] Todos los textos de la interfaz están en español
- [ ] Los botones tienen texto descriptivo
- [ ] Las acciones tienen feedback visual (spinner, progreso)
- [ ] El tema se adapta al modo del sistema Windows

---

## Matriz de Trazabilidad

| ID | Prioridad | Estimación | Sprint |
|----|-----------|------------|--------|
| HU-001 | Alta | 3 puntos | 1 |
| HU-002 | Alta | 2 puntos | 1 |
| HU-003 | Alta | 2 puntos | 1 |
| HU-004 | Media | 3 puntos | 2 |
| HU-005 | Alta | 1 punto | 1 |
| HU-006 | Media | 2 puntos | 2 |
| HU-007 | Alta | 2 puntos | 1 |
| HU-008 | Alta | 2 puntos | 2 |
| HU-009 | Baja | 2 puntos | 3 |
| HU-010 | Alta | 3 puntos | 3 |

---

## Notas

- Las prioridades pueden ajustarse durante el desarrollo
- Los requisitos no funcionales aplican a todas las historias de usuario
- Se utilizará desarrollo iterativo: cada iteración entregable incluye un subconjunto de funcionalidades
