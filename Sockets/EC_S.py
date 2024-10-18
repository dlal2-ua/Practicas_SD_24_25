import socket
import sys
import time
import threading
import select


HEADER = 64
FORMAT= 'utf-8'
FIN = "FIN"
MSG = "OK"


def sendmsg(client):
    while True:
        client.sendall(MSG.encode('utf-8'))
        time.sleep(1)
        

if(len(sys.argv)==3):
    print("Están bien los argumentos")
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

else:
    print("Los argumentos introducidos no son los correctos.El formato es: <IP> <Puerto del EC_DE>")

