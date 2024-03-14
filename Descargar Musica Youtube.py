import os
import threading
import tkinter as tk
from tkinter import HORIZONTAL, ttk, filedialog, messagebox
from ttkbootstrap import Style
from pytube import YouTube
from moviepy.editor import AudioFileClip
import re

# Define el tema BOOTSTRAP
BOOTSTRAP = 'flatly'

class DescargadorMP3YouTube:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de YouTube a MP3")
        self.root.geometry("600x250")
        self.url = tk.StringVar()
        self.ruta_salida = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Documents"))
        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Configuración del estilo
        style = Style(theme=BOOTSTRAP)
        style.configure('TButton', font=('Helvetica', 12), background='#4285F4', foreground='white')
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12))
        style.configure('TProgressbar', background='#4285F4')

        # Frame para la URL de YouTube
        frame_url = ttk.Frame(self.root)
        frame_url.pack(pady=10)
        ttk.Label(frame_url, text="URL de YouTube:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame_url, textvariable=self.url, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Frame para los botones
        frame_botones = ttk.Frame(self.root)
        frame_botones.pack(pady=10)
        ttk.Button(frame_botones, text="Descargar", command=self.iniciar_hilo_descarga).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(frame_botones, text="Vaciar URL", command=self.vaciar_url).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_botones, text="Seleccionar Carpeta", command=self.seleccionar_carpeta).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame_botones, text="Abrir Carpeta", command=self.abrir_carpeta).grid(row=0, column=3, padx=5, pady=5)

        # Barra de progreso
        self.barra_progreso = ttk.Progressbar(self.root, orient=HORIZONTAL, length=300, mode="determinate")
        self.barra_progreso.pack(pady=10)

    def seleccionar_carpeta(self):
        directorio = filedialog.askdirectory()
        if directorio:
            self.ruta_salida.set(directorio)

    def iniciar_hilo_descarga(self):
        if not self.url.get().strip():
            messagebox.showerror("Error", "Por favor, ingrese una URL de YouTube")
            return
        threading.Thread(target=self.descargar_video, daemon=True).start()
        self.root.after(100, self.actualizar_interfaz)

    def descargar_video(self):
        self.root.after(0, self.barra_progreso.start)
        try:
            yt = YouTube(self.url.get(), on_progress_callback=self.progreso_descarga)
            video = yt.streams.filter(only_audio=True).first()
            archivo_salida = video.download(output_path=self.ruta_salida.get())
            archivo_mp3 = os.path.join(self.ruta_salida.get(), self.sanitize_filename(yt.title) + ".mp3")
            clip_audio = AudioFileClip(archivo_salida)
            clip_audio.write_audiofile(archivo_mp3)
            clip_audio.close()
            os.remove(archivo_salida)
            self.mostrar_mensaje("Éxito", "Descarga completada")
        except Exception as e:
            self.mostrar_mensaje("Error", str(e))
        finally:
            self.root.after(0, self.barra_progreso.stop)

    def progreso_descarga(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = int((bytes_downloaded / total_size) * 100)
        self.barra_progreso["value"] = percentage

    def sanitize_filename(self, title):
        return re.sub(r'[\\/*?:"<>|]', "_", title)

    def mostrar_mensaje(self, titulo, mensaje):
        messagebox.showinfo(titulo, mensaje)

    def abrir_carpeta(self):
        os.startfile(self.ruta_salida.get())

    def vaciar_url(self):
        self.url.set("")

    def actualizar_interfaz(self):
        if self.barra_progreso["value"] < 100:
            self.root.after(100, self.actualizar_interfaz)
        else:
            self.root.after(0, self.barra_progreso.stop)

if __name__ == "__main__":
    root = tk.Tk()
    app = DescargadorMP3YouTube(root)
    root.mainloop()
