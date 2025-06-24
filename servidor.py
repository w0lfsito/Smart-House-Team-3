import socket
import threading
import serial
import time
import json
arduino = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)

HOST = '10.1.141.29'
PORT = 5001
clientes = []

datos_sensores = {
    "Temperatura": 0.0,
    "Humedad": 0.0,
    "Distancia": 0.0,
    "Luz": 0.0
}

def leer_datos_arduino():
    while True:
        try:
            if arduino.in_waiting:
                linea = arduino.readline().decode('utf-8').strip()
                partes = linea.split(',')
                if len(partes) == 4:
                    datos_sensores["Temperatura"] = float(partes[0])
                    datos_sensores["Humedad"] = float(partes[1])
                    datos_sensores["Distancia"] = float(partes[2])
                    datos_sensores["Luz"] = float(partes[3])
        except Exception as e:
            print("Error al leer de Arduino:", e)
        time.sleep(1)

def manejar_cliente(conn, addr):
    print(f"[+] Cliente conectado desde {addr}")
    try:
        while True:
            mensaje = json.dumps(datos_sensores)
            conn.sendall(mensaje.encode('utf-8'))
            time.sleep(1)
    except:
        print(f"[-] Cliente desconectado: {addr}")
    finally:
        conn.close()
        clientes.remove(conn)

def aceptar_clientes(server_socket):
    while True:
        conn, addr = server_socket.accept()
        clientes.append(conn)
        threading.Thread(target=manejar_cliente, args=(conn, addr)).start()

def iniciar_servidor():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[✔] Servidor en {HOST}:{PORT}")
    threading.Thread(target=aceptar_clientes, args=(server_socket,), daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=leer_datos_arduino, daemon=True).start()
    iniciar_servidor()
    while True:
        time.sleep(1)
