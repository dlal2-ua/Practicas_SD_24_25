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


def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    while True:
        conn, addr = server.accept()
        msg_length = int(conn.recv(HEADER).decode(FORMAT))
        msg = conn.recv(msg_length).decode(FORMAT)
        print(msg)
        while msg != FIN:
            msg_length = int(conn.recv(HEADER).decode(FORMAT))
            msg = conn.recv(msg_length).decode(FORMAT)
            print(msg)
        print("Sale del while")
        conn.close()
        exit(1)
        
def handle_server():
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
    print(respuesta.decode('utf-8'))

#Función cliente con la central
SERVER_CLIENT = sys.argv[1]
PORT_CLIENT = int(sys.argv[2])
ADDR_CLIENT = (SERVER_CLIENT,PORT_CLIENT)

t1= threading.Thread(target=handle_server)
t1.start()




#Función servidor con el sensor
t2= threading.Thread(target=start)
t2.start()


#if (len(sys.argv)==6):
#    
#else:
#    print("Los argumentos son:<Ip del EC_Central><Puerto del EC_Central><Ip del broker><Puerto del broker>><ID del taxi>")