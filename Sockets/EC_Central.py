import socket
import threading
import sys

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 6060
ADDR=(SERVER,PORT)
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 4

# Leer mapa de la ciudad y taxis
def leer_mapa(fichero_mapa):
    mapa = {}
    with open(fichero_mapa, 'r') as f:
        for linea in f:
            partes = linea.strip().split()
            mapa[partes[0]] = (int(partes[1]), int(partes[2]))
    return mapa
def handle_client(conn, addr):
    msg_length = int(conn.recv(HEADER).decode(FORMAT))
    msg = conn.recv(msg_length).decode(FORMAT)
    if msg == "3" or msg == "4" or msg == "5":
        print(f"El taxi con id {msg} está autentificado")
    else:
        print(f"Se ha intentado conectar el taxi con id {msg} pero no está en la bbdd")
        conn.send("Este taxi no está registrado".encode(FORMAT))
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


if(len(sys.argv)==4):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    start()
else:
    print("Los argumentos introducidos no son los correctos.El formato es:<IP gestor de colas> <puerto del broker del gestor de colas> <IP y puerto de la BBDD>")
