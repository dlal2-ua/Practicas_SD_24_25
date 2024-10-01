import socket
import sys
import os
import time
import msvcrt 
from modulos.AA_Screen import *


HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
FIN = "F"

class Player:
    def __init__(self, name, cx,cy,level,ef,ec):
        self.name= name
        self.cx=cx
        self.cy=cy
        self.level=level
        self.ef=ef
        self.ec=ec

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    
    
#################################### MAIN #############################


if  (len(sys.argv) == 7):
    SERVER = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (SERVER, PORT)
    STRPLAYER=""
    PLAYERS=[]
    timeout = 1


    player = Player (sys.argv[3],1,1,sys.argv[4],sys.argv[5],sys.argv[6])
    playerStr = player.name + "#" + str(player.level) + "#" + str(player.ef) +"#" + str(player.ec)
       
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    
    print (f"Establecida conexión en [{ADDR}]")

    #### Enviando los datos del Jugador ####
    try:
        send(playerStr)
        STRPLAYER = client.recv(4096).decode(FORMAT)   
        STRMAPA = client.recv(4096).decode(FORMAT)      
        PLAYERS = STRPLAYER.split('\n')   
        print_map(20,20,PLAYERS,STRMAPA)
        
    except:
        print("NADIE ME QUIERE: No puedo enviar los datos del jugador. La conexión se cerró. Hasta otra")
        client.close()


    #### Enviando Teclas de movimiento ###
    msg=""
    
    try:
        while msg != FIN :
            
            #Espera a que se pulse una tecla o a que pase el timeout especificado
            startTime = time.time()

            while True:
                msg=""
                if msvcrt.kbhit():
                    msg = msvcrt.getch().decode(FORMAT)
                    break
                
                elif time.time() - startTime > timeout :
                    break
                
 
            #Vacia el buffer de teclas repetidas
            while msvcrt.kbhit():
                msvcrt.getch()

            send(msg)
            STRPLAYER = client.recv(4096).decode(FORMAT)
            STRMAPA = client.recv(4096).decode(FORMAT)  
            os.system("cls")
            #print(STRPLAYER)
            #print(STRMAPA)
            PLAYERS=STRPLAYER.split('\n')
            #print(PLAYERS)
            print_map(20,20,PLAYERS,STRMAPA)
            
        print ("SE ACABO LO QUE SE DABA")
        print("Envio al servidor: ", FIN)
        send(FIN)
        client.close()
    except:
        print("NADIE ME QUIERE: La conexión se cerró. Debo haber muerto. Hasta otra")
        print(STRPLAYER)
        print(PLAYERS)
        client.close()
        
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <ServerIP> <Puerto> <Nombre Jugador> <Nivel> <Ef> <Ec>")
