import socket
import sys
import time
import threading


HEADER = 64
FORMAT= 'utf-8'
FIN = "FIN"
MSG = "OK"


def sendmsg(client):
    try:
        while True:
            client.sendall(MSG.encode('utf-8'))
            time.sleep(1)
    except ConnectionAbortedError:
        print(f"Se ha perdido la conexion con el DE con puerto {sys.argv[2]}. Voy a morir")
        client.close()
        raise SystemExit(1)
if(len(sys.argv)==3):
    try:
        SERVER = sys.argv[1]
        PORT = int(sys.argv[2])
        ADDR = (SERVER,PORT)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        threading.Thread(target=sendmsg, args=(client,), daemon=True).start()
        while True:
            user_input = input()
            MSG = "KO"
            user_input = input()
            MSG = "OK"
    #Si el puerto que se ha puesto no lo tiene ningún DE
    except ConnectionRefusedError:
        print("Este puerto no pertenece a ningún DE. Prueba con el siguiente")
else:
    print("Los argumentos introducidos no son los correctos.El formato es: <IP> <Puerto del EC_DE>")

