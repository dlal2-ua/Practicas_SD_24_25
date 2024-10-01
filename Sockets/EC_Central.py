import socket
import sys



if(len(sys.argv)==4):
    print("Están bien los argumentos")
else:
    print("Los argumentos introducidos no son los correctos.El formato es: <Puerto de escucha> <IP y puerto del broker del gestor de colas> <IP y puerto de la BBDD>")
