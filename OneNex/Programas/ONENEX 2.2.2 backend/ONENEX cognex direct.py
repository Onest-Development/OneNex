import serial
import threading

control = serial.Serial(port='COM6', baudrate=115200, timeout=1)
com_cognex = serial.Serial(port='COM12', baudrate=115200, timeout=0.01)

info = None
pass_cont = 0
code_cont = 0
# Función para enviar datos
def enviar():
    global s
    while True:
        mensaje = input("Escribe mensaje\n")
        control.write(("ARRANQUE").encode('utf-8'))

# Función para recibir datos
def recibir():
    global info, pass_cont, code_cont

    while True:
        if com_cognex.in_waiting > 0:
            data = com_cognex.readline().decode('utf-8').strip()
            info = data

            if info == "PASS":
                pass_cont += 1
                print(pass_cont)
                if pass_cont >= 2 and code_cont == 0:
                    control.write("PARO".encode('utf-8'))
                    pass_cont = 0
            else:
                code_cont += 1
                if code_cont <= 2:
                    code_cont = 0
                    print(f"Recibido: {info}")
                    pass_cont = 0





# Crear hilos para trabajar en paralelo
hilo_envio = threading.Thread(target=enviar)
hilo_recepcion = threading.Thread(target=recibir)

hilo_envio.start()
hilo_recepcion.start()



