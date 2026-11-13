import serial
import time

while True:
    escribe = input("Escribe algo\n")
    # Configurar la conexión serie (ajusta 'COM3' y baudrate según tu dispositivo)
    try:
        ser = serial.Serial('COM6', 115200, timeout=0.1)
        #time.sleep(2) # Esperar a que se estabilice la conexión

        # Enviar datos (los datos deben ser bytes, usando b'...')
        mensaje = escribe
        ser.write(mensaje.encode('utf-8'))
        print(f"Enviado: {mensaje}")

        ser.close() # Cerrar el puerto
    except Exception as e:
        print(f"Error: {e}")
