import requests, json, openpyxl, os, webbrowser
import serial.tools.list_ports
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.drawing.image import Image
from win32com import client


def serial_ports():
    ports = serial.tools.list_ports.comports()
    sp = []
    for port in ports:
        name_port = port.device
        sp.append(str(name_port))

    #if len(sp) == 1: return sp
    if len(sp) >= 1: return sp
    else: return []

def obtener_devoluciones():
    #url = "http://10.249.249.3/ords34/ords/tstapex/Planeta-qa/getDev"

    #url = "http://10.249.249.3/ords34/ords/wms_planeta/planeta_qa/getListaDevoluciones"
    url = "http://10.249.249.3/ordspla/wms_planeta/conveyor/getListaDevoluciones"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        #print(data)
        return data
        #return [f"{item['REFERENCIA']} - {item['CLIENTE']}" for item in data.get("LISTA_PEDIDOS", [])]
    except Exception as e:
        #print("Error al obtener devoluciones:", e)
        with open("documentos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

def enviar_json(payload):
    #url = "http://10.249.249.3/ords34/ords/wms_planeta/planeta_qa/recibe_oc"
    #url = "http://10.249.249.3/ords34/ords/wms_planeta/planeta_qa/getListaDevoluciones"
    url = "http://10.249.249.3/ordspla/wms_planeta/conveyor/recibe_oc"
    #url = "http://10.249.249.3/ords34/ords/wms_planeta/planeta_qa/recibe_oc2"
    try:
        """
        data = {
            "REFERENCIA": payload["pedido"],
            "LISTA": [
                {"PRODUCTO_SKU": item["sku"], "CANTIDAD": item["cantidad"]}
                for item in payload["detalle"]
            ]
        }
        """
        data = payload
        response = requests.post(url, json=data, timeout=5)
        #response.raise_for_status()
        #r_json = response.json()
        #estado = r_json.get("Estado", 500)
        #mensaje = r_json.get("Mensaje", "Respuesta inesperada.")
        #print("RESPUESTA")
        #print(response.text)
        #print("----------------")
        #print(response)
        #print("----------------")
        return (200, response) #estado, mensaje
    except Exception as e:
        #print("no envio")
        return 500, f"Error de conexión: {e}"

def formato_impreso(doc, no_listados, date, ruta, nombre, nss):
    #file = open('documentos.json', 'r', encoding='utf-8')
    #datos = json.load(file)
    #doc = datos[0]
    #no_listados=datos[1]["DETALLES"]

    objs = doc["DETALLES"]
    esperados = 0
    escaneados = 0
    for obj in objs:
        cant = obj["DET_ENT_CANT_PED"]
        scans = obj["DET_ENT_CANT_CONF"]
        esperados += int(cant)
        escaneados += int(scans)

    wb = openpyxl.Workbook()
    ws = wb.active

    one_format = Font(size=12, bold=True)

    ######################
    #Formato general de hoja
    def encabezado(r):
        imagen_path = 'media/onestlogo.png'
        img = Image(imagen_path)
        # 4. Establece la celda donde quieres anclar la imagen
        img.anchor = f'A{r}' #se puede usar para colocar la imagen a partir de la celda A2
        # 5. Agrega la imagen a la hoja de trabajo
        ws.add_image(img, f"A{r}")

        #ws.cell(row=r+1, column=7).value = "FECHA"
        #ws.cell(row=r+1, column=7).font = one_format
        #ws.cell(row=r+1, column=8).value = f"{date}".replace("-", "/")
        #ws.cell(row=r+1, column=8).font = one_format

        ws.cell(row=r+1, column=6).value = f"Hecho por: {nss}"
        ws.cell(row=r+1, column=6).font = one_format

        ws.merge_cells(start_row=r+3, start_column=1, end_row=r+3, end_column=5)
        ws.cell(row=r+3, column=1).value = f"Concentrado: {doc["DOCTO_ENT_ID"]}"
        ws.cell(row=r+3, column=1).font = one_format

        ws.cell(row=r+3, column=7).value = f"{doc["DOCTO_ENT_REFERENCIA"]}"
        ws.cell(row=r+3, column=7).font = one_format
    def resumen():
        r = 6
        #RESUMEN
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        ws.cell(row=r, column=3).value = "RESUMEN"
        ws.cell(row=r, column=3).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=r, column=3).font = one_format

        #TOTAL LIBROS
        ws.merge_cells(start_row=r+1, start_column=2, end_row=r+1, end_column=3)
        ws.cell(row=r+1, column=2).value = "TOTAL LIBROS"
        ws.cell(row=r+1, column=2).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=r+1, column=2).font = one_format
        #NO: LIBROS
        ws.cell(row=r+1, column=4).value = f"{esperados}"
        ws.cell(row=r+1, column=4).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=r+1, column=4).font = one_format

        #TOTAL ESCANEADOS
        ws.merge_cells(start_row=r+1, start_column=6, end_row=r+1, end_column=7)
        ws.cell(row=r+1, column=6).value = "TOTAL"
        ws.cell(row=r+1, column=6).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=r+1, column=6).font = one_format
        #NO: ESCANEADOS
        ws.cell(row=r+1, column=8).value = f"{escaneados}"
        ws.cell(row=r+1, column=8).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=r+1, column=8).font = one_format
    def titulos(r):
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        ws.cell(row=r, column=2).value = "LISTA SKUS"
        ws.cell(row=r, column=2).font = one_format
        ws.cell(row=r, column=2).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=1, end_row=r+1, end_column=2)
        ws.cell(row=r+1, column=1).value = "SKU"
        ws.cell(row=r+1, column=1).font = one_format
        ws.cell(row=r+1, column=1).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=3, end_row=r+1, end_column=5)
        ws.cell(row=r+1, column=3).value = "ETIQUETA"
        ws.cell(row=r+1, column=3).font = one_format
        ws.cell(row=r+1, column=3).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=6, end_row=r+1, end_column=7)
        ws.cell(row=r+1, column=6).value = "TEORICO"
        ws.cell(row=r+1, column=6).font = one_format
        ws.cell(row=r+1, column=6).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=8, end_row=r+1, end_column=9)
        ws.cell(row=r+1, column=8).value = "ESCANEADO"
        ws.cell(row=r+1, column=8).font = one_format
        ws.cell(row=r+1, column=8).alignment = Alignment(horizontal='center', vertical='center')
    def escribir(r, sku, etiqueta, teorico, escaneado):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.cell(row=r, column=1).value = sku
        ws.cell(row=r, column=1).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        ws.cell(row=r, column=3).value = etiqueta
        ws.cell(row=r, column=3).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=7)
        ws.cell(row=r, column=6).value = teorico
        ws.cell(row=r, column=6).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r, start_column=8, end_row=r, end_column=9)
        ws.cell(row=r, column=8).value = escaneado
        ws.cell(row=r, column=8).alignment = Alignment(horizontal='center', vertical='center')
    def extras(r):
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        ws.cell(row=r, column=2).value = "SKUS EXTRAS"
        ws.cell(row=r, column=2).font = one_format
        ws.cell(row=r, column=2).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=1, end_row=r+1, end_column=2)
        ws.cell(row=r+1, column=1).value = "SKU"
        ws.cell(row=r+1, column=1).font = one_format
        ws.cell(row=r+1, column=1).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=3, end_row=r+1, end_column=5)
        ws.cell(row=r+1, column=3).value = "ETIQUETA"
        ws.cell(row=r+1, column=3).font = one_format
        ws.cell(row=r+1, column=3).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=6, end_row=r+1, end_column=7)
        ws.cell(row=r+1, column=6).value = "TEORICO"
        ws.cell(row=r+1, column=6).font = one_format
        ws.cell(row=r+1, column=6).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r+1, start_column=8, end_row=r+1, end_column=9)
        ws.cell(row=r+1, column=8).value = "ESCANEADO"
        ws.cell(row=r+1, column=8).font = one_format
        ws.cell(row=r+1, column=8).alignment = Alignment(horizontal='center', vertical='center')

    def pie_paj(r):
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        ws.cell(row=r, column=2).value = "ENTREGA"
        ws.cell(row=r, column=2).font = one_format
        ws.cell(row=r, column=2).alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
        ws.cell(row=r, column=6).value = "RECIBE"
        ws.cell(row=r, column=6).font = one_format
        ws.cell(row=r, column=6).alignment = Alignment(horizontal='center', vertical='center')

        linea_firma = Border(bottom=Side(style='thin'))
        ws.cell(row=r+2, column=2).border = linea_firma
        ws.cell(row=r+2, column=3).border = linea_firma
        ws.cell(row=r+2, column=4).border = linea_firma

        ws.cell(row=r+2, column=6).border = linea_firma
        ws.cell(row=r+2, column=7).border = linea_firma
        ws.cell(row=r+2, column=8).border = linea_firma

    r_title = 1
    r_list = 10
    r_obj = 11

    hojas = []
    end_hojas = []
    for h in range(1, 20):
        hojas.append((47*h)-3)
        end_hojas.append(47*h)


    encabezado(r_title)
    resumen()
    titulos(r_list)

    #print(len(objs))
    #print(hojas)
    #print(end_hojas)
    finalizo = 0

    for i in range(1, len(objs)+1):
        sku = objs[i-1]["PRODUCTO_SKU"]
        etiqueta = objs[i-1]["DET_ENT_ETIQUETA"]
        teorico = objs[i-1]["DET_ENT_CANT_PED"]
        escaneado = objs[i-1]["DET_ENT_CANT_CONF"]

        rob = r_obj+i
        finalizo = rob

        if rob in hojas:
            r_title += 47
            encabezado(r_title)

            r_obj+=10
            #titulos(r_obj)

        escribir(rob, sku, etiqueta, teorico, escaneado)

    #PIE DE HOJA
    ant = 1
    act = 47
    for h in range(0, len(end_hojas)):
        if h != 0:
            ant = end_hojas[h-1]+1
            act = end_hojas[h]

        #print(finalizo, ant, act)
        if finalizo > ant and finalizo <= act-3:
            r = act-3
            #print(r)
            pie_paj(r=r)
            break


    wb.save(f"{ruta}\\formato1.xlsx")
    wb.close()

    xlsx2pdf(ruta, nombre)

def xlsx2pdf(ruta, nombre):

    excel_file_path = f"{ruta}\\formato1.xlsx"
    pdf_file_path = f"{ruta}\\{nombre}.pdf"

    excel = client.Dispatch("Excel.Application")
    sheets = excel.Workbooks.Open(os.path.abspath(excel_file_path))
    work_sheets = sheets.Worksheets[0] # Select the first worksheet

    # Export as PDF (0 for PDF format)
    work_sheets.ExportAsFixedFormat(0, os.path.abspath(pdf_file_path))

    sheets.Close(SaveChanges=False) # Close the workbook without saving changes
    excel.Quit()

    os.remove(f"{ruta}\\formato1.xlsx")

    webbrowser.open(f"{ruta}\\{nombre}.pdf")
