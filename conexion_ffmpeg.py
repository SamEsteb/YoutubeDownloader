import subprocess

def check_ffmpeg():
    try:
        # Ejecuta "ffmpeg -version" y captura la salida
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        print("✅ FFmpeg detectado correctamente.")
        print(result.stdout.splitlines()[0])  # Muestra solo la primera línea, ej. "ffmpeg version 6.1 ..."
    except FileNotFoundError:
        print("❌ FFmpeg no se encuentra instalado o no está en el PATH del entorno actual.")
    except subprocess.CalledProcessError as e:
        print("⚠️ Se encontró FFmpeg, pero ocurrió un error al ejecutarlo:")
        print(e)

if __name__ == "__main__":
    check_ffmpeg()
