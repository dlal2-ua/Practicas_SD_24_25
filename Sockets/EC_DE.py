import socket 
import threading
import time
import sys
from kafka import KafkaConsumer, KafkaProducer


HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'

def enviar_coord(broker):
    producer = KafkaProducer(
        bootstrap_servers=broker,
    )
    id_taxi = sys.argv[5]
    coordenada = id_taxi + ",6,5"

    print(f"Mensaje enviado: {coordenada}")
    producer.send('TAXIS', value=coordenada.encode('utf-8'))
    producer.flush()
    producer.close()
#Función cliente con la central
def handle_server():
    contador = 0
    while True:
        try:                
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR_CLIENT)
            msg = sys.argv[5]
            message = msg.encode(FORMAT)
            client.sendall(message)
            break
        except ConnectionRefusedError:
                if contador == 0:
                    print("La central no está conectada. Esperando a que se conecte...")
                contador += 1
                time.sleep(1)
    respuesta = client.recv(2048).decode(FORMAT)
    print(respuesta)

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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR=(SERVER,PORT)
    server.bind(ADDR)
    print(f"Puerto en el que está escuchando: {PORT}")
    server.listen()

    while True:
        try:
            conn, addr = server.accept()
            handle_server()
            enviar_coord(broker)
            msg = conn.recv(1024).decode('utf-8')
            while msg:
                msg = conn.recv(1024).decode('utf-8')
                print(msg)
            conn.close()
        except ConnectionResetError:
            print("El sensor se ha perdido, esperando a que se conecte otro...")





#MAIN

if (len(sys.argv)==6):
    SERVER_CLIENT = sys.argv[1]
    PORT_CLIENT = int(sys.argv[2])
    ip_broker = sys.argv[3]
    puerto_broker = sys.argv[4]
    broker = f'{ip_broker}:{puerto_broker}'
    ADDR_CLIENT = (SERVER_CLIENT,PORT_CLIENT)
    hilo_servidor = threading.Thread(target= servidor(broker))
    hilo_servidor.start()

else:
    print("Los argumentos son:<Ip del EC_Central><Puerto del EC_Central><Ip del broker><Puerto del broker><ID del taxi>")