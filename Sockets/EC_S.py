import socket
import sys

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


if(len(sys.argv)==3):
    print("Están bien los argumentos")
    SERVER = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (SERVER,PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    aux=input()
    while aux != FIN:
        msg="KO"
        print("Envío al servidor: ",msg)
        send(msg)
        aux=input()
        if aux == FIN:
            msg = FIN
            print("Envío al servidor: ",msg)
            send(msg)
            break
        msg="OK"
        print("Envío al servidor: ",msg)
        send(msg)
        aux=input()
        if aux == FIN:
            msg = FIN
            print("Envío al servidor: ",msg)
            send(msg)
    client.close()
else:
    print("Los argumentos introducidos no son los correctos.El formato es: <IP> <Puerto del EC_DE>")

