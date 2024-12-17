from kafka import KafkaConsumer,KafkaProducer 
from funciones_generales import *
from colorama import *
import time

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
def ir_destino(broker,id_taxi,x,y,pasajero):
    producer = KafkaProducer(bootstrap_servers=broker)   
    conexion = conectar_bd()
    print("A que destino quieres ir?")
    destino = input()
    if existe_destino(destino):
        cambiar_destino(id_taxi,destino)
        coords = obtener_destino_coords(conexion,destino)
        coord_X = coords[0]
        coord_Y = coords[1]
        if hay_pasajero(id_taxi):
            mensaje = f"{id_taxi},{coord_X},{coord_Y},{pasajero[0]},{x},{y},cambiadocon" 
            producer.send('CENTRAL-TAXI', key=str(id_taxi).encode('utf-8'), value=mensaje.encode('utf-8'))
            print(Fore.GREEN + f"Se ha cambiado el destino de {pasajero[0]}")
        else:
            mensaje1 = f"{id_taxi},{coord_X},{coord_Y},{pasajero[0]},{x},{y},cambiadosin" 
            producer.send('CENTRAL-TAXI', key=str(id_taxi).encode('utf-8'), value=mensaje1.encode('utf-8'))
            print(Fore.GREEN + f"Se ha cambiado el destino del taxi {id}. En un momento el taxi seguirá con su ruta")
            time.sleep(20)
            (clienteX, clienteY) = obtener_pos_inicial_cliente(pasajero[0])
            coord_act_X = int(coordX_taxi(id_taxi))
            coord_act_Y = int(coordY_taxi(id_taxi))
            mensaje2 = f"{id_taxi},{clienteX},{clienteY},{pasajero[0]},{coord_act_X},{coord_act_Y},nada"
            producer.send('CENTRAL-TAXI', key=str(id_taxi).encode('utf-8'), value=mensaje2.encode('utf-8'))
            print(Fore.GREEN + f"El taxi va a recoger al cliente" )
    else:
        print("El destino que has puesto no está disponible")

def volver_base(broker,id_taxi,x,y,pasajero):
    cambiar_estado_TAXI_ciudad_ko(id_taxi)
    producer = KafkaProducer(bootstrap_servers=broker)
    mensaje = f"{id_taxi},1,1,{pasajero[0]},{x},{y},nada"
    producer.send('CENTRAL-TAXI', key=str(id).encode('utf-8'), value=mensaje.encode('utf-8'))
    producer.flush()



def volver_base2(broker,id_taxi,x,y):
    cambiar_estado_TAXI_ciudad_ko(id_taxi)
    producer = KafkaProducer(bootstrap_servers=broker)
    mensaje = f"{id_taxi},1,1,NULL,{x},{y},nada"
    producer.send('CENTRAL-TAXI', key=str(id).encode('utf-8'), value=mensaje.encode('utf-8'))
    producer.flush()

  
def reanudar_no_congelado(broker, id_taxi, x, y, pasajero, destino_a_cliente, destino_a_final):

    # Crear el productor Kafka
    producer = KafkaProducer(bootstrap_servers=broker)

    # Obtener conexión a la base de datos
    conexion = conectar_bd()

    # Determinar el destino del taxi
    if existe_pasajero(id_taxi):  # Caso: el pasajero ya está en el taxi
        cambiarEstadoCliente(conexion, destino_a_cliente, "EN TAXI {}".format(id_taxi))

        destinos = obtener_destino_coords(conexion, destino_a_final)
        destinoX, destinoY = destinos[0], destinos[1]
        mensaje = f"{id_taxi},{destinoX},{destinoY},{pasajero},{x},{y},nada"
    else:  # Caso: el taxi debe recoger al pasajero
        cambiarEstadoCliente(conexion, destino_a_cliente, "EN ESPERA")
        clienteX, clienteY = obtener_coord_cliente(destino_a_cliente)
        destinoX, destinoY = clienteX, clienteY
        mensaje = f"{id_taxi},{clienteX},{clienteY},{pasajero},{x},{y},nada"

    # Enviar el mensaje a la central
    producer.send('CENTRAL-TAXI', key=str(id_taxi).encode('utf-8'), value=mensaje.encode('utf-8'))
    producer.flush()

