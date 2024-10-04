import socket 
import threading
import time
import sys

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR=(SERVER,PORT)
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 1

def handle_client(conn, addr):
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            while msg != FIN:
                print(msg)
                time.sleep(1)
            connected = False
    conn.close()

def start():
    server.listen()
    CONEX_ACTIVAS = threading.active_count()-1
    print(CONEX_ACTIVAS)
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        if (CONEX_ACTIVAS <= MAX_CONEXIONES): 
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONEXIONES ACTIVAS] {CONEX_ACTIVAS}")
            print("CONEXIONES RESTANTES PARA CERRAR EL SERVICIO", MAX_CONEXIONES-CONEX_ACTIVAS)
        else:
            print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
            conn.send("OOppsss... DEMASIADAS CONEXIONES. Tendrás que esperar a que alguien se vaya".encode(FORMAT))
            conn.close()
            CONEX_ACTUALES = threading.active_count()-1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

start()

#if (len(sys.argv)==6):
#    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    ADDR=(SERVER,PORT)
#    server.bind(ADDR)
#    start()
#else:
#    print("Los argumentos son:<Ip del EC_Central><Puerto del EC_Central><Ip del broker><Puerto del broker>><ID del taxi>")