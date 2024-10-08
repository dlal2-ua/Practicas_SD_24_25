import socket
import sys
import time
import threading
import select

HEADER = 64
FORMAT= 'utf-8'
FIN = "FIN"


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
def sendmsg(msg):
    while True:
        send(msg)
        time.sleep(1)

if(len(sys.argv)==3):
    print("Están bien los argumentos")
    SERVER = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (SERVER,PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    msg = "OK"
    t1 = threading.Thread(target=sendmsg(msg))
    t1.deamon = True
    aux=input()
    t1.start()
    if select.select([sys.stdin],[],[],0.1)[0]:
        aux=input()

else:
    print("Los argumentos introducidos no son los correctos.El formato es: <IP> <Puerto del EC_DE>")

