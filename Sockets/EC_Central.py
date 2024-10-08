import socket
import sys

if(len(sys.argv)==4):
    print("Están bien los argumentos")
    # Leer mapa de la ciudad y taxis
    def leer_mapa(fichero_mapa):
        mapa = {}
        with open(fichero_mapa, 'r') as f:
            for linea in f:
                partes = linea.strip().split()
                mapa[partes[0]] = (int(partes[1]), int(partes[2]))
        return mapa

    




    
else:
    print("Los argumentos introducidos no son los correctos.El formato es: <Puerto de escucha> <IP y puerto del broker del gestor de colas> <IP y puerto de la BBDD>")
