import socket
import sys

HEADER = 64
PORT = 5050
FORMAT= 'utf-8'
FIN = "FIN"


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


if(len(sys.argv)==3):
    print("Están bien los argumentos")
    SERVER = sys.argv[1]
    PORT = sys.argv[2]
    ADDR = (SERVER,PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    msg ="jordi"
    while msg != FIN:
        msg=input()
        send(msg)
        

    


else:
    print("Los argumentos introducidos no son los correctos.El formato es: <IP> <Puerto del EC_DE>")

