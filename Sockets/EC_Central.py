import socket
import threading
import sys
from kafka import KafkaConsumer, KafkaProducer
import time
import queue
import pandas as pd
import signal
import sqlite3
from funciones_generales import conectar_bd


"""
En Python, no se puede manejar señales (como SIGINT o SIGTERM) en hilos secundarios.
puedes manejar las señales como SIGINT en el hilo principal y luego comunicar este evento a los 
hilos secundarios mediante una variable compartida o una cola para que se detengan adecuadamente.
"""

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 6060
ADDR=(SERVER,PORT)
FORMAT = 'utf-8'


#=======================================================================================================================================================================
#=======================================================================================================================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Inicializar una tabla (DataFrame) con las columnas ID, DESTINO, ESTADO
tabla = pd.DataFrame(columns=["ID", "DESTINO", "ESTADO"])

# Cola para almacenar los mensajes entrantes de los clientes
cola_mensajes = queue.Queue()

# Cola para la información del tablero
cola_tablero = queue.Queue()

# Lista para mantener un registro de clientes que ya están en el tablero
clientes_tablero = set()

# Bloqueo para sincronizar la tabla
lock = threading.Lock()

# ** Lista global para mantener todos los clientes visibles en el tablero
clientes_a_mostrar_global = []

# Variable para controlar si la central está activa
central_activa = True

server_active = True  # Variable global para controlar la actividad del servidor



# Manejador de la señal SIGINT para cerrar la central limpiamente
def manejar_cierre(signal, frame):
    global central_activa, server_active
    print("\nSeñal de cierre recibida. Procesando mensajes pendientes...")
    central_activa = False
    server_active = False


# Función para imprimir la tabla de clientes solo si hay datos
def imprimir_tabla():
    global tabla
    print("\nTabla de Clientes:")
    print("+---------+---------+------------+")
    print("|   ID    | DESTINO |   ESTADO   |")
    print("+---------+---------+------------+")
    if not tabla.empty:
        for _, row in tabla.iterrows():
            print(f"|   {row['ID']:<5}  | {row['DESTINO']:<7} | {row['ESTADO']:<10} |")
    else:
        print("|          NO HAY DATOS          |")
    print("+---------+---------+------------+")

# Función para actualizar la tabla de clientes
def actualizar_tabla(cliente_id, destino):
    global tabla
    with lock:
        # Verificar si el cliente ya está en la tabla
        if cliente_id in tabla['ID'].values:
            # Actualizar el destino y estado del cliente existente
            tabla.loc[tabla['ID'] == cliente_id, ['DESTINO', 'ESTADO']] = [destino, 'EN ESPERA']
            print(f"\nActualización: Cliente {cliente_id} actualizado con destino {destino}. Estado: EN ESPERA.")
        else:
            # Agregar un nuevo cliente a la tabla si no existe
            nueva_fila = pd.DataFrame({
                "ID": [cliente_id],
                "DESTINO": [destino],
                "ESTADO": ["EN ESPERA"]
            })
            tabla = pd.concat([tabla, nueva_fila], ignore_index=True)
            print(f"\nNuevo cliente añadido: {cliente_id}. Destino: {destino}. Estado: EN ESPERA.")

        # Imprimir la tabla actualizada
        imprimir_tabla()


# Función para recibir mensajes de clientes y actualizar la tabla
def hilo_lector_cliente(broker, cola_mensajes):
    consumer = KafkaConsumer('CLIENTES', bootstrap_servers=broker)
    producer = KafkaProducer(bootstrap_servers=broker)

    # Aquí abrimos una nueva conexión en el hilo actual
    conexion = conectar_bd()

    for message in consumer:
        if not central_activa:
            break  # Terminar el hilo si la central está cerrando

        # Decodificar el mensaje recibido
        mensaje = message.value.decode('utf-8')
        print(f"Mensaje recibido: {mensaje}")

        # Verificar si el cliente está pidiendo si la central está activa
        if mensaje == "Central activa?":
            cliente_id = message.key.decode('utf-8')  # ID del cliente desde el 'key'
            respuesta = "Central está operativa"
            producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=respuesta.encode('utf-8'))
            producer.flush()
            print(f"Respondido al cliente {cliente_id}: {respuesta}")
            continue  # Saltar al siguiente mensaje, no procesar destinos aún

        # Extraer el cliente y el destino del mensaje recibido
        try:
            partes = mensaje.split()
            cliente_id = partes[1].strip("'")  # Extraer ID del cliente sin las comillas
            destino = partes[-1]  # El último valor es el destino
        except IndexError:
            print(f"Error procesando el mensaje: {mensaje}")
            continue

        # Obtener coordenadas iniciales del cliente
        coordX, coordY = obtener_pos_inicial_cliente(cliente_id)

        # Añadir el mensaje a la cola de mensajes para procesarlo
        cola_mensajes.put((cliente_id, destino))  # Guardar también las coordenadas

        # Si el cliente no está en el tablero, añadirlo
        if cliente_id not in clientes_tablero:
            # Añadir el cliente a la cola del tablero para actualizar la posición en el mapa
            cola_tablero.put((cliente_id, destino, (coordX, coordY)))
            clientes_tablero.add(cliente_id)  # Marcar cliente como añadido al tablero

        # ** Añadir el cliente a la lista global
        clientes_a_mostrar_global.append((cliente_id, destino, (coordX, coordY)))

        # Actualizar la tabla con la nueva información
        actualizar_tabla(cliente_id, destino)

        # ==============
        # Obtener un taxi disponible desde la base de datos
        taxi_asignado = obtener_taxi_disponible(conexion)

        if taxi_asignado:
            # Obtener coordenadas iniciales del cliente
            coordX_cliente, coordY_cliente = obtener_pos_inicial_cliente(cliente_id)

            if coordX_cliente is not None and coordY_cliente is not None:
                mensaje_asignacion = f"ID:{cliente_id} ASIGNADO TAXI:{taxi_asignado} COORDENADAS:{coordX_cliente},{coordY_cliente} DESTINO:{destino}"
                print(f"Taxi asignado: {taxi_asignado} al cliente {cliente_id} en coordenadas {coordX_cliente}, {coordY_cliente}")

                # Enviar el mensaje de asignación al taxi con las coordenadas del cliente y el destino
                producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_asignacion.encode('utf-8'))
                producer.flush()
            else:
                print(f"No se encontraron coordenadas para el cliente {cliente_id}, no se puede asignar taxi.")
        else:
            print(f"No hay taxis disponibles para el cliente {cliente_id}")
        # ==============

        # Simula un pequeño retraso entre mensajes
        time.sleep(1)



# Función para escuchar las coordenadas de los taxis y procesar si ha llegado al cliente o destino
def hilo_lector_taxis(broker):
    consumer = KafkaConsumer('TAXIS', bootstrap_servers=broker)

    while central_activa:
        for message in consumer:
            # Decodificar el mensaje recibido del taxi
            mensaje = message.value.decode('utf-8')
            print(f"Mensaje recibido del taxi: {mensaje}")

            # Extraer el ID del taxi y sus coordenadas
            try:
                partes = mensaje.split(",")
                taxi_id = int(partes[0])
                coordX_taxi = int(partes[1])  # Coordenada X
                coordY_taxi = int(partes[2])  # Coordenada Y

                print(f"Taxi ID: {taxi_id}, Coordenadas: ({coordX_taxi}, {coordY_taxi})")
            except IndexError:
                print(f"Error procesando el mensaje del taxi: {mensaje}")
                continue

            # Verificar si el taxi está asignado a un cliente y comparar coordenadas
            procesar_coordenadas_taxi(taxi_id, coordX_taxi, coordY_taxi, broker)





# Función para procesar las coordenadas del taxi y verificar si ha llegado al cliente o destino
def procesar_coordenadas_taxi(taxi_id, coordX_taxi, coordY_taxi, broker):

    producer = KafkaProducer(bootstrap_servers=broker)
    conexion = conectar_bd()

    # Buscar si este taxi está asignado a algún cliente en el sistema
    for cliente in clientes_a_mostrar_global:
        cliente_id, destino, (coordX_cliente, coordY_cliente) = cliente

        # Verificar si el taxi ha llegado a la posición del cliente
        if abs(coordX_taxi - coordX_cliente) < 0.1 and abs(coordY_taxi - coordY_cliente) < 0.1:
            print(f"Taxi {taxi_id} ha recogido al cliente {cliente_id}.")
            # Actualizar el estado del cliente en la tabla a 'EN TAXI'
            with lock:
                tabla.loc[tabla['ID'] == cliente_id, 'ESTADO'] = f"EN TAXI {taxi_id}"
                imprimir_tabla()

            # Enviar confirmación al cliente a través del tópico 'CENTRAL-CLIENTE'
            mensaje_confirmacion = f"ID:{cliente_id} IN"
            producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_confirmacion.encode('utf-8'))
            producer.flush()
            print(f"Confirmación enviada al cliente {cliente_id}: {mensaje_confirmacion}")

            # Enviar el destino al taxi
            destino_coords = obtener_destino_coords(conexion, destino)
            conexion.close()

            if destino_coords:
                coordX_destino, coordY_destino = destino_coords
                mensaje_destino = f"ID:{cliente_id} DESTINO COORDENADAS:{coordX_destino},{coordY_destino}"
                producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_destino.encode('utf-8'))
                producer.flush()
                print(f"Enviado al taxi {taxi_id} las coordenadas del destino {destino}: {coordX_destino}, {coordY_destino}.")

        # Verificar si el taxi ha llegado al destino
        if destino_coords and abs(coordX_taxi - coordX_destino) < 0.1 and abs(coordY_taxi - coordY_destino) < 0.1:
            print(f"Taxi {taxi_id} ha llegado al destino del cliente {cliente_id}.")
            # Actualizar el estado del cliente a 'HA LLEGADO'
            with lock:
                tabla.loc[tabla['ID'] == cliente_id, 'ESTADO'] = 'HA LLEGADO'
                imprimir_tabla()

            # Enviar confirmación al cliente de que ha llegado al destino
            mensaje_confirmacion = f"ID:{cliente_id} OK"
            producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_confirmacion.encode('utf-8'))
            producer.flush()
            print(f"Confirmación enviada al cliente {cliente_id}: {mensaje_confirmacion}")

            # Liberar el taxi
            liberar_taxi(conexion, taxi_id)



###================== FUNCIONES DE BASE DE DATOS ==================###

# Función para obtener destinos desde la base de datos
def obtener_destinos(conexion):
    query = "SELECT destino, coordX, coordY FROM destinos"
    df_destinos = pd.read_sql_query(query, conexion)
    destinos_dict = {row['destino']: (row['coordX'], row['coordY']) for _, row in df_destinos.iterrows()}
    return destinos_dict


# Función para liberar un taxi después de completar el viaje
def liberar_taxi(conexion, taxi_id):
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET estado = 1 WHERE id = ?", (taxi_id,))
    conexion.commit()  # Asegurar que los cambios se guarden en la base de datos



# Función para obtener un taxi disponible desde la base de datos
def obtener_taxi_disponible(conexion):
    cursor = conexion.cursor()

    # Consulta para seleccionar un taxi disponible (estado = 1)
    cursor.execute("SELECT id FROM taxis WHERE estado = 1 LIMIT 1")
    taxi = cursor.fetchone()

    # Si se encuentra un taxi disponible, cambiar su estado a ocupado (0)
    if taxi:
        taxi_id = taxi[0]
        cursor.execute("UPDATE taxis SET estado = 0 WHERE id = ?", (taxi_id,))
        conexion.commit()  # Asegurar que los cambios se guarden en la base de datos
        return taxi_id
    else:
        return None  # No hay taxis disponibles


# Función para obtener las coordenadas iniciales del cliente
def obtener_pos_inicial_cliente(cliente_id):
    # Establecer una nueva conexión a la base de datos para cada hilo
    conexion = conectar_bd()
    try:
        # Usar parámetros en la consulta para evitar inyección SQL
        query = "SELECT coordX, coordY FROM pos_inicial_cliente WHERE id = ?"
        df_pos_inicial = pd.read_sql_query(query, conexion, params=(cliente_id,))
        if not df_pos_inicial.empty:
            return df_pos_inicial['coordX'][0], df_pos_inicial['coordY'][0]
        else:
            print(f"No se encontraron coordenadas para el cliente {cliente_id}.")
            return None, None  # Manejo del error
    finally:
        conexion.close()  # Asegúrate de cerrar la conexión después de usarla



# Función para obtener las coordenadas del destino desde la base de datos
def obtener_destino_coords(conexion, destino):
    query = "SELECT coordX, coordY FROM destinos WHERE destino = ?"
    cursor = conexion.cursor()
    cursor.execute(query, (destino,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0], resultado[1]  # Retornar coordX y coordY
    else:
        print(f"No se encontraron coordenadas para el destino {destino}")
        return None


###===========================================================================
###===========================================================================


# Función para crear y actualizar el tablero
def actualizar_tablero(ax, destinos, clientes):
    # Eliminar parches anteriores
    for patch in ax.patches:
        patch.remove()

    for txt in ax.texts:
        txt.remove()

    # Agregar destinos al tablero (que son estáticos)
    for label, (x, y) in destinos.items():
        ax.add_patch(plt.Rectangle((x - 1, y - 1), 1, 1, color="deepskyblue"))
        ax.text(x - 0.5, y - 0.5, label, va='center', ha='center', fontsize=10, color="black")

    # Agregar clientes en su posición inicial
    for cliente_id, destino, (coordX, coordY) in clientes:
        ax.add_patch(plt.Rectangle((coordX - 1, coordY - 1), 1, 1, color="yellow"))
        ax.text(coordX - 0.5, coordY - 0.5, cliente_id, fontsize=10, ha='center', va='center', color='black')

    plt.draw()
    plt.pause(0.01)





    

# Función para iniciar la central (debe ejecutarse en el hilo principal)
def iniciar_central(broker):
    imprimir_tabla()

    fig, ax = plt.subplots(figsize=(8, 8))
    grid_size = 20

    ax.set_xlim(0.1, grid_size)
    ax.set_ylim(0.1, grid_size)
    ax.set_xticks(np.arange(1, grid_size + 1))
    ax.set_yticks(np.arange(1, grid_size + 1))
    ax.grid(True)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.tick_params(axis='both', which='both', length=0)

    conexion = conectar_bd()
    destinos = obtener_destinos(conexion)
    actualizar_tablero(ax, destinos, [])

    # Iniciar hilo para escuchar mensajes de clientes
    hilo_lector = threading.Thread(target=hilo_lector_cliente, args=(broker, cola_mensajes))
    hilo_lector.start()

    # Iniciar hilo para escuchar coordenadas de los taxis
    hilo_lector_taxis_thread = threading.Thread(target=hilo_lector_taxis, args=(broker,))
    hilo_lector_taxis_thread.start()

    # Bucle principal de la interfaz gráfica (Matplotlib)
    while central_activa:
        if clientes_a_mostrar_global:
            actualizar_tablero(ax, destinos, clientes_a_mostrar_global)
        plt.pause(0.1)

    print("Central cerrada correctamente.")


    



#=======================================================================================================================================================================
#=======================================================================================================================================================================

"""
def leer_coord(broker):
    consumer = KafkaConsumer(
        'TAXIS',
        bootstrap_servers=broker,
        auto_offset_reset='earliest',  
        enable_auto_commit=True,  
    )

    for mensaje in consumer:
        msg = mensaje.value.decode('utf-8')  
        print(f"Mensaje recibido: {msg}") 
        try:
            partes = msg.split(",")
            taxi_id = int(partes[0])
            coordX_taxi = int(partes[1])  # Coordenada X
            coordY_taxi = int(partes[2])  # Coordenada Y

            print(f"Taxi ID: {taxi_id}, Coordenadas: ({coordX_taxi}, {coordY_taxi})")
        except IndexError:
            print(f"Error procesando el mensaje del taxi: {mensaje}")
            continue
        break
    consumer.close()
"""


def buscar_taxi_arg(msg):
    conexion = sqlite3.connect('database.db')
    query = f"SELECT id FROM taxis WHERE id == {msg}"
    df_busqueda = pd.read_sql_query(query,conexion)
    if df_busqueda.empty:
        return False
    else:
        return True

def handle_client(conn, addr,broker):
    msg = conn.recv(1024).decode(FORMAT)
    if buscar_taxi_arg(msg):
        print(f"El taxi con id {msg} está autentificado")
        conn.send("Taxi correctamente autentificado".encode(FORMAT))
        #leer_coord(broker)
        #hilo_lector_taxis(broker)
    else:
        print(f"Se ha intentado conectar el taxi con id {msg} pero no está en la bbdd")
        conn.send("Este taxi no está registrado en la bbdd".encode(FORMAT))
    conn.close()

def start(broker):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()


    while server_active:
        conn, addr = server.accept()
        handle_client(conn,addr,broker)
    server.close()
    print("Servidor cerrado correctamente.")


# Función principal unificada
def main():
    if len(sys.argv) == 3:
        ip_broker = sys.argv[1]
        puerto_broker = sys.argv[2]
        broker = f'{ip_broker}:{puerto_broker}'

        # Registrar la señal SIGINT para manejarla en el hilo principal
        signal.signal(signal.SIGINT, manejar_cierre)

        # Crear hilo para el servidor
        hilo_servidor = threading.Thread(target=start, args=(broker,))
        hilo_servidor.start()

        # Iniciar la central en el hilo principal (para evitar el problema de Matplotlib)
        iniciar_central(broker)

        # Esperar a que el hilo del servidor termine
        hilo_servidor.join()
    else:
        print("Los argumentos introducidos no son los correctos. El formato es: <IP gestor de colas> <puerto del broker del gestor de colas>")

if __name__ == "__main__":
    main()