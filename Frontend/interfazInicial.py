import tkinter as tk
from tkinter.constants import *
from tkinter import filedialog, messagebox
import os

_location = os.path.dirname(__file__)

class Toplevel1:
    def __init__(self, top=None):
        top.geometry("550x509+565+119")
        top.minsize(120, 1)
        top.maxsize(1540, 845)
        top.resizable(1,  1)
        top.title("Proyecto de Inteligencia Artificial")
        top.configure(background="#c4fffc")
        self.top = top
        self.selected_file = None

        self.Label2 = tk.Label(self.top)
        self.Label2.place(relx=0.046, rely=0.077, height=95, width=313)
        self.Label2.configure(background="#c4fffc")
        self.Label2.configure(font="-family {System} -size 10 -weight bold")
        self.Label2.configure(text='''Participantes: Jim Gabriel Ariñez Bautista  
Yuri Daniel Ayaviri Quispe 
Humberto Alejandro Campos Torrejón  
Fabricio Alejandro Herrera Rojas  
Adam Jhoel Mamani 
Camila Belen Quispe Flores''')

        self.Label5 = tk.Label(self.top)
        self.Label5.place(relx=0.435, rely=0.491, height=261, width=284)
        self.Label5.configure(background="#c4fffc")
        photo_location = os.path.join(_location,"./src/si.png")
        global _img0
        _img0 = tk.PhotoImage(file=photo_location)
        self.Label5.configure(image=_img0)

        self.Label1 = tk.Label(self.top)
        self.Label1.place(relx=0.143, rely=0.02, height=24, width=415)
        self.Label1.configure(background="#c4fffc")
        self.Label1.configure(font="-family {System} -size 20 -weight bold")
        self.Label1.configure(text='''Clasificación de canciones''')

        self.Button1 = tk.Button(self.top)
        self.Button1.place(relx=0.065, rely=0.295, height=26, width=247)
        self.Button1.configure(background="#edd3fe", activebackground="#52f5ff")
        self.Button1.configure(font="-family {Rustic Story} -size 9 -weight bold -slant italic")
        self.Button1.configure(text='''Seleccionar archivo''', command= self.seleccionar_archivo)

        self.Label3 = tk.Label(self.top)
        self.Label3.place(relx=0.043, rely=0.393, height=60, width=235)
        self.Label3.configure(background="#c4fffc")
        self.Label3.configure(font="-family {System} -size 10 -weight bold")
        self.Label3.configure(text='''Características extraídas:              
BPM:              
Género real:              
Duración:''')

        self.Button2 = tk.Button(self.top)
        self.Button2.place(relx=0.065, rely=0.53, height=26, width=117)
        self.Button2.configure(activebackground="#52f5ff")
        self.Button2.configure(background="#edd3fe")
        self.Button2.configure(font="-family {Rustic Story} -size 9 -weight bold -slant italic")
        self.Button2.configure(text='''Clasificar Cancion''')

        self.Label4 = tk.Label(self.top)
        self.Label4.place(relx=0.055, rely=0.589, height=72, width=224)
        self.Label4.configure(background="#c4fffc")
        self.Label4.configure(font="-family {System} -size 10 -weight bold")
        self.Label4.configure(text='''Resultado:                                   
Género predicho:                 
Agente reward:''')
    def seleccionar_archivo(self):
                file_path = filedialog.askopenfilename(
                title="Seleccionar archivo WAV",
                filetypes=[("Archivos WAV", "*.wav")]
                )

                if file_path:
                        if not file_path.lower().endswith(".wav"):
                                messagebox.showerror("Formato inválido", "Por favor, seleccione un archivo con extensión .wav")
                                return

                self.selected_file = file_path

                file_name = os.path.basename(file_path)
                self.Button1.configure(text=file_name)

# Inicializacion de root.
root = tk.Tk()
root.protocol('WM_DELETE_WINDOW', root.destroy)
_top1 = root
_w1 = Toplevel1(_top1)

if __name__ == '__main__':
    root.mainloop()