from tkinter import messagebox
import serial, serial.tools.list_ports, threading
import json, os, datetime, time, sys
import customtkinter as ctk
from PIL import Image

import wms_client_idea2

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        #Propiedades de la app
        self.title("OneNex")
        self.geometry("1550x800")

        #Frame principal
        self.start_frame = ctk.CTkFrame(self)
        self.start_frame.pack(fill="both", expand=True)

        #INICIALIZAR NUEVO FRAME PARA POSTERIOR MANIPULACION
        self.main_frame = ctk.CTkFrame(self, fg_color="YELLOW")

        #VARIABLES GENERALES
        self.nss = ""
        self.documentos = {}
        self.doc_pendientes = []
        self.nombre_trabajo = ''
        self.documento_seleccionado = None
        self.pzas = 0
        self.cont_lib = 0
        self.referencias = []
        self.referencias_procesadas = []

        self.leyendo = False
        #self.serial_port = None

        #DESCARTAR PUERTOS DE COMUNICACION
        #self.puertos_pasados = wms_client_idea2.serial_ports()
        #self.puertos_presentes = []

        #LLEGAMOS A PRIMER FRAME
        self.primer_frame()

    """FRAME DE ENTRADA"""
    def primer_frame(self):
        #Imagen de Fondo
        img_path = "../media/onestlogo.jpg"
        self.bg_image = ctk.CTkImage(Image.open(img_path), size=(1550, 800))
        self.image_label = ctk.CTkLabel(self.start_frame, image=self.bg_image, text="")
        self.image_label.pack(fill="both", expand=True)

        self.nss_entry = ctk.CTkEntry(self.start_frame, placeholder_text=" INGRESE USUARIO")
        self.nss_entry.configure(height=50, width=200)
        self.nss_entry.place(x=240, y=180)

        self.get_start_button = ctk.CTkButton(self.start_frame, text="Iniciar", command=self.accion_registro, font=("Arial", 24, "bold"))
        self.get_start_button.configure(height=50, width=200)
        self.get_start_button.place(x=240, y=235)
    def accion_registro(self):
        self.nss = self.nss_entry.get()
        if len(self.nss) == 11:
            self.coms_usbs()
        else:
            self.nss = ""
            title = "Warning"
            msg = "Este Usuario no es valido\nvolver a ingresar"
            messagebox.showwarning(title=title, message=msg)
    def coms_usbs(self):
        self.puerto = wms_client_idea2.serial_ports()
        if self.puerto != []:
            print(self.puerto)
            self.descargar_documento()

            self.com_control= serial.Serial(port=self.puerto[0], baudrate=115200, timeout=1)
            self.com_cognex = serial.Serial(port=self.puerto[1], baudrate=115200, timeout=0.01)

        else:
            title = "Warning"
            msg = "DISPOSITIVOS NO ENCONTRADOS"
            messagebox.showwarning(title=title, message=msg)
            self.segundo_frame_seleccion()
    def descargar_documento(self):
        #Crear una carpeta de pendientes
        origen = os.getcwd()
        carpetas = os.listdir(origen)
        if "Pendientes" not in carpetas: os.mkdir("../Pendientes")

        #Descargamos informacion de ONE
        try:
            f = wms_client_idea2.obtener_devoluciones()
            data = f#json.load(f)
            self.documentos = {item["DOCTO_ENT_REFERENCIA"]: item for item in data}
            self.referencias = list(self.documentos.keys())

            #with open("documentos.json", "r", encoding="utf-8") as f:
            #    data = json.load(f)
            #    self.documentos = {item["DOCTO_ENT_REFERENCIA"]: item for item in data}
            #    self.referencias = list(self.documentos.keys())

        except Exception as e:
            messagebox.showwarning("Error", f"No Hay documentos por el momento:\n{e}")
            return

        #Crear lista de muestreo con documentos pendientes:
        self.doc_pendientes = os.listdir(f"{origen}\\Pendientes")
        if len(self.doc_pendientes) != 0:
            for pdte in self.doc_pendientes:
                if str(pdte[0:-6]) in self.referencias:
                    self.referencias.remove(str(pdte[0:-6]))
                    self.referencias.append(str(pdte[0:-5]))

        self.segundo_fame_seleccion()

    """FRAME SECUNDARIO"""
    def segundo_fame_seleccion(self):

        #OLVIDAR EL START_FRAME AL PRESIONAR BOTON DE INICIO
        self.start_frame.pack_forget()
        self.nss_entry.place_forget()
        self.get_start_button.place_forget()
        #EMPAQUETAR EL MAIN_FRAME PARA SU RESPECTIVO USO
        self.main_frame.pack(fill="both", expand=True)

        #LABEL DE MUESTRA DE INFORMACION
        self.label_var = f"Operador: {self.nss}\n\nSeleccione un documento:"
        self.label_title = ctk.CTkLabel(self.main_frame, text=self.label_var, font=("Arial", 32, 'bold'))
        self.label_title.pack(pady=40)

        # OptionMenu sin selección inicial
        # ACTIVACION DE BOTON PARA SELECCION DE DOCUMENTO: documento_seleccionado_callback
        self.doc_selector = ctk.CTkOptionMenu(
            self.main_frame,
            values=[""] + self.referencias,
            command=self.comando_seleccion_documento,
            height=40, width=200,
            font=("Arial", 32, "bold")
        )
        self.doc_selector.set("")
        self.doc_selector.pack(pady=20)

        # Crear botones, pero NO mostrarlos aún
        #BOTON DE CONTINUACION CON DOCUMENTO SELECCIONADO
        self.next_button = ctk.CTkButton(self.main_frame, text="Siguiente", command=self.decidir_documento, height=40, width=200, font=("Arial", 16, 'bold'))

        #ENTRY BUTTON
        #Entrada para buscar manualmente documentos
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.pack(pady=40)
        self.manual_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Escanea", height=20, width=200, font=("Arial", 32, "bold"))
        self.manual_entry.pack(side="left", anchor="ne")
        self.manual_button = ctk.CTkButton(self.search_frame, text="Buscar", height=20, width=200, command=self.decidir_documento, font=("Arial", 32, "bold"))
        self.manual_button.pack(side="right",anchor="nw")


        # FORMATO de Resultados de los detalles del documento (vacío por ahora)
        self.label_doc_title = ctk.CTkLabel(self.main_frame, text="",font=("Arial", 32, 'bold'))
        #self.resultado_label = ctk.CTkLabel(self.main_frame, text="", justify="left", anchor="w", wraplength=650)
        self.totales_label = ctk.CTkLabel(self.main_frame, text="",font=("Arial", 32, 'bold'))


        #refresh button
        self.refresh_button = ctk.CTkButton(self.main_frame, text="Refresh", command=self.refresh_info, fg_color="gold", text_color="black", height=40, width=200, font=("Arial", 16, 'bold'))
        self.refresh_button.pack(pady=10)

        #resend button
        self.resend_button = ctk.CTkButton(self.main_frame, text="RE-SEND", command=self.resend_info, fg_color="orange", text_color="black", height=40, width=200, font=("Arial", 16, 'bold'))
        self.resend_button.pack(pady=10)

        #returnn button:
        self.ret2main = ctk.CTkButton(self.main_frame, text="SALIR", command=self.returned, fg_color="red", text_color="white", height=40, width=200, font=("Arial", 16, 'bold'))
        self.ret2main.pack(pady=20)
    def comando_seleccion_documento(self, value):
        if value != "":
            self.next_button.pack(pady=10)
            self.refresh_button.pack_forget()
            self.resend_button.pack_forget()
            self.search_frame.pack_forget()
            self.ret2main.pack_forget()
        else:
            self.next_button.pack_forget()
            self.search_frame.pack(pady=40)
            self.refresh_button.pack(pady=10)
            self.resend_button.pack(pady=10)
            self.ret2main.pack(pady=20)
    def decidir_documento(self):
        valores = [""] + self.referencias

        seleccion_entry = self.manual_entry.get()
        seleccion_button = self.doc_selector.get()

        if seleccion_entry:
            if seleccion_entry.upper() not in valores:
                msg = f"Documento {seleccion_entry} no encontrado"
                messagebox.showwarning(message=msg)
            else:
                self.trabajando_documento(seleccion_entry.upper())

        if seleccion_button:
            if seleccion_button == "CIEGO":pass
            else:self.trabajando_documento(seleccion_button)
    def refresh_info(self):
        self.doc_selector.pack_forget()
        self.next_button.pack_forget()
        self.label_title.pack_forget()
        self.search_frame.pack_forget()
        self.refresh_button.pack_forget()
        self.resend_button.pack_forget()
        self.resend_button.pack_forget()
        self.ret2main.pack_forget()
        self.descargar_documento()
    def resend_info(self):
        def doc_reenviar():
            now = datetime.datetime.now()
            y, m, d = now.year, now.month, now.day
            path = f"COGNEX_DOCS\\{y}\\{m}\\{d}"
            try:
                docs = os.listdir(path)
                docs2resend = []
                for i in docs:
                    if ".json" in str(i): docs2resend.append(i)
                return docs2resend

            except:
                messagebox.showerror(title="Error", message="No hay documentos creados el dia de hoy")
                return []
        def limpiar(valor):
            if valor != "":
                enviar_reenvio.pack(pady=10)
                buscar_reenvio.pack_forget()
            else:
                enviar_reenvio.pack_forget()
                buscar_reenvio.pack(pady=20)
        def preparar():
            valor = doc_resend.get()
            now = datetime.datetime.now()
            y, m, d = now.year, now.month, now.day
            path = f"COGNEX_DOCS\\{y}\\{m}\\{d}"
            j_file = open(f"{path}\\{valor}", "r")
            j_file = json.load(j_file)
            reenviar(j_file)
        def buscar():
            current = os.getcwd()
            filename = ctk.filedialog.askopenfilename(initialdir=current,
                                                      title="Select a File",
                                                      filetypes=(("Json Files", "*.json"),
                                                                 ("all files", "*.*")))
            if filename == '':
                msg = "Archivo JSON no seleccionado\n"
                messagebox.showwarning(message=msg, title="Warning")
                resend_root.destroy()
            else:
                j_file = open(f"{filename}", "r")
                j_file = json.load(j_file)
                reenviar(j_file)
        def reenviar(j_file):
            while True:
                ans = wms_client_idea2.enviar_json(j_file)
                if ans[0] != 500:
                    messagebox.showinfo(title="Exito", message=f"DOCUMENTO ENVIADO CON EXITO\n{ans}")
                    resend_root.destroy()
                    break
                else:
                    msn="El documento no pudo ser enviado\nverifique coneccion al servidor\n\n¿Desea que intentarlo de nuevo?"
                    ans = messagebox.askokcancel(title="Error", message=msn)
                    if ans == False: break

        resend_root = ctk.CTk()
        resend_root.title("Reenviar informacion")
        resend_root.geometry("600x400")
        resend_root.resizable(False, False)

        title = ctk.CTkLabel(resend_root, text="ENVIAR DOCUMENTO", font=("Arial", 16, 'bold'))
        title.pack(pady=10)

        # OptionMenu sin selección inicial
        referencias = doc_reenviar()
        doc_resend = ctk.CTkOptionMenu(
            resend_root,
            values=[""] + referencias,
            command=limpiar,
            height=40, width=200,
            font=("Arial", 32, "bold")
        )
        doc_resend.set("")
        doc_resend.pack(pady=20)

        buscar_reenvio = ctk.CTkButton(resend_root, text="BUSCAR", command=buscar, height=40, width=200, font=("Arial", 16, 'bold'))
        buscar_reenvio.pack(pady=20)

        enviar_reenvio = ctk.CTkButton(resend_root, text="ENVIAR", command=preparar, height=40, width=200, fg_color="green", font=("Arial", 16, 'bold'))
        resend_root.mainloop()
    def returned(self):
        msn = "¿Desea regresar al inicio para cambiar usuario?"
        ans = messagebox.askokcancel(title="Regresar", message=msn)
        if ans == True:
            self.label_title.pack_forget()
            self.doc_selector.pack_forget()
            self.search_frame.pack_forget()
            self.refresh_button.pack_forget()
            self.resend_button.pack_forget()
            self.next_button.pack_forget()
            self.ret2main.pack_forget()
            self.main_frame.pack_forget()

            self.com_control.close()
            self.com_cognex.close()
            self.start_frame.pack(fill="both", expand=True)

            #OLVIDAR TABLA
            try:
                self.form_tab_L.place_forget()
                self.form_tab_ML.place_forget()
                self.form_tab_MR.place_forget()
                self.form_tab_R.place_forget()

                self.form_tab_BL.place_forget()
                self.form_tab_BML.place_forget()
                self.form_tab_BMR.place_forget()
                self.form_tab_BR.place_forget()
            except: pass

            self.primer_frame()

    """FRAME DE PROCESAMIENTO"""
    def trabajando_documento(self, seleccion):
        # Ocultar menú y botón
        self.doc_selector.pack_forget()
        self.next_button.pack_forget()
        self.label_title.pack_forget()
        self.search_frame.pack_forget()
        self.refresh_button.pack_forget()
        self.resend_button.pack_forget()

        ###########
        #informacion general
        documento = self.documentos.get(seleccion)

        if not documento: return
        self.documento_seleccionado = documento

        ############
        #FORMATO DE DOCUMENTACION
        doc_ref = documento["DOCTO_ENT_REFERENCIA"]

        self.worker_frame = ctk.CTkFrame(self.main_frame, fg_color="blue", height=200, width=1550)
        self.worker_frame.place(x=0, y=0)
        self.concentrado = ctk.CTkLabel(master=self.main_frame, text=f"#CONCENTRADO: {doc_ref}", font=("Arial", 32, "bold"))
        self.concentrado.place(x=100, y=65)

        ################
        #BOTONES
        self.inicio_button = ctk.CTkButton(self.worker_frame, text="INICIO", fg_color="green", command=self.iniciar_lectura, height=40, width=200, font=("Arial", 32, 'bold'))
        self.regresar_button = ctk.CTkButton(self.worker_frame, text="REGRESAR", fg_color="gold", text_color="black", command=self.regresar_a_selector,height=40, width=200, font=("Arial", 32, 'bold'))
        self.finalizar_button = ctk.CTkButton(self.worker_frame, text="FINALIZAR", fg_color="red", command=self.finalizar_proceso, height=40, width=200, font=("Arial", 32, 'bold'))
        self.ver_detalle = ctk.CTkButton(self.worker_frame, text="Ver Detalle", fg_color="purple", command=self.ver_documento, height=40, width=200, font=("Arial", 32, 'bold'))


        self.inicio_button.configure(state="normal")
        self.inicio_button.place(x=650, y=60)
        self.regresar_button.place(x=900, y=60)


        titles = ("SKU", "ETIQUETA", "ESPERADOS", "ESCANEADO")
        #######################
        #TABLA SUPERIOR
        self.form_tab_L = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_L.place(x=36, y=320)
        self.form_tab_ML = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_ML.place(x=409, y=320)
        self.form_tab_MR = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_MR.place(x=782, y=320)
        self.form_tab_R = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_R.place(x=1135, y=320)

        self.text_tab_L = ctk.CTkLabel(self.form_tab_L, text=f"{titles[0]}", height=20, width=115, font=("Arial", 36, "bold"))
        self.text_tab_L.place(relx=0.5, rely=0.5, anchor="center")
        self.text_tab_ML = ctk.CTkLabel(self.form_tab_ML, text=f"{titles[1]}", height=20, width=115, font=("Arial", 36, "bold"))
        self.text_tab_ML.place(relx=0.5, rely=0.5, anchor="center")
        self.text_tab_MR = ctk.CTkLabel(self.form_tab_MR, text=f"{titles[2]}", height=20, width=115, font=("Arial", 36, "bold"))
        self.text_tab_MR.place(relx=0.5, rely=0.5, anchor="center")
        self.text_tab_R = ctk.CTkLabel(self.form_tab_R, text=f"{titles[3]}", height=20, width=115, font=("Arial", 36, "bold"))
        self.text_tab_R.place(relx=0.5, rely=0.5, anchor="center")


        #######################
        #TABLA INFERIOR
        self.form_tab_BL = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_BL.place(x=36, y=400)
        self.form_tab_BML = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_BML.place(x=409, y=400)
        self.form_tab_BMR = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_BMR.place(x=782, y=400)
        self.form_tab_BR = ctk.CTkFrame(self, height=90, width=375, border_width=1, border_color="black", corner_radius=0)
        self.form_tab_BR.place(x=1135, y=400)

        self.lab_sku = ctk.CTkLabel(self.form_tab_BL, text="", height=20, width=115, font=("Arial", 36, "bold"))
        self.lab_sku.place(relx=0.5, rely=0.5, anchor="center")
        self.lab_etiqueta = ctk.CTkLabel(self.form_tab_BML, text="", height=20, width=115, font=("Arial", 36, "bold"))
        self.lab_etiqueta.place(relx=0.5, rely=0.5, anchor="center")
        self.lab_teorico = ctk.CTkLabel(self.form_tab_BMR, text="", height=20, width=115, font=("Arial", 36, "bold"))
        self.lab_teorico.place(relx=0.5, rely=0.5, anchor="center")
        self.lab_escaneado = ctk.CTkLabel(self.form_tab_BR, text="", height=20, width=115, font=("Arial", 36, "bold"))
        self.lab_escaneado.place(relx=0.5, rely=0.5, anchor="center")

        #FIN DE LA TABLA MANUAL
        #######################

        self.resumen = ctk.CTkLabel(self.worker_frame, text="RESUMEN", font=("Arial", 48, "bold"))
        self.resumen.place(x=650, y=150)

        # Mostrar resultado del documento
        self.actualizar_resultado_label()
        self.totales_label.place(x=440, y=220)

        #Mostrar boton Ver detalle
        self.ver_detalle.place(x=130, y=550)

        # Mostrar botón INICIO solamente
        self.inicio_button.configure(state="normal")
        self.inicio_button.place(x=650, y=60)
        self.regresar_button.place(x=900, y=60)
        #PREPARAR VARIABLES ANTES DE MOSTRAR EN PANTALLA
    def actualizar_resultado_label(self):

        documento = self.documento_seleccionado

        ###########################
        #FORMATO

        #Detalles del documento

        detalles = documento.get("DETALLES", [])
        #texto_resultado = ""

        for detalle in detalles:
            self.pzas += int(detalle['DET_ENT_CANT_PED'])
            self.cont_lib += int(detalle['DET_ENT_CANT_CONF'])

            """
            texto_resultado += (
                f"- SKU: {detalle['PRODUCTO_SKU']}, "
                f"Etiqueta: {detalle['DET_ENT_ETIQUETA']}, "
                f"Pedidas: {detalle['DET_ENT_CANT_PED']}, "
                #f"Recibidas: {detalle['DET_ENT_CANT_REC']}, "
                f"Confirmadas: {detalle['DET_ENT_CANT_CONF']}\n"
            )
            """

        #self.resultado_label.configure(text=texto_resultado)

        self.totales_label.configure(text=f"Total Libros: {self.pzas}       Total Escaneados: {self.cont_lib}")

    ##############
    #PRIMERA OPCION - Comenzar a escanear
    def iniciar_lectura(self):
        if self.leyendo: return
        self.leyendo = True

        banda_msg = "ARRANQUE"
        self.inicio_uart(banda_msg)

        # Desactivar el botón INICIO
        self.inicio_button.configure(state="disabled", fg_color="gray")

        # Activar y mostrar el botón FINALIZAR & PAUSAR
        self.pausar_button.place(x=900, y=550)
        self.finalizar_button.configure(state="normal")
        self.finalizar_button.place(x=1150, y=60)

        #Guardar primera copia
        self.guardar_autonomo()
        # Comenzar lectura periódica
        self.cognex_lectura_directa()
    def inicio_uart(self, msg_banda):
        try:
            self.com_control.write(msg_banda.encode('utf-8'))
            #print(f"✅ Mensaje enviado por {puerto}: {mensaje}")

        except Exception as e:
            messagebox.showerror(title="warning", message=f"{e}")
            #print(f"❌ Error al enviar mensaje: {e}")
    def guardar_autonomo(self):
        nombre = str(self.documento_seleccionado['DOCTO_ENT_REFERENCIA'])+'P'
        doc2save = self.documento_seleccionado
        with open(f"Pendientes\\{nombre}.json", "w", encoding="utf-8") as archivo:
            json.dump(doc2save, archivo, ensure_ascii=False, indent=4)
    ######################
    #CONTROL DE DIFERENTES LECTURAS
    def libro_paro(self, mensaje, evento=False):
        while True:
            if  evento == False:
                ans = messagebox.showwarning(title="WARNING", message=mensaje)
                if str(ans) == "ok":
                    banda_msg = "PARO_LIBRO"
                    self.inicio_uart(banda_msg)
                    break
            else:
                ans = messagebox.askokcancel(title="WARNING", message=mensaje)
                if ans == True:
                    self.event_manual_entry()
                    break
                else:
                    banda_msg = "PARO_LIBRO"
                    self.inicio_uart(banda_msg)
                    break

    #############
    #ENTRY NUEVO PARA ESCANEO MANUAL
    def cognex_lectura_directa(self):
        if not self.leyendo:return
        try:
            data = ""
            if self.com_cognex.in_waiting > 0:
                data = self.com_cognex.readline().decode('utf-8').strip()
                print(f"Recibido: {data}")
                if data == "PASS" or len(data) > 13 or len(data) < 13 :
                    self.inicio_uart("PARO")
                    mensaje = "NO SE ENCONTRÓ ETIQUETA EN EL LIBRO."
                    self.libro_paro(mensaje)
                #SECCION FUTURA  A MANIPULAR CON CODIGOS MULTIPLES
                elif len(data) == 13:
                    self.procesar_dato_entrada(data)

                self.com_cognex.reset_input_buffer()
                self.com_cognex.reset_output_buffer()
                data=""
                print("limpio", data)
            else:
                data=""
                print("limpio", data)
                self.com_cognex.reset_input_buffer()
                self.com_cognex.reset_output_buffer()
        except Exception as e:
            messagebox.showerror(title="ERROR", message=f"{e}")
        self.after(100, self.cognex_lectura_directa)
    def procesar_dato_entrada(self, dato):
        detalles = self.documento_seleccionado["DETALLES"]
        encontrado = False

        for detalle in detalles:
            if detalle["DET_ENT_ETIQUETA"] == dato:
                encontrado = True
                if int(detalle['DET_ENT_CANT_PED']) != 0 and int(detalle["DET_ENT_CANT_CONF"]) >= int(detalle["DET_ENT_CANT_PED"]):
                    banda_msg = "PARO"
                    self.inicio_uart(banda_msg)

                    mensaje = f"LIBRO SOBRANTE\n¿DESEA AGREGAR UNA PIEZA ADICIONAL?\n\n{dato}"
                    add = messagebox.askyesno(title="Libro sobrante", message=mensaje)
                    if add == True:
                        self.cont_lib += 1
                        detalle["DET_ENT_CANT_CONF"] += 1

                        self.lab_sku.configure(text=f"{detalle['PRODUCTO_SKU']}")
                        self.lab_etiqueta.configure(text=f"{detalle['DET_ENT_ETIQUETA']}")
                        self.lab_teorico.configure(text=f"{detalle['DET_ENT_CANT_PED']}")
                        self.lab_escaneado.configure(text=f"{detalle['DET_ENT_CANT_CONF']}")

                        self.totales_label.configure(text=f"Objs. Totales: {self.pzas}       Obj Contados: {self.cont_lib}")

                        banda_msg = "ARRANQUE"
                        self.inicio_uart(banda_msg)

                        break

                    else:
                        banda_msg = "ARRANQUE"
                        self.inicio_uart(banda_msg)



                    #self.libro_paro(mensaje)
                    #break

                else:
                    self.cont_lib += 1
                    detalle["DET_ENT_CANT_CONF"] += 1
                    """
                    resultado_individual = (
                        f"{detalle['PRODUCTO_SKU']},"
                        f"{detalle['DET_ENT_ETIQUETA']},"
                        f"{detalle['DET_ENT_CANT_PED']},"
                        f"{detalle['DET_ENT_CANT_CONF']}"
                    )"""
                    #if int(detalle['DET_ENT_CANT_PED']) == 0: pass
                    #resultado_individual = resultado_individual + "OBJETO NO LISTADO\n"

                    self.lab_sku.configure(text=f"{detalle['PRODUCTO_SKU']}")
                    self.lab_etiqueta.configure(text=f"{detalle['DET_ENT_ETIQUETA']}")
                    self.lab_teorico.configure(text=f"{detalle['DET_ENT_CANT_PED']}")
                    self.lab_escaneado.configure(text=f"{detalle['DET_ENT_CANT_CONF']}")

                    #self.resultado_label.configure(text=resultado_individual)
                    #self.resultado_label.place(x=50, y=175)
                    self.totales_label.configure(text=f"Objs. Totales: {self.pzas}       Obj Contados: {self.cont_lib}")

                    break

        #######################
        """seccion CANCELADA"""
        #######################
        """
        if encontrado == False:
            banda_msg = "PARO"
            self.inicio_uart(banda_msg)
            mensaje = f"LIBRO {dato} NO SE ENCUENTRA EN EL DOCUMENTO"
            self.libro_paro(mensaje)
        """

        ########################
        """SECCION REACTIVADA"""
        ########################
        if not encontrado:
            nuevo = {
                "DET_ENT_ID": 0,
                "PRODUCTO_SKU": 0,
                "DET_ENT_ETIQUETA": dato,
                "DET_ENT_CANT_PED": 0,
                "DET_ENT_CANT_REC": 0,
                "DET_ENT_CANT_CONF": 1
            }
            detalles.append(nuevo)
            self.cont_lib += 1

            self.lab_sku.configure(text=f"{nuevo['PRODUCTO_SKU']}")
            self.lab_etiqueta.configure(text=f"{nuevo['DET_ENT_ETIQUETA']}")
            self.lab_teorico.configure(text=f"{nuevo['DET_ENT_CANT_PED']}")
            self.lab_escaneado.configure(text=f"{nuevo['DET_ENT_CANT_CONF']}")

            self.totales_label.configure(text=f"Objs. Totales: {self.pzas}       Obj Contados: {self.cont_lib}")

        self.guardar_autonomo()

    ##############
    #SEGUNDA OPCION - REGRESAR A MENU ANTERIOR
    def regresar_a_selector(self):
        msg = "Si regresa, los datos procesados iniciaran nuevamente en cero.\n¿Desea regresar? "
        self.back_confirm = messagebox.askyesno(title="WARNING", message=msg)
        if self.back_confirm == True:
            try:
                nombre = str(self.documento_seleccionado['DOCTO_ENT_REFERENCIA'])+'P'
                nombre_lista = str(nombre)+'.json'
                if nombre_lista in self.doc_pendientes:
                    self.doc_pendientes.remove(nombre_lista)
                os.remove(f'Pendientes\\{nombre}.json')
            except: pass

            self.regreso_general()
    def regreso_general(self):
        banda_msg = "PARO"
        self.inicio_uart(banda_msg)


        self.leyendo = False  # Detener lectura serial si estaba activa
        #self.resultado_label.pack_forget()
        self.inicio_button.configure(fg_color="green")
        self.inicio_button.place_forget()
        self.regresar_button.place_forget()
        self.concentrado.place_forget()
        #OLVIDAR TITULOS
        self.control_frame.place_forget()
        #OLVIDAR TABLA
        self.form_tab_L.place_forget()
        self.form_tab_ML.place_forget()
        self.form_tab_MR.place_forget()
        self.form_tab_R.place_forget()

        self.form_tab_BL.place_forget()
        self.form_tab_BML.place_forget()
        self.form_tab_BMR.place_forget()
        self.form_tab_BR.place_forget()


        #self.formato_onest_frame.place_forget()
        #self.text_format_label.pack_forget()
        self.resumen.place_forget()
        self.pausar_button.place_forget()
        self.finalizar_button.place_forget()

        #self.resultado_label.place_forget()

        self.totales_label.place_forget()
        self.ver_detalle.place_forget()
        self.ret2main.pack_forget()

        try: self.window_frame.place_forget()
        except: pass

        #self.label_title.pack_forget()
        #self.label_title.configure(text="Seleccione un documento:")
        #self.label_doc_title.pack_forget()
        #self.totales_label.pack_forget()
        #self.finalizar_button.pack_forget()
        #self.doc_selector.pack_forget()
        #self.doc_selector.set("")
        #self.doc_selector.pack(pady=10)
        #self.next_button.pack_forget()
        #self.concentrado.place_forget()

        self.pzas = 0
        self.cont_lib = 0

        self.descargar_documento()

    ##############
    #TERCERA OPCION - FINALIZAR
    def guardado(self):
        now = datetime.datetime.now()
        year = str(now.year)
        month = str(now.month)
        day = str(now.day)

        current = os.getcwd()
        carpetas = os.listdir(current)
        name = 'COGNEX_DOCS'
        try:
            if name not in carpetas:
                os.mkdir(f"{current}\\{name}")
                os.mkdir(f"{current}\\{name}\\{year}")
                os.mkdir(f"{current}\\{name}\\{year}\\{month}")
                os.mkdir(f"{current}\\{name}\\{year}\\{month}\\{day}")
            else:
                carpetas = os.listdir(f"{current}\\{name}")
                if str(year) not in carpetas:
                    os.mkdir(f"{current}\\{name}\\{year}")
                    os.mkdir(f"{current}\\{name}\\{year}\\{month}")
                    os.mkdir(f"{current}\\{name}\\{year}\\{month}\\{day}")
                else:
                    carpetas = os.listdir(f"{current}\\{name}\\{year}")
                    if str(month) not in carpetas:
                        os.mkdir(f"{current}\\{name}\\{year}\\{month}")
                        os.mkdir(f"{current}\\{name}\\{year}\\{month}\\{day}")
                    else:
                        carpetas = os.listdir(f"{current}\\{name}\\{year}\\{month}")
                        if str(day) not in carpetas: os.mkdir(f"{current}\\{name}\\{year}\\{month}\\{day}")

            path_saver = f"{current}\\{name}\\{year}\\{month}\\{day}"
        except:
            path_saver = f"{current}\\{name}\\{year}\\{month}\\{day}"

        return path_saver
    def finalizar_proceso(self):
        banda_msg = "PARO"
        self.inicio_uart(banda_msg)

        referencia = self.documento_seleccionado.get("DOCTO_ENT_REFERENCIA", "desconocido")
        nombre_archivo = f"{referencia}"
        carpeta = self.guardado()

        #os.makedirs(carpeta, exist_ok=True)
        ruta_completa = os.path.join(carpeta, str(f"{nombre_archivo}.json"))

        # Marcar como procesado
        #self.referencias_procesadas.append(referencia)

        # Eliminar de la lista de referencias activas
        #if referencia in self.referencias:
        #    self.referencias.remove(referencia)

        ###################
        #PARTE 1 GUARDAR DOCUMENTO
        with open(ruta_completa, "w", encoding="utf-8") as f:
            json.dump(self.documento_seleccionado, f, indent=4, ensure_ascii=False)
            f.close()

        objs = self.documento_seleccionado["DETALLES"]
        no_listados = []
        for obj in objs:
            if obj["DET_ENT_CANT_PED"] == 0: no_listados.append(obj)

        doc = self.documento_seleccionado
        now = datetime.datetime.now()
        y, m, d = now.year, now.month, now.day
        date = f"{y}-{m}-{d}"
        nss = self.nss
        wms_client_idea2.formato_impreso(doc, no_listados, date, carpeta, nombre_archivo, nss)

        messagebox.showinfo("Éxito", f"Documento guardado en:\n{ruta_completa}")


        while True:

            final_doc = self.documento_seleccionado
            respuesta = wms_client_idea2.enviar_json(final_doc)
            if respuesta[0] != 500:
                msg = f"Documento enviado con EXITO\n\n{respuesta}"
                messagebox.showinfo(title="EXITO", message=msg)
                break

            else:
                e = respuesta[1]
                ans = messagebox.askokcancel("Error", f"No se pudo enviar el archivo:\n\n{e}\n\n¿Desea volver a intentarlo?")
                if ans == False: break

        self.leyendo = False
        self.finalizar_button.configure(state="disabled")

        # Registrar como procesado
        #self.referencias_procesadas.append(referencia)

        #BORRAR DOCUMENTOS PENDIENTES
        self.eliminar_docpdte_finalizar()

        # Limpiar y volver al selector de documentos
        self.mostrar_pantalla_principal_post_finalizar()
    def eliminar_docpdte_finalizar(self):
        nombre = str(self.documento_seleccionado['DOCTO_ENT_REFERENCIA'])+'P'
        nombre_lista = str(nombre)+'.json'
        if nombre_lista in self.doc_pendientes:
            self.doc_pendientes.remove(nombre_lista)

        os.remove(f'Pendientes\\{nombre}.json')
        if self.nombre_trabajo[-1] == 'P':
            msg = f"Documento Pendiente\n\n{nombre}\n\nFINALIZADO CON EXITO"
            messagebox.showinfo(title="AVISO", message=msg)
    def mostrar_pantalla_principal_post_finalizar(self):
        self.main_frame.pack_forget()
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.pzas = 0
        self.cont_lib = 0

        #self.mostrar_pantalla_principal()
        self.refresh_info()
    ##############
    #CUARTA OPCION - Pausa de trabajo
    def pausar_operacion(self):
        msg = "PAUSA DEL PROCESO\nEL DOCUMENTO SE GUARDARA PARA SU USO FUTURO\n\n¿DESEA PAUSAR EL PROCESO?"
        ans = messagebox.askyesno(title="PAUSA DEL PROCESO", message=msg)
        if ans == True:
            self.guardar_autonomo()
            self.regreso_general()

    ##############
    #Cuarta opcion independiente
    def ver_documento(self):
        def actualizar():
            obj_buscar = self.buscar.get()
            no_se_encontro = False
            for detalle in esperados:
                if str(detalle['PRODUCTO_SKU']) == str(obj_buscar) or str(detalle['DET_ENT_ETIQUETA']) == str(obj_buscar):
                    obj_buscar = f"{detalle['PRODUCTO_SKU']}       {detalle['DET_ENT_ETIQUETA']}        {detalle['DET_ENT_CANT_PED']}       {detalle['DET_ENT_CANT_CONF']}"
                    if self.mostrar == False:
                        self.scroll_frame.pack_forget()

                        self.search_label = ctk.CTkLabel(self.ver_doc_root, text=f"{obj_buscar}", font=("Arial", 16, "bold"))
                        self.search_label.pack(fill="both", expand=True)
                        self.mostrar = True
                    if self.mostrar == True:
                        self.search_label.configure(text=f"{obj_buscar}")
                    no_se_encontro = True
                    break
            if no_se_encontro == False:
                titulo = "Warning"
                msg = f"{obj_buscar} NO SE ENCUENTRA EN LA LISTA"
                messagebox.showwarning(title=titulo, message=msg)

        self.ver_doc_root = ctk.CTk()
        self.ver_doc_root.title("Proyecto Serial")
        self.ver_doc_root.geometry("600x400")
        self.ver_doc_root.resizable(False, False)

        totales_info = f"Total Libros: {self.pzas}       Total Escaneados: {self.cont_lib}"
        texto_doc = f"Pantalla Detalle\n\nLista SKUS Escaneados\n{totales_info}"
        self.pantalla_detalle = ctk.CTkLabel(self.ver_doc_root, text=texto_doc, font=("Arial", 16, "bold"))
        self.pantalla_detalle.pack(pady=5)


        documento = self.documento_seleccionado
        #print(documento)

        #########################
        #REVISION
        esperados = []
        #desconocidos = []
        for detalle in documento['DETALLES']:
            #print(detalle['PRODUCTO_SKU'])
            #    if int(detalle['PRODUCTO_SKU']) == 0: desconocidos.append(detalle)
            #    else: esperados.append(detalle)
            esperados.append(detalle)

        #################
        #BUSCADOR
        self.mostrar = False
        self.busc_frame = ctk.CTkFrame(self.ver_doc_root, width=200, height=5)
        self.busc_frame.pack(padx=10, pady=2)
        self.buscar = ctk.CTkEntry(self.busc_frame, placeholder_text="BUSCAR ETIQUETA")
        self.buscar.pack(side="left", pady=2)
        self.boton = ctk.CTkButton(self.busc_frame, text="Buscar", command=actualizar)
        self.boton.pack(side="right", pady=2)

        ########################
        #TITULOS DEL SCROLL
        tst ="SKU                          ETIQUETA                          TEORICO                          ESCANEADO"
        scrol_title = ctk.CTkLabel(self.ver_doc_root, text=tst)#, font=("Arial", 16, "bold"))
        scrol_title.pack(padx=10, pady=2, fill="both", expand=True)

        ########################
        #SECCION SCROLL
        self.scroll_frame = ctk.CTkScrollableFrame(self.ver_doc_root, width=480, height=75)
        self.scroll_frame.pack(padx=10, pady=2, fill="both", expand=True)

        for detalle in esperados:  # Cambiá por tu lista real
            show_frame = ctk.CTkFrame(self.scroll_frame, height=30, width=125, border_color="black", corner_radius=0)


            obj_sku = ctk.CTkLabel(show_frame, text=f"{detalle['PRODUCTO_SKU']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
            obj_sku.place(x=15, y=10)
            obj_eti = ctk.CTkLabel(show_frame, text=f"{detalle['DET_ENT_ETIQUETA']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
            obj_eti.place(x=135, y=10)
            obj_teoric = ctk.CTkLabel(show_frame, text=f"{detalle['DET_ENT_CANT_PED']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
            obj_teoric.place(x=267, y=10)
            obj_escan = ctk.CTkLabel(show_frame, text=f"{detalle['DET_ENT_CANT_CONF']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
            obj_escan.place(x=410, y=10)

            #obj_lab_sku = ctk.CTkLabel(obj_sku, text=f"HOLA MUNDO", height=20, width=115, font=("Arial", 12, "bold"))
            #obj_lab_sku.place(relx=0.5, rely=0.5, anchor="center")

            show_frame.pack(pady=5, fill="x", expand=True)

        ########################
        #SELECCION SCROLL SKUS EXTRAS
        #print(desconocidos)
        """
        if len(desconocidos) > 0:
            self.ver_doc_root.geometry("600x600")
            titulo_extra = ctk.CTkLabel(self.ver_doc_root, text=f"SKU EXTRAS\n\n{tst}")#, font=("Arial", 16, "bold"))
            titulo_extra.pack(padx=10, pady=10, fill="both", expand=True)

            ########################
            #SECCION SCROLL
            scroll2_frame = ctk.CTkScrollableFrame(self.ver_doc_root, width=480, height=75)
            scroll2_frame.pack(padx=10, pady=10, fill="both", expand=True)

            for detalle in desconocidos:  # Cambiá por tu lista real
                show_frame2 = ctk.CTkFrame(scroll2_frame, height=30, width=125, border_color="black", corner_radius=0)

                obj_sku = ctk.CTkLabel(show_frame2, text=f"{detalle['PRODUCTO_SKU']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
                obj_sku.place(x=15, y=10)
                obj_eti = ctk.CTkLabel(show_frame2, text=f"{detalle['DET_ENT_ETIQUETA']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
                obj_eti.place(x=135, y=10)
                obj_teoric = ctk.CTkLabel(show_frame2, text=f"{detalle['DET_ENT_CANT_PED']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
                obj_teoric.place(x=267, y=10)
                obj_escan = ctk.CTkLabel(show_frame2, text=f"{detalle['DET_ENT_CANT_CONF']}", height=30, width=125)#, border_width=1, border_color="black", corner_radius=0)
                obj_escan.place(x=410, y=10)

                #obj_lab_sku = ctk.CTkLabel(obj_sku, text=f"HOLA MUNDO", height=20, width=115, font=("Arial", 12, "bold"))
                #obj_lab_sku.place(relx=0.5, rely=0.5, anchor="center")

                show_frame2.pack(pady=5, fill="x", expand=True)
        """

        self.ver_doc_root.mainloop()


if __name__ == "__main__":
    app = App()
    app.mainloop()