from kafka import KafkaConsumer,KafkaProducer 
from funciones_generales import *

def para(broker,id,x,y,pasajero):
    producer = KafkaProducer(bootstrap_servers=broker)
    mensaje = f"{id},{x},{y},{pasajero[0]},{x},{y},Parar"
    producer.send('CENTRAL-TAXI', key=str(id).encode('utf-8'), value=mensaje.encode('utf-8'))
    producer.flush()

def reanudar(broker,id,x,y,pasajero):
    producer = KafkaProducer(bootstrap_servers=broker)
    conexion = conectar_bd()
    
    if existe_pasajero(id):
        destino_pasajero = obtener_destino_final_de_taxi(id)
        destinos = obtener_destino_coords(conexion,destino_pasajero[0])
        destinoX = destinos[0]
        destinoY = destinos[1]
        mensaje = f"{id},{destinoX},{destinoY},{pasajero[0]},{x},{y},Seguir"      
    else:
        (clienteX, clienteY) = obtener_pos_inicial_cliente(pasajero[0])
        mensaje = f"{id},{clienteX},{clienteY},{pasajero[0]},{x},{y},Seguir"
    producer.send('CENTRAL-TAXI', key=str(id).encode('utf-8'), value=mensaje.encode('utf-8'))
    producer.flush()
def ir_destino(id_taxi):
    print("A que destino quieres ir?")
    destino = input()
    existe_destino(destino)
