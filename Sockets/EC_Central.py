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
import numpy as np
import matplotlib.pyplot as plt
from queue import Queue

"""
En Python, no se puede manejr señales (como SIGINT o SIGTERM) en hilos secundarios.
puedes manejar las señales comao SIGINT en el hilo principal y luego comunicar este evento a los 
hilos secundarios mediante una variable compartida o una cola para que se detengan adecuadamente.
"""

"""
Uso de with conectar_bd() para abrir y cerrar conexiones: Esto asegura que las conexiones 
a la base de datos se abren y cierran correctamente en cada operación.

Ventaja: Evita errores de "base de datos cerrada" y mantiene la conexión abierta solo cuando es necesario.
"""

HEADER = 64
PORT = 6060
FORMAT = 'utf-8'


#=======================================================================================================================================================================
#=======================================================================================================================================================================




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

# Crear colas para la comunicación entre hilos
cola_taxis = Queue()


def obtener_ip():
    # Intenta conectarse a una dirección externa
    try:
        # La dirección IP 8.8.8.8 es un servidor DNS de Google
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return f"Error: {e}"


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


## Función para recibir mensajes de clientes y actualizar la tabla
def hilo_lector_cliente(broker, cola_mensajes):
    consumer = KafkaConsumer('CLIENTES', bootstrap_servers=broker)
    producer = KafkaProducer(bootstrap_servers=broker)

    conexion = conectar_bd()

    while True:
        if not central_activa:
            break  # Terminar el hilo si la central está cerrando

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

                if (buscarCliente(conexion, cliente_id) == False):
                    # Abre la conexión a la base de datos para agregar el cliente
                    agregarCliente(conexion, cliente_id, destino, "EN ESPERA", 0, 0)

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

                    agregarCoordCliente(conexion, cliente_id, coordX_cliente, coordY_cliente)

                    # Enviar el mensaje de asignación al taxi con las coordenadas del cliente y el destino
                    producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_asignacion.encode('utf-8'))
                    producer.flush()

                    # Iniciar un nuevo hilo para enviar las coordenadas del cliente al taxi
                    threading.Thread(target=hilo_enviar_coordenadas_taxi, args=(cliente_id, taxi_asignado, coordX_cliente, coordY_cliente, broker)).start()

                else:
                    print(f"No se encontraron coordenadas para el cliente {cliente_id}, no se puede asignar taxi.")
            else:
                print(f"No hay taxis disponibles para el cliente {cliente_id}")
            # ==============

            # Simula un pequeño retraso entre mensajes
            time.sleep(1)



# Función que envía las coordenadas del cliente al taxi por el tópico CENTRAL-TAXI
def hilo_enviar_coordenadas_taxi(cliente_id, taxi_id, coordX_cliente, coordY_cliente, broker):
    producer = KafkaProducer(bootstrap_servers=broker)

    # Preparar el mensaje con las coordenadas del cliente
    mensaje_coordenadas = f"{taxi_id},{coordX_cliente},{coordY_cliente},{cliente_id}"
    
    # Enviar mensaje al taxi a través del tópico 'CENTRAL-TAXI'
    producer.send('CENTRAL-TAXI', key=str(taxi_id).encode('utf-8'), value=mensaje_coordenadas.encode('utf-8'))
    producer.flush()
    
    print(f"Enviadas al taxi {taxi_id} las coordenadas de recogida del cliente {cliente_id}: ({coordX_cliente}, {coordY_cliente})")






# Función para escuchar las coordenadas de los taxis y procesar si ha llegado al cliente o destino
def hilo_lector_taxis(broker):
    consumer = KafkaConsumer('TAXIS', bootstrap_servers=broker)
    
    while central_activa:
        for message in consumer:
            mensaje = message.value.decode('utf-8')
            try:
                partes = mensaje.split(",")
                taxi_id = int(partes[0])
                coordX_taxi = int(partes[1])
                coordY_taxi = int(partes[2])
                print(f"Taxi ID: {taxi_id}, Coordenadas: ({coordX_taxi}, {coordY_taxi})")

                # Pasar las coordenadas procesadas al hilo principal mediante la cola
                cola_taxis.put((taxi_id, coordX_taxi, coordY_taxi))

            except IndexError:
                print(f"Error procesando el mensaje del taxi: {mensaje}")
                continue




clientes_en_taxi_global = []  # Clientes ya recogidos y en trayecto
def procesar_coordenadas_taxi(taxi_id, coordX_taxi, coordY_taxi, broker):
    conexion = conectar_bd()
    producer = KafkaProducer(bootstrap_servers=broker)

    try:
        taxis_en_tablero = []

        # Procesar clientes que están esperando ser recogidos por un taxi
        for cliente in clientes_a_mostrar_global:
            cliente_id, destino, (coordX_cliente, coordY_cliente) = cliente

            # Verificar si el taxi ha llegado a la posición del cliente
            if abs(coordX_taxi - coordX_cliente) < 0.1 and abs(coordY_taxi - coordY_cliente) < 0.1:
                print(f"Taxi {taxi_id} ha recogido al cliente {cliente_id}.")
                cambiarEstadoCliente(conexion, cliente_id, f"EN TAXI {taxi_id}")

                with lock:
                    tabla.loc[tabla['ID'] == cliente_id, 'ESTADO'] = f"EN TAXI {taxi_id}"
                    imprimir_tabla()

                # Mover al cliente de la lista de clientes esperando a la lista de clientes en taxi
                clientes_a_mostrar_global.remove(cliente)
                clientes_en_taxi_global.append((cliente_id, destino, taxi_id))

                # Actualizar la lista de taxis en el tablero
                taxis_en_tablero.append((taxi_id, coordX_taxi, coordY_taxi, 0, cliente_id))

                # Enviar confirmación al cliente
                mensaje_confirmacion = f"ID:{cliente_id} IN"
                producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_confirmacion.encode('utf-8'))
                producer.flush()
                print(f"Confirmación enviada al cliente {cliente_id}: {mensaje_confirmacion}")

                # Obtener coordenadas del destino y enviarlas al taxi
                destino_coords = obtener_destino_coords(conexion, destino)
                if destino_coords:
                    coordX_destino, coordY_destino = destino_coords
                    mensaje_destino = f"{taxi_id},{coordX_destino},{coordY_destino},{cliente_id}"
                    producer.send('CENTRAL-TAXI', key=cliente_id.encode('utf-8'), value=mensaje_destino.encode('utf-8'))
                    producer.flush()
                    print(f"Enviado al taxi {taxi_id} las coordenadas del destino {destino}: {coordX_destino}, {coordY_destino}.")
            else:
                # Si no se ha recogido a un cliente, actualizar el taxi como en movimiento
                taxis_en_tablero.append((taxi_id, coordX_taxi, coordY_taxi, 1, None))

        # Procesar clientes que están en trayecto en el taxi
        for cliente_id, destino, taxi_asignado in clientes_en_taxi_global:
            destino_coords = obtener_destino_coords(conexion, destino)
            if destino_coords:
                coordX_destino, coordY_destino = destino_coords
                # Verificar si el taxi ha llegado al destino del cliente
                if abs(coordX_taxi - coordX_destino) < 0.1 and abs(coordY_taxi - coordY_destino) < 0.1 and taxi_asignado == taxi_id:
                    print(f"Taxi {taxi_id} ha llegado al destino del cliente {cliente_id}.")
                    cambiarEstadoCliente(conexion, cliente_id, "HA LLEGADO")
                    cambiarPosInicialCliente(conexion, cliente_id, coordX_destino, coordY_destino)

                    with lock:
                        tabla.loc[tabla['ID'] == cliente_id, 'ESTADO'] = 'HA LLEGADO'
                    imprimir_tabla()

                    # Enviar confirmación de llegada al cliente
                    mensaje_confirmacion = f"ID:{cliente_id} OK"
                    producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_confirmacion.encode('utf-8'))
                    producer.flush()
                    print(f"Confirmación enviada al cliente {cliente_id}: {mensaje_confirmacion}")

                    # Liberar el taxi
                    liberar_taxi(conexion, taxi_id)

                    # Eliminar al cliente de la lista de clientes en trayecto
                    clientes_en_taxi_global.remove((cliente_id, destino, taxi_asignado))

                    # Actualizar la lista de taxis en el tablero (sin cliente)
                    taxis_en_tablero = [(tid, x, y, 1, None) if tid == taxi_id else (tid, x, y, cid) for tid, x, y, cid in taxis_en_tablero]
                else:
                    # Mantener al cliente en el taxi durante el trayecto
                    taxis_en_tablero.append((taxi_id, coordX_taxi, coordY_taxi, 0, cliente_id))

    finally:
        conexion.close()

    return taxis_en_tablero




###================== FUNCIONES DE BASE DE DATOS ==================###

# Función para obtener destinos desde la base de datos

def cambiarPosInicialCliente(conexion, id, coordX, coordY):
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE pos_inicial_cliente SET coordX = ?, coordY = ? WHERE id = ?", (coordX, coordY, id))
        conexion.commit()
    except sqlite3.Error as e:
        print(f"Error al actualizar coordenadas iniciales del cliente en la base de datos: {e}")

def agregarCliente(conexion, id, destino, estado, coordX, coordY):
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO clientes (id, destino, estado, coordX, coordY) VALUES (?, ?, ?, ?, ?)", (id, destino, estado, coordX, coordY))
        conexion.commit()
    except sqlite3.Error as e:
        print(f"Error al insertar cliente en la base de datos: {e}")

def buscarCliente(conexion, id):
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (id,))
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Error al buscar cliente en la base de datos: {e}")
        return False



def cambiarEstadoCliente(conexion, id, estado):
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE clientes SET estado = ? WHERE id = ?", (estado, id))
        conexion.commit()
    except sqlite3.Error as e:
        print(f"Error al actualizar estado del cliente en la base de datos: {e}")


def agregarCoordCliente(conexion, id, coordX, coordY):
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE clientes SET coordX = ?, coordY = ? WHERE id = ?", (coordX, coordY, id))
        conexion.commit()
    except sqlite3.Error as e:
        print(f"Error al actualizar coordenadas del cliente en la base de datos: {e}")



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
    
def obtener_taxis(conexion):
   
    cursor = conexion.cursor()
    query = """
        SELECT id, coordX, coordY, estado
        FROM taxis;
    """
    cursor.execute(query)
    taxis = cursor.fetchall()
    return taxis  # Retorna una lista de tuplas: (taxi_id, coordX, coordY, estado)


###===========================================================================
###===========================================================================

def procesar_taxis(conexion, clientes):

    taxis_en_tablero = []
    taxis = obtener_taxis(conexion)

    for taxi_id, coordX_taxi, coordY_taxi, estado in taxis:
        cliente_en_taxi = None

        # Verificar si el taxi ha llegado a la posición de algún cliente
        for cliente_id, destino, (coordX_cliente, coordY_cliente) in clientes:
            if abs(coordX_taxi - coordX_cliente) < 0.1 and abs(coordY_taxi - coordY_cliente) < 0.1:
                cliente_en_taxi = cliente_id
                clientes_a_mostrar_global.remove((cliente_id, destino, (coordX_cliente, coordY_cliente)))  # Remover cliente de la lista
                print(f"Taxi {taxi_id} ha recogido al cliente {cliente_id}.")  # Imprimir mensaje de recogida
                break  # Salir del bucle si se ha recogido a un cliente

        # Añadir taxi al tablero con el cliente si lo ha recogido
        taxis_en_tablero.append((taxi_id, coordX_taxi, coordY_taxi, estado, cliente_en_taxi))

        # Imprimir el cliente en taxi (puede ser None si no hay cliente)
        if cliente_en_taxi:
            print(f"Cliente en taxi: {cliente_en_taxi}")
        else:
            print("No hay cliente en taxi.")

    return taxis_en_tablero




# Función para actualizar el tablero (solo en el hilo principal)
def actualizar_tablero(ax, destinos, clientes, taxis):
    """Actualiza el tablero con las posiciones actuales."""
    # Limpiar el tablero de elementos anteriores (patches y texts)
    
    # Eliminar patches (rectángulos, que representan destinos y taxis)
    for patch in ax.patches[:]:
        patch.remove()

    # Eliminar textos (que muestran IDs y coordenadas)
    for txt in ax.texts[:]:
        txt.remove()

    for label, (x, y) in destinos.items():
        ax.add_patch(plt.Rectangle((x - 1, y - 1), 1, 1, color="deepskyblue"))
        ax.text(x - 0.5, y - 0.5, label, va='center', ha='center', fontsize=10, color="black")

    for cliente_id, destino, (coordX, coordY) in clientes:
        ax.add_patch(plt.Rectangle((coordX - 1, coordY - 1), 1, 1, color="yellow"))
        ax.text(coordX - 0.5, coordY - 0.5, cliente_id, fontsize=10, ha='center', va='center', color='black')

    for taxi_id, coordX_taxi, coordY_taxi, estado, cliente_en_taxi in taxis:
        color_taxi = "green" if estado == 0 else "red"  # Verde si está en movimiento, rojo si está estacionado
        ax.add_patch(plt.Rectangle((coordX_taxi - 1, coordY_taxi - 1), 1, 1, color=color_taxi))
        if cliente_en_taxi:
            ax.text(coordX_taxi - 0.5, coordY_taxi - 0.5, f"{taxi_id}-{cliente_en_taxi}", fontsize=8, ha='center', va='center', color='black')
        else:
            ax.text(coordX_taxi - 0.5, coordY_taxi - 0.5, f"{taxi_id}", fontsize=10, ha='center', va='center', color='black')

    plt.draw()
    plt.pause(0.01)



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
    actualizar_tablero(ax, destinos, [], [])  # Inicialmente, sin clientes ni taxis

    # Iniciar hilo para escuchar mensajes de clientes
    hilo_lector = threading.Thread(target=hilo_lector_cliente, args=(broker, cola_mensajes))
    hilo_lector.start()

    # Iniciar hilo para escuchar coordenadas de los taxis
    hilo_lector_taxis_thread = threading.Thread(target=hilo_lector_taxis, args=(broker,))
    hilo_lector_taxis_thread.start()

    # Bucle principal de la interfaz gráfica (Matplotlib)
    try:
        while central_activa:
            # Procesar mensajes en la cola (coordenadas de taxis)
            while not cola_taxis.empty():
                taxi_id, coordX_taxi, coordY_taxi = cola_taxis.get()
                
                # Procesar las coordenadas del taxi y obtener taxis en el tablero
                taxis_en_tablero = procesar_coordenadas_taxi(taxi_id, coordX_taxi, coordY_taxi, broker)

                # Actualizar el tablero con los taxis procesados
                #taxis_en_tablero = procesar_taxis(conexion, clientes_a_mostrar_global)
                actualizar_tablero(ax, destinos, clientes_a_mostrar_global, taxis_en_tablero)

            plt.pause(0.1)  # Permitir actualizaciones de la GUI
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        print("Cerrando hilos...")
        # Aquí podrías tener lógica para cerrar los hilos de manera ordenada si es necesario
        hilo_lector.join()  # Esperar a que termine el hilo del lector
        hilo_lector_taxis_thread.join()  # Esperar a que termine el hilo de taxis
        conexion.close()  # Cerrar la conexión a la base de datos
        print("Central cerrada correctamente.")
    



#=======================================================================================================================================================================
#=======================================================================================================================================================================
def autentificar_taxi(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET estado = 1 WHERE id = {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()

def buscar_taxi_arg(msg):
    conexion = conectar_bd()
    query = f"SELECT id FROM taxis WHERE id == {msg} AND estado IS NULL"
    df_busqueda = pd.read_sql_query(query,conexion)
    if df_busqueda.empty:
        conexion.close()
        return False
    else:
        conexion.close()
        return True

def handle_client(conn, addr,broker):
    msg = conn.recv(1024).decode(FORMAT)
    if buscar_taxi_arg(msg):
        autentificar_taxi(msg)
        print(f"El taxi con id {msg} está autentificado")
        conn.send("Taxi correctamente autentificado".encode(FORMAT))

    else:
        print(f"Se ha intentado conectar el taxi con id {msg} pero no ha sido posible")
        conn.send("Este taxi no se puede registrar en la bbdd".encode(FORMAT))
    conn.close()

def start(broker):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER = obtener_ip()
    ADDR=(SERVER,PORT)
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