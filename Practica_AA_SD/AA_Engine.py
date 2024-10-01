import socket 
import threading
import time
from datetime import datetime
from modulos.AA_Screen import *
from random import *
import os

VIVO = True
MUERTO = False
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FIN = "F"
MAX_CONEXIONES = 3
TIEMPO_RESTANTE=60
STRMAP=""
MAP_WIDTH=20
MAP_HEIGHT=20
MAP=[]
PLAYERS = []
STRPLAYERS=""


class Player:
    def __init__(self, name,level,ef,ec):
        self.name= name
        # El identificador del jugador será un autonumérico
        self.id = 3
        # Creo aleatoriamente la posicion del jugador
        self.cx=randint(0,MAP_WIDTH-1)
        self.cy=randint(0,MAP_HEIGHT-1)
        self.level=level
        self.ef=ef
        self.ec=ec
        self.status=VIVO
    
    def addlevel(self,qty):
        self.level += qty

    def print(self) :
        print("NOMBRE=", self.name, " LEVEL=", self.level, " CX=", self.cx," CY=",self.cy)
    
    
class Board:
    def __init__(self):
        Players=[]
        Mapa=""


def recibir (conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    msg_length = int(msg_length)
    msg = conn.recv(msg_length).decode(FORMAT)
    return msg


#### IMPLEMENTAR LA IMPRESION DE HORA CADA x SEGUNDOS
def handle_timer(time_delay):
    global TIEMPO_RESTANTE
    while True:
        #print("Hora actual:",datetime.now())
        time.sleep(time_delay)
        TIEMPO_RESTANTE-=2
        print(f"TIEMPO PARA EMPEZAR PARTIDA= {TIEMPO_RESTANTE} segundos")
        if TIEMPO_RESTANTE<0 :
            return 0

## Aplica el efecto que hay en la casilla del mapa destino 
def aplicar_efecto(pl,casilla):
    
    pl.print()
    print("CASILLA=\'", casilla,'\'')
    if casilla == '.':
        try:
            pl.addlevel(1)
        except:
            print("PUES MUERO EN EL LEVEL ESTE DE MARRAS")
            print(casilla)
    elif casilla == 'v':
        pl.level = 0
        pl.status = MUERTO
    pl.print()
    
'''
    elif casilla == BLANK:
        pass

    else: 
        # Si no es ninguno de los anteriores es porque hay otro jugador
        if pl.level > pl2.level
            pl2.level = 0
            pl2.estado = MUERTO        
'''

def procesar_movimiento(pl, tecla):
    global STRMAP
    global STRPLAYERS
    # Ponemos un espacio en el lugar donde estaba el jugador
    STRMAP=STRMAP[:(pl.cy*MAP_WIDTH+pl.cx)]+' '+STRMAP[(pl.cy*MAP_WIDTH+pl.cx)+1:]

    if tecla == 'W':
        # Movemos las coordenadas
        if pl.cy == 0:
            pl.cy=MAP_HEIGHT-1
        else :
            pl.cy-=1
    
    elif tecla == 'A':
        # Movemos las coordenadas
        if pl.cx == 0:
            pl.cx=MAP_WIDTH-1
        else :
            pl.cx-=1
        
    elif tecla == 'S':
        # Movemos las coordenadas
        if pl.cy == MAP_HEIGHT-1:
            pl.cy=0
        else :
            pl.cy+=1
        
    elif tecla == 'D':
        # Movemos las coordenadas
        if pl.cx == MAP_WIDTH-1:
            pl.cx=0
        else :
            pl.cx+=1
    
    # Comprobamos qué hay en la nueva posición
    aplicar_efecto(pl, STRMAP[(pl.cy*MAP_WIDTH+pl.cx)])

    # Pintamos el jugador en la nueva posición
    STRMAP=STRMAP[:(pl.cy*MAP_WIDTH+pl.cx)]+pl.name[0]+STRMAP[(pl.cy*MAP_WIDTH+pl.cx)+1:]  
    #print(STRMAP)
    
    # Actualizamos la cadena STRPLAYERS
    STRPLAYERS=""
    for i in range(len(PLAYERS)):
        strnametmp= PLAYERS[i].split('#')[0]
        if strnametmp==pl.name :
            PLAYERS[i]=pl.name+'# LEVEL= '+str(pl.level)+' # '+str(pl.ef)+' # '+str(pl.ec)+' # CX='+str(pl.cx)+' # CY='+str(pl.cy)+'\n'
        STRPLAYERS+=PLAYERS[i]
        
    
    
    

##### Tratamiento del hilo jugador ######################

def handle_client(conn, addr):
    global STRMAP
    global PLAYERS
    global STRPLAYERS
    global MAP_HEIGHT, MAP_WIDTH

    print(f"[NUEVA CONEXION] {addr} connected.")
    
    connected = True
    #conn.settimeout(10)
    
    # RECIBIR LOS DATOS DEL JUGADOR ###
    msg = recibir(conn)

    # Creo el objeto jugador y lo añado a la lista de jugadores y a la clase jugador
    playerList = msg.split('#')
    print(playerList)
    
    pl= Player( playerList[0],playerList[1],playerList[2],playerList[3])
    
    # Concateno las coordenadas donde aparece aleatoriamente el jugador
    msg+='# CX= '+str(pl.cx)+"# CY= "+str(pl.cy)+'\n'
    PLAYERS.append(msg)
    print(PLAYERS)
    STRPLAYERS+=msg

    #Posiciono al jugador en el mapa y los envio al AA_PLAYER
    STRMAP=STRMAP[:(pl.cy*MAP_WIDTH+pl.cx)]+pl.name[0]+STRMAP[(pl.cy*MAP_WIDTH+pl.cx)+1:]
    print_map(MAP_HEIGHT,MAP_WIDTH,PLAYERS, STRMAP)
    print(f"DATOS DEL JUGADOR: {msg}")
    print(PLAYERS)
    conn.send(STRPLAYERS.encode(FORMAT))
    conn.send(STRMAP.encode(FORMAT))

    ### RECIBIR MOVIMIENTOS ###       
    while connected:
        try:
            movimiento = recibir(conn)
            print(f" He recibido del cliente [{addr}] el mensaje: {movimiento}")
            procesar_movimiento(pl,movimiento)
            #print(STRPLAYERS)
            #print(STRMAP)
            conn.send(STRPLAYERS.encode(FORMAT))
            conn.send(STRMAP.encode(FORMAT))
            if movimiento == FIN:
                connected = False
        except:
            print("Parece que no me quieres decir nada")
            print(STRPLAYERS)
            print(STRMAP)
            connected= False
    print("ADIOS. TE ESPERO EN OTRA OCASION")
    conn.close()
    
        
def start():
    global STRMAP
    global PLAYERS
    # Creo el mapa
    MAP, STRMAP = create_map(MAP_HEIGHT,MAP_WIDTH)
    os.system("cls")
    print_map(MAP_HEIGHT,MAP_WIDTH,PLAYERS,STRMAP)
 
    #Pongo a la escucha el servidor
    server.listen()
    print(f"ESPERANDO JUGADORES: Servidor a la escucha en {SERVER}")
    CONEX_ACTIVAS = threading.active_count()-1
    
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        print(f"[CONEXIONES ACTIVAS] {CONEX_ACTIVAS}")
        print("CONEXIONES RESTANTES PARA CERRAR EL SERVICIO", MAX_CONEXIONES-CONEX_ACTIVAS)

        if (CONEX_ACTIVAS <= MAX_CONEXIONES and TIEMPO_RESTANTE >= 0 ): 
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        else:
            print("Ya estamos todos. A JUGARRRRRRR")
            print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
            conn.send("OOppsss... DEMASIADAS CONEXIONES. Tendrás que esperar a que alguien se vaya".encode(FORMAT))
            conn.close()
            CONEX_ACTUALES = threading.active_count()-1
        

######################### MAIN ##########################

# Solo para implementar la impresión de la hora
'''
thread = threading.Thread(target=handle_timer, args=(2,))
thread.start()
'''

# Genero el servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Arranco el proceso de esperar jugadores
start()
    

#################### FIN ####################################
