import socket 
import threading
import time
import sys
from kafka import KafkaConsumer, KafkaProducer
from funciones_generales import *
import os
import requests

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'
parar_hilo_enviar_coord = False



def enviar_central(id_taxi,broker,pasajero):
    global parar_hilo_enviar_coord
    global msg_sensor
    global Central_para
    global X_taxi
    global Y_taxi
    global destinoX
    global destinoY
    producercliente = KafkaProducer(
        bootstrap_servers=broker,
    )
    producer = KafkaProducer(
        bootstrap_servers=broker,
    )

    # Una vez que ha llegado, puedes manejar la lógica adicional aquí (ej: recoger el pasajero)
    #print(f"Antes de entrar al bucle: {X_taxi} , {Y_taxi}")
    # Iniciar el movimiento del taxi

    try:
        if X_taxi == destinoX and Y_taxi == destinoY:
            print(f"Taxi {id_taxi} ha llegado al destino y ha recogido al pasajero {pasajero}.")
            coordenada = str(id_taxi) + "," + str(X_taxi) + "," + str(Y_taxi) + "," + str(msg_sensor)+ ",nada"
            producer.send('TAXIS', value=coordenada.encode('utf-8'))
            mensaje_cliente = f"ID:{pasajero} OK"
            producercliente.send('TAXI-CLIENTE',value=mensaje_cliente.encode('utf-8'))
            time.sleep(1)

            # Actualizar el mapa cada vez que se envían coordenadas
            dibujar_mapa()
        else:
            while (X_taxi != destinoX or Y_taxi != destinoY) and parar_hilo_enviar_coord==False and Central_para ==False:
                #print(f"En el bucle: {X_taxi} , {Y_taxi}")
                if msg_sensor == "OK":
                    if destinoX > X_taxi:
                        X_taxi += 1
                    else: 
                        X_taxi -= 1
                    coordenada = str(id_taxi) + "," + str(X_taxi) + "," + str(Y_taxi) + "," + str(msg_sensor)+ ",nada"
                    producer.send('TAXIS', value=coordenada.encode('utf-8'))
                    time.sleep(1)
                    # Actualizar el mapa cada vez que se envían coordenadas
                    dibujar_mapa()

                    while Y_taxi != destinoY and parar_hilo_enviar_coord == False and Central_para == False:
                        #print(f"En el bucle: {X_taxi} , {Y_taxi}")
                        if msg_sensor == "OK":
                            if destinoY > Y_taxi:
                                Y_taxi += 1
                            else: 
                                Y_taxi -= 1
                            coordenada = str(id_taxi) + "," + str(X_taxi) + "," + str(Y_taxi) + "," + str(msg_sensor)+ ",nada"
                            producer.send('TAXIS', value=coordenada.encode('utf-8'))
                            time.sleep(1)
                            # Actualizar el mapa cada vez que se envían coordenadas
                            dibujar_mapa()

                        else:
                            coordenada = str(id_taxi) + "," + str(X_taxi) + "," + str(Y_taxi) + "," + str(msg_sensor)+ ",nada"
                            producer.send('TAXIS', value=coordenada.encode('utf-8'))
                            time.sleep(1)
                            # Actualizar el mapa cada vez que se envían coordenadas
                            dibujar_mapa()

                else:
                    coordenada = str(id_taxi) + "," + str(X_taxi) + "," + str(Y_taxi) + "," + str(msg_sensor) + ",nada"
                    producer.send('TAXIS', value=coordenada.encode('utf-8'))
                    time.sleep(1)
                    # Actualizar el mapa cada vez que se envían coordenadas
                    dibujar_mapa()

    except KeyboardInterrupt:
        print("sale enviar central")
        exit(1)
    producer.close()

def recibir_central(broker):
    global Central_para
    global X_taxi
    global Y_taxi
    global destinoY
    global destinoX
    topicos = ['CENTRAL-TAXI','CENTRAL-CAIDA']
    consumer= KafkaConsumer(*topicos, bootstrap_servers=broker)
    producer = KafkaProducer(
        bootstrap_servers=broker,
    )
    try:
        Central_para = False
        for message in consumer:
            # Decodificar el mensaje recibido del taxi
            mensaje = message.value.decode('utf-8')
            id_taxi = sys.argv[5]
            partes = mensaje.split(",")
            if(partes == "Central caida"):
                print("La central se ha caido. Terminando la última orden que recibió de central")
            else:
                taxi = int(partes[0])
                central = partes[6]
                if int(id_taxi) == taxi:
                    #print(mensaje)
                    if central == "Parar":
                        Central_para = True
                        coordenada = str(id_taxi) + "," + str(X_taxi) + "," + str(Y_taxi) + "," + str(msg_sensor) + ",parado"
                        producer.send('TAXIS', value=coordenada.encode('utf-8'))
                        time.sleep(1)
                    elif central== "Seguir":
                        Central_para = False
                        coordenada = str(id_taxi) + "," + str(X_taxi) + "," + str(Y_taxi) + "," + str(msg_sensor) + ",sigue"
                        producer.send('TAXIS', value=coordenada.encode('utf-8'))
                        time.sleep(1)
                    else:
                        destinoX = int(partes[1])
                        destinoY = int(partes[2])
                        pasajero = partes[3]
                        X_taxi = int(partes[4])
                        Y_taxi = int(partes[5])
                        if central == "cambiadocon":
                            print(f"Se ha cambiado el destino del cliente al destino: {destinoX},{destinoY}")
                        if central == "cambiadosin":
                            print(f"El cliente {pasajero}, tendrá que esperar un momento a que el taxi vaya a por el")
                    hilo_enviar_a_central = threading.Thread(target=enviar_central, args=(id_taxi,broker,pasajero,))
                    hilo_enviar_a_central.start()
    except ValueError:
        print("La central se ha caido. Terminando la última orden que recibió de central")



def enviar_coord(broker,):

    hilo_recibir_central = threading.Thread(target=recibir_central,args=(broker,))
    hilo_recibir_central.start()
    hilo_recibir_central.join()

    
        

        

#Función cliente con la central
def handle_server():
    try:
        global autentificado
        autentificado = False
        contador = 0
        idTaxi = sys.argv[5]
        while True:
            try:     
                r = ""    
                while r != "1" and r != "2" and r != "3":
                    print("--------------------Menu-------------------")
                    print("1. Registrar el taxi")
                    print("2. Dar de baja el taxi")
                    print("3. Comenzar recorrido")
                    r = input()
                if r == "3":
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect(ADDR_CLIENT)
                    message = idTaxi.encode(FORMAT)
                    client.sendall(message)
                elif r =="1":
                    url = 'https://localhost:3000/taxis'
                    data = {'id': idTaxi}

                    try:
                        response = requests.post(url, json=data)
                        response.raise_for_status()  # Lanza una excepción si ocurre un error HTTP
                        print('Código de respuesta:', response.status_code)
                        print('Respuesta del servidor:', response.json())
                    except requests.exceptions.RequestException as error:
                        print('Error:', error)
                elif r== "2":
                    print("Dar de baja")
                break
            except ConnectionRefusedError:
                    if contador == 0:
                        print("La central no está conectada. Esperando a que se conecte...")
                    contador += 1
                    time.sleep(1)
        respuesta = client.recv(2048).decode(FORMAT)
        print(respuesta)
        if(respuesta == "Taxi correctamente autentificado"):
            autentificado = True
    except ConnectionAbortedError:
        print("Se ha perdido la conexion con la central")
#Función para que el puerto aumente automáticamente cuando se ejecuta mas de 1 DE
def servidor(broker):
    try:
        global PORT
        while True:
            try:
                start(broker)
            except OSError:
                PORT += 1
    except KeyboardInterrupt:
        producercliente = KafkaProducer( bootstrap_servers=broker,)
        mensaje_cliente = f"ID:{obtener_cliente(sys.argv[5])} KO"
        producercliente.send('TAXI-CLIENTE',value=mensaje_cliente.encode('utf-8'))
        sacar_taxi(int(sys.argv[5]))
        sacar_token(int(sys.argv[5]))
        os._exit(1)



# Función servidor con el Sensor
def start(broker):
    global PORT
    global parar_hilo_enviar_coord
    global msg_sensor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    ADDR=(SERVER,PORT)
    print(ADDR)
    server.bind(ADDR)
    server.listen()

    while True:
        try:
            conn, addr = server.accept()
            handle_server()
            if autentificado:
                msg_sensor = conn.recv(1024).decode('utf-8')
                hilo_enviar_coord = threading.Thread(target=enviar_coord, args=(broker,))
                hilo_enviar_coord.start()
                while msg_sensor:
                    msg_sensor = conn.recv(1024).decode('utf-8')
                    #print(msg_sensor)
                conn.close()
                hilo_enviar_coord.join()

        except ConnectionResetError:
            print("El sensor se ha perdido, esperando a que se conecte otro...")
            parar_hilo_enviar_coord = True
            

# Función para dibujar el mapa en la terminal
def dibujar_mapa(tamano=21):
    # Crear el mapa como una matriz de caracteres vacíos
    mapa = [["." for _ in range(tamano)] for _ in range(tamano)]
    
    # Marcar la posición del destino
    mapa[destinoY][destinoX] = "D"  # 'D' para destino
    
    # Marcar la posición actual del taxi
    mapa[Y_taxi][X_taxi] = "T"  # 'T' para taxi
    
    # Mostrar el mapa
    print("\n" * 2)  # Espaciado adicional para facilitar visualización
    for fila in mapa:
        print(" ".join(fila))
    print(f"\nTaxi en: ({X_taxi}, {Y_taxi}), Destino en: ({destinoX}, {destinoY})\n")


# Simulación del movimiento del taxi hacia el destino
def mover_taxi():
    global X_taxi, Y_taxi
    while X_taxi != destinoX or Y_taxi != destinoY:
        # Movimiento en eje X
        if X_taxi < destinoX:
            X_taxi += 1
        elif X_taxi > destinoX:
            X_taxi -= 1

        # Movimiento en eje Y
        if Y_taxi < destinoY:
            Y_taxi += 1
        elif Y_taxi > destinoY:
            Y_taxi -= 1

        # Dibujar el mapa en cada paso del movimiento
        dibujar_mapa()

    print("El taxi ha llegado al destino!")




#MAIN

if __name__ == "__main__":

    if (len(sys.argv)==6):
        try:
            SERVER_CLIENT = sys.argv[1]
            PORT_CLIENT = int(sys.argv[2])
            ip_broker = sys.argv[3]
            puerto_broker = sys.argv[4]
            broker = f'{ip_broker}:{puerto_broker}'
            ADDR_CLIENT = (SERVER_CLIENT,PORT_CLIENT)
            hilo_servidor = threading.Thread(target= servidor(broker))
            hilo_servidor.start()
        except KeyboardInterrupt:
            print("saca taxi")
            try:
                producercliente = KafkaProducer( bootstrap_servers=broker,)
                mensaje_cliente = f"ID:{obtener_cliente(sys.argv[5])} KO"
                producercliente.send('TAXI-CLIENTE',value=mensaje_cliente.encode('utf-8'))
                sacar_taxi(int(sys.argv[5]))
                sacar_token(int(sys.argv[5]))
            except KeyboardInterrupt:
                print("sale segundo keyinterrup")
                os._exit(1)

    

    else:
        print("Los argumentos son:<Ip del EC_Central><Puerto del EC_Central><Ip del broker><Puerto del broker><ID del taxi>")