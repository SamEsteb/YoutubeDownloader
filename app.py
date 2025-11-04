import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import threading
import re
import sys
import ctypes
import sv_ttk

def get_system_downloads_dir():
    """
    Intenta obtener la carpeta de Descargas del sistema en Windows, macOS y Linux (XDG).
    Si falla, cae de vuelta a ~/Downloads.
    """
    home = os.path.expanduser("~")

    if sys.platform.startswith("linux"):
        try:
            cfg = os.path.join(home, ".config", "user-dirs.dirs")
            if os.path.exists(cfg):
                with open(cfg, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("XDG_DOWNLOAD_DIR"):
                            parts = line.split("=")
                            if len(parts) >= 2:
                                val = parts[1].strip().strip('"').strip()
                                val = val.replace("$HOME", home)
                                val = os.path.expandvars(val)
                                return os.path.normpath(val)
        except Exception:
            pass
        return os.path.join(home, "Downloads")

    if sys.platform == "darwin":
        return os.path.join(home, "Downloads")

    if os.name == "nt":
        try:
            class GUID(ctypes.Structure):
                _fields_ = [
                    ("Data1", ctypes.c_ulong),
                    ("Data2", ctypes.c_ushort),
                    ("Data3", ctypes.c_ushort),
                    ("Data4", ctypes.c_ubyte * 8),
                ]

            FOLDERID_Downloads = GUID(
                0x374DE290,
                0x123F,
                0x4565,
                (ctypes.c_ubyte * 8)(0x91, 0x64, 0x39, 0xC4, 0x92, 0x5E, 0x46, 0x7B),
            )

            SHGetKnownFolderPath = ctypes.windll.shell32.SHGetKnownFolderPath
            SHGetKnownFolderPath.argtypes = [
                ctypes.POINTER(GUID),
                ctypes.c_uint,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_wchar_p),
            ]
            path_ptr = ctypes.c_wchar_p()
            hr = SHGetKnownFolderPath(ctypes.byref(FOLDERID_Downloads), 0, None, ctypes.byref(path_ptr))
            if hr == 0 and path_ptr.value:
                return os.path.normpath(path_ptr.value)
        except Exception:
            pass
        return os.path.join(home, "Downloads")

    return os.path.join(home, "Downloads")

def abrir_carpeta_descarga():
    """
    Abre la carpeta de salida en el explorador de archivos del sistema.
    Usa la variable global 'NOMBRE_CARPET_SALIDA'.
    """
    path = NOMBRE_CARPET_SALIDA
    print(f"Abriendo carpeta: {path}")
    try:
        path_normalizada = os.path.normpath(path)
        
        if not os.path.isdir(path_normalizada):
            print(f"La ruta no existe, no se puede abrir: {path_normalizada}")
            messagebox.showwarning("Error", f"La carpeta de destino ya no existe:\n{path_normalizada}")
            return
            
        if sys.platform == "win32":
            os.startfile(path_normalizada)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path_normalizada])
        else:
            subprocess.Popen(["xdg-open", path_normalizada])
    except Exception as e:
        print(f"No se pudo abrir la carpeta: {e}")
        messagebox.showwarning("Error", f"No se pudo abrir la carpeta:\n{e}")

DEFAULT_DOWNLOAD_PATH = get_system_downloads_dir()
NOMBRE_CARPET_SALIDA = os.path.normpath(DEFAULT_DOWNLOAD_PATH)

PROGRESS_REGEX = re.compile(r"\[download\]\s+([0-9\.]+)%")

def seleccionar_carpeta():
    """
    Abre un diálogo para que el usuario seleccione una carpeta de destino.
    Actualiza la variable global y el label en la GUI.
    """
    global NOMBRE_CARPET_SALIDA
    path_seleccionado = filedialog.askdirectory(initialdir=NOMBRE_CARPET_SALIDA)

    if path_seleccionado:
        NOMBRE_CARPET_SALIDA = os.path.normpath(path_seleccionado)
        label_path.config(text=f"Guardar en: {NOMBRE_CARPET_SALIDA}")
        boton_abrir_carpeta.pack_forget() 

def iniciar_descarga_thread():
    """
    Función 'envoltorio' que se llama desde el botón 'Descargar'.
    Prepara la GUI y lanza la descarga en un hilo separado.
    """
    boton_abrir_carpeta.pack_forget() 
    
    boton_descargar.config(text="Descargando...", state="disabled")
    boton_carpeta.config(state="disabled")
    radio_video.config(state="disabled")
    radio_audio_wav.config(state="disabled")
    radio_audio_mp3.config(state="disabled")
    check_compatibilidad.config(state="disabled") 

    progress_var.set(0)
    status_var.set("Iniciando...")

    video_url = entry_url.get()
    opcion_elegida = var_opcion.get()

    if not video_url:
        messagebox.showwarning("Error", "Por favor, pega un enlace de YouTube.")
        reactivar_controles()
        return

    download_thread = threading.Thread(
        target=ejecutar_descarga,
        args=(video_url, opcion_elegida, root),
        daemon=True
    )
    download_thread.start()

def ejecutar_descarga(video_url, opcion_elegida, root_window):
    """
    Contiene la lógica principal de yt-dlp.
    Se ejecuta en un hilo separado.
    """
    try:
        safe_output_path = os.path.normpath(NOMBRE_CARPET_SALIDA)
        convirtiendo = False 

        if opcion_elegida == 'video':
            TIPO_DESCARGA = 'video'
            FORMATO_SALIDA = 'mp4'
        elif opcion_elegida == 'audio_wav':
            TIPO_DESCARGA = 'audio'
            FORMATO_SALIDA = 'wav'
        elif opcion_elegida == 'audio_mp3':
            TIPO_DESCARGA = 'audio'
            FORMATO_SALIDA = 'mp3'

        command_list = []

        if TIPO_DESCARGA == 'video':
            convirtiendo = True 
            
            if var_compatibilidad.get() == True:
                metodo_video = '--recode-video'
                status_var.set("Iniciando (con recodificación AAC)...")
            else:
                metodo_video = '--remux-video'
                status_var.set("Iniciando (copia rápida Opus)...")
            
            command_list = [
                'yt-dlp',
                '-P', safe_output_path,
                '-o', '%(title)s.%(ext)s',
                '-f', 'bv*+ba/b',
                metodo_video, FORMATO_SALIDA, 
                '--quiet', '--no-warnings',
                '--progress',
                video_url
            ]
        elif TIPO_DESCARGA == 'audio':
            convirtiendo = True 
            command_list = [
                'yt-dlp',
                '-P', safe_output_path,
                '-o', '%(title)s.%(ext)s',
                '-x',
                '--audio-format', FORMATO_SALIDA,
                '-f', 'bestaudio/best',
                '--quiet', '--no-warnings',
                '--progress',
                video_url
            ]

        print("--- INICIANDO DESCARGA (Confiando en el PATH) ---")
        print(f"Comando: {' '.join(command_list)}")
        print(f"Guardando en: {safe_output_path}")

        process = subprocess.Popen(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        for line in iter(process.stdout.readline, ''):
            if not line: break
            print(f"[yt-dlp]: {line.strip()}")
            match = PROGRESS_REGEX.search(line)
            if match:
                percent_str = match.group(1)
                percent_float = float(percent_str)
                progress_var.set(percent_float)
                if status_var.get() not in ["¡Descarga completada!", "Error en la descarga."]:
                    status_var.set(f"Descargando: {percent_float}%")

        
        if convirtiendo:
            print("[Debug] Descarga a 100%. Esperando post-procesamiento (ffmpeg)...")
            status_var.set("Procesando (convirtiendo)...")
        
        process.wait()
        stderr_output = process.stderr.read()

        if process.returncode == 0:
            progress_var.set(100)
            status_var.set("¡Descarga completada!")
            print("--- DESCARGA COMPLETADA CON ÉXITO ---")
            
            def exito_completo():
                messagebox.showinfo(
                    "¡Éxito!",
                    f"Descarga completada.\nGuardado en:\n{safe_output_path}"
                )
                boton_abrir_carpeta.pack(pady=(10, 0), fill="x", ipady=4)
            
            root_window.after(0, exito_completo)
            
        else:
            status_var.set("Error en la descarga.")
            print(f"--- ERROR DURANTE LA DESCARGA ---")
            print(stderr_output)
            print("-----------------------------------")
            root_window.after(0, lambda: messagebox.showerror(
                "Error de Descarga",
                f"yt-dlp falló.\nRevisa la consola para más detalles.\n\nError:\n{stderr_output[:500]}..."
            ))

    except Exception as e:
        print(f"--- ERROR INESPERADO EN EL HILO ---")
        print(str(e))
        print("-----------------------------------")
        status_var.set("Error inesperado.")
        root_window.after(0, lambda: messagebox.showerror("Error Inesperado", str(e)))

    finally:
        root_window.after(0, reactivar_controles)

def reactivar_controles():
    """
    Restaura la interfaz a su estado original.
    """
    boton_descargar.config(text="Descargar", state="normal")
    boton_carpeta.config(state="normal")
    radio_video.config(state="normal")
    radio_audio_wav.config(state="normal")
    radio_audio_mp3.config(state="normal")
    check_compatibilidad.config(state="normal") 
    entry_url.delete(0, tk.END)

root = tk.Tk()
root.title("Descargador YouTube")
root.iconbitmap(default='assets/logo.ico')
sv_ttk.set_theme("dark")

root.geometry("500x520")
root.minsize(500, 520)
root.resizable(False, False)

progress_var = tk.DoubleVar(root)
status_var = tk.StringVar(root, value="")
var_opcion = tk.StringVar(value="audio_mp3")
var_compatibilidad = tk.BooleanVar(value=True) 

frame = ttk.Frame(root, padding="20")
frame.pack(expand=True, fill="both")

label_url = ttk.Label(frame, text="Pega la URL de YouTube aquí:")
label_url.pack(pady=(0, 5), anchor="w")
entry_url = ttk.Entry(frame, width=80)
entry_url.pack(fill="x", ipady=4)

label_formato = ttk.Label(frame, text="Selecciona el formato de salida:")
label_formato.pack(pady=(15, 5), anchor="w")
radio_video = ttk.Radiobutton(frame, text="Video (MP4)", variable=var_opcion, value="video")
radio_video.pack(anchor="w", padx=10, pady=2)
radio_audio_wav = ttk.Radiobutton(frame, text="Audio (WAV)", variable=var_opcion, value="audio_wav")
radio_audio_wav.pack(anchor="w", padx=10, pady=2)
radio_audio_mp3 = ttk.Radiobutton(frame, text="Audio (MP3)", variable=var_opcion, value="audio_mp3")
radio_audio_mp3.pack(anchor="w", padx=10, pady=2)

separator = ttk.Separator(frame, orient='horizontal')
separator.pack(fill='x', pady=10, padx=10)

check_compatibilidad = ttk.Checkbutton(
    frame,
    text="Máxima Compatibilidad (Video a AAC)",
    variable=var_compatibilidad,
    onvalue=True,
    offvalue=False,
    style="Switch.TCheckbutton"
)
check_compatibilidad.pack(anchor="w", padx=10)

label_path_info = ttk.Label(frame, text="Destino:", font=("-weight", "bold"))
label_path_info.pack(pady=(15, 0), anchor="w")
frame_path = ttk.Frame(frame)
frame_path.pack(fill="x")
label_path = ttk.Label(frame_path, text=f"Guardar en: {NOMBRE_CARPET_SALIDA}", wraplength=350)
label_path.pack(side="left", fill="x", expand=True, pady=5)
boton_carpeta = ttk.Button(frame_path, text="Cambiar...", command=seleccionar_carpeta)
boton_carpeta.pack(side="right", padx=(10, 0))

boton_descargar = ttk.Button(
    frame,
    text="Descargar",
    command=iniciar_descarga_thread
)
boton_descargar.pack(pady=(20, 0), fill="x", ipady=8)

label_estado = ttk.Label(frame, textvariable=status_var)
label_estado.pack(pady=(15, 5), anchor="w")

progress_bar = ttk.Progressbar(
    frame,
    orient="horizontal",
    mode="determinate",
    variable=progress_var,
    maximum=100
)
progress_bar.pack(fill="x", ipady=4)

boton_abrir_carpeta = ttk.Button(
    frame,
    text="Abrir Carpeta de Descarga",
    command=abrir_carpeta_descarga 
)
boton_abrir_carpeta.pack_forget() 

root.mainloop()
