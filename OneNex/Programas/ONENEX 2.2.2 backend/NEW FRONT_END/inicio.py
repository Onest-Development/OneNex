from tkinter import messagebox
import serial, serial.tools.list_ports, threading
import json, os, datetime, time, sys
import customtkinter as ctk
from PIL import Image

import sys

from numpy.random.mtrand import set_state

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        #Propiedades de la app
        self.title("OneNex")
        self.geometry("1550x800")

        #Frame principal
        self.start_frame = ctk.CTkFrame(self, fg_color="white")
        self.start_frame.pack(fill="both", expand=True)

        #INICIALIZAR NUEVO FRAME PARA POSTERIOR MANIPULACION
        self.main_frame = ctk.CTkFrame(self)

        #LLEGAMOS A PRIMER FRAME
        self.primer_frame()


    """FRAME DE ENTRADA"""
    def primer_frame(self):
        self.frame_inicio_botones = ctk.CTkFrame(self.start_frame, fg_color="WHITE")
        self.frame_inicio_botones.pack(pady=75)
        self.nss_entry = ctk.CTkEntry(self.frame_inicio_botones, placeholder_text=" INGRESE USUARIO")
        self.nss_entry.configure(height=50, width=200)
        self.nss_entry.pack(pady=5)

        self.get_start_button = ctk.CTkButton(self.frame_inicio_botones, text="Iniciar", command=self.accion_registro, font=("Arial", 24, "bold"))
        self.get_start_button.configure(height=50, width=200)
        self.get_start_button.pack(pady=0)

        #Imagen de Fondo
        img_path = "media/onestlogo.jpg"
        self.bg_image = ctk.CTkImage(Image.open(img_path), size=(1350, 600))
        self.image_label = ctk.CTkLabel(self.start_frame, image=self.bg_image, text="")
        self.image_label.pack(fill="both", expand=True)


    def accion_registro(self):
        self.nss = self.nss_entry.get()
        if len(self.nss) == 11:
            self.coms_usbs()
        else:
            self.nss = ""
            title = "Warning"
            msg = "Este Usuario no es valido\nvolver a ingresar"
            messagebox.showwarning(title=title, message=msg)

if __name__ == "__main__":
    app = App()
    app.mainloop()