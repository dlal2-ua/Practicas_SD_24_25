import socket 
import threading
import time
import sys

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'


def handle_server():
    contador = 0
    while True:
        try:                
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR_CLIENT)
            msg = sys.argv[5]
            message = msg.encode(FORMAT)
            client.sendall(message)
            break
        except ConnectionRefusedError:
                if contador == 0:
                    print("La central no está conectada. Esperando a que se conecte...")
                contador += 1
                time.sleep(1)
    respuesta = client.recv(2048).decode(FORMAT)
    print(respuesta)


def start():
    global PORT
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR=(SERVER,PORT)
    server.bind(ADDR)
    print(f"Puerto en el que está escuchando: {PORT}")
    server.listen()

    while True:
        try:
            conn, addr = server.accept()
            handle_server()
            msg = conn.recv(1024).decode('utf-8')
            while msg:
                msg = conn.recv(1024).decode('utf-8')
                print(msg)
            conn.close()
        except ConnectionResetError:
            print("El sensor se ha perdido, esperando a que se conecte otro...")


#Función servidor con el sensor
def servidor():
    global PORT
    while True:
        try:
            start()
        except OSError:
            PORT += 1


#MAIN



if (len(sys.argv)==6):
    SERVER_CLIENT = sys.argv[1]
    PORT_CLIENT = int(sys.argv[2])
    ADDR_CLIENT = (SERVER_CLIENT,PORT_CLIENT)
    hilo_servidor = threading.Thread(target= servidor)
    hilo_servidor.start()

else:
    print("Los argumentos son:<Ip del EC_Central><Puerto del EC_Central><Ip del broker><Puerto del broker><ID del taxi>")