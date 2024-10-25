import socket 
import threading
import time
import sys
from kafka import KafkaConsumer, KafkaProducer
from funciones_generales import coordX_taxi,coordY_taxi,nueva_pos_taxi,pasajero_dentro,sacar_taxi

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'
parar_hilo_enviar_coord = False

def enviar_coord(broker,):
    global parar_hilo_enviar_coord
    global msg_sensor
    producer = KafkaProducer(
        bootstrap_servers=broker,
    )

    consumer= KafkaConsumer('CENTRAL-TAXI', bootstrap_servers=broker)
    id_taxi = sys.argv[5]
    for message in consumer:
        # Decodificar el mensaje recibido del taxi
        mensaje = message.value.decode('utf-8')
        
        # Extraer el ID del taxi y sus coordenadas
        try:
            partes = mensaje.split(",")
            taxi = int(partes[0])
            if taxi == int(id_taxi) :
                destinoX = int(partes[1])  
                destinoY = int(partes[2])
                pasajero = partes[3]

                # Una vez que ha llegado, puedes manejar la lógica adicional aquí (ej: recoger el pasajero)
                if coordX_taxi(id_taxi) == destinoX and coordY_taxi(id_taxi) == destinoY:
                    print(f"Taxi {id_taxi} ha llegado al destino y ha recogido al pasajero {pasajero}.")
                    coordenada = str(id_taxi) + "," + str(coordX_taxi(id_taxi)) + "," + str(coordY_taxi(id_taxi)) + "," + str(msg_sensor)
                    producer.send('TAXIS', value=coordenada.encode('utf-8'))
                    time.sleep(1)
                else:
                    #pasajero_dentro(taxi,pasajero)
                    while coordX_taxi(id_taxi) != destinoX and parar_hilo_enviar_coord==False:
                        if msg_sensor == "OK":
                            if destinoX > coordX_taxi(id_taxi):
                                nuevaX = int(coordX_taxi(id_taxi)) + 1
                            else: 
                                nuevaX = int(coordX_taxi(id_taxi)) - 1
                            coordenada = str(id_taxi) + "," + str(nuevaX) + "," + str(coordY_taxi(id_taxi)) + "," + str(msg_sensor)
                            nueva_pos_taxi(id_taxi,nuevaX,coordY_taxi(id_taxi))
                            producer.send('TAXIS', value=coordenada.encode('utf-8'))
                            time.sleep(1)
                            while coordY_taxi(id_taxi) != destinoY and parar_hilo_enviar_coord == False:
                                if msg_sensor == "OK":
                                    if destinoY > coordY_taxi(id_taxi):
                                        nuevaY = int(coordY_taxi(id_taxi)) + 1
                                    else: 
                                        nuevaY = int(coordY_taxi(id_taxi)) - 1
                                    coordenada = str(id_taxi) + "," + str(coordX_taxi(id_taxi)) + "," + str(nuevaY) + "," + str(msg_sensor)
                                    nueva_pos_taxi(id_taxi,coordX_taxi(id_taxi),nuevaY)
                                    producer.send('TAXIS', value=coordenada.encode('utf-8'))
                                    time.sleep(1)
                                else:
                                    coordenada = str(id_taxi) + "," + str(coordX_taxi(id_taxi)) + "," + str(coordY_taxi(id_taxi)) + "," + str(msg_sensor)
                                    producer.send('TAXIS', value=coordenada.encode('utf-8'))
                                    time.sleep(1)
                        else:
                            coordenada = str(id_taxi) + "," + str(coordX_taxi(id_taxi)) + "," + str(coordY_taxi(id_taxi)) + "," + str(msg_sensor)
                            producer.send('TAXIS', value=coordenada.encode('utf-8'))
                            time.sleep(1)
        except IndexError:
            print(f"Error procesando el mensaje del taxi: {mensaje}")
            continue
    producer.close()
        

#Función cliente con la central
def handle_server():
    try:
        global autentificado
        autentificado = False
        contador = 0
        while True:
            try:                
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(ADDR_CLIENT)
                idTaxi = sys.argv[5]
                message = idTaxi.encode(FORMAT)
                client.sendall(message)
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
    except ConnectionResetError:
        print("Se ha perdido la conexion con la central")
#Función para que el puerto aumente automáticamente cuando se ejecuta mas de 1 DE
def servidor(broker):
    global PORT
    while True:
        try:
            start(broker)
        except OSError:
            PORT += 1


# Función servidor con el Sensor
def start(broker):
    global PORT
    global parar_hilo_enviar_coord
    global msg_sensor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR=(SERVER,PORT)
    server.bind(ADDR)
    print(f"Puerto en el que está escuchando: {PORT}")
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
                    print(msg_sensor)
                conn.close()
                hilo_enviar_coord.join()

        except ConnectionResetError:
            print("El sensor se ha perdido, esperando a que se conecte otro...")
            parar_hilo_enviar_coord = True
            




#MAIN

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
        sacar_taxi(int(sys.argv[5]))

else:
    print("Los argumentos son:<Ip del EC_Central><Puerto del EC_Central><Ip del broker><Puerto del broker><ID del taxi>")