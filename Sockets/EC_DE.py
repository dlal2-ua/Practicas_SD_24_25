import socket 
import threading
import time
import sys

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'
FIN = "FIN"


def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR=(SERVER,PORT)
    server.bind(ADDR)
    print(f"Puerto en el que está escuchando: {PORT}")
    server.listen()

    while True:
        try:
            conn, addr = server.accept()
            msg = conn.recv(1024).decode('utf-8')
            while msg:
                msg = conn.recv(1024).decode('utf-8')
                print(msg)
            conn.close()
        except ConnectionResetError:
            print("El sensor se ha perdido, esperando a que se conecte otro...")
        


        
"""def handle_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR_CLIENT)
    msg = sys.argv[3]
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    respuesta = client.recv(4096)
    print(respuesta.decode('utf-8'))"""

#Función cliente con la central
"""SERVER_CLIENT = sys.argv[1]
PORT_CLIENT = int(sys.argv[2])
ADDR_CLIENT = (SERVER_CLIENT,PORT_CLIENT)"""


#Función servidor con el sensor
while True:
    try:
        start()
    except OSError:
        PORT += 1





#if (len(sys.argv)==6):
#    
#else:
#    print("Los argumentos son:<Ip del EC_Central><Puerto del EC_Central><Ip del broker><Puerto del broker>><ID del taxi>")