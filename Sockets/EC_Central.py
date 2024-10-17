import socket
import threading
import sys
from kafka import KafkaConsumer, KafkaProducer
import time
import queue
import pandas as pd
import signal

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 6060
ADDR=(SERVER,PORT)
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 4


#=======================================================================================================================================================================
#=======================================================================================================================================================================

# Inicializar una tabla (DataFrame) con las columnas ID, DESTINO, ESTADO
tabla = pd.DataFrame(columns=["ID", "DESTINO", "ESTADO"])

# Cola para almacenar los mensajes entrantes de los clientes
cola_mensajes = queue.Queue()

# Bloqueo para sincronizar la tabla
lock = threading.Lock()

# Variable para controlar si la central está activa
central_activa = True

# Manejador de la señal SIGINT para cerrar la central limpiamente
def manejar_cierre(signal, frame):
    global central_activa
    print("\nSeñal de cierre recibida. Procesando mensajes pendientes...")
    central_activa = False

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
def hilo_lector_mensajes(broker, cola_mensajes):
    consumer = KafkaConsumer(
        'CLIENTES',
        bootstrap_servers=broker
    )

    for message in consumer:
        if not central_activa:
            break  # Terminar el hilo si la central está cerrando

        # Decodificar el mensaje recibido
        mensaje = message.value.decode('utf-8')
        print(f"Mensaje recibido: {mensaje}")

        # Extraer el cliente y el destino del mensaje recibido
        try:
            # Ejemplo del formato: "Cliente 'b' quiere ir a X"
            partes = mensaje.split()
            cliente_id = partes[1].strip("'")  # Extraer ID del cliente sin las comillas
            destino = partes[-1]  # El último valor es el destino
        except IndexError:
            print(f"Error procesando el mensaje: {mensaje}")
            continue

        # Añadir el mensaje a la cola
        cola_mensajes.put((cliente_id, destino))

        # Actualizar la tabla con la nueva información
        actualizar_tabla(cliente_id, destino)

        # Simula un pequeño retraso entre mensajes
        time.sleep(1)

# Función para procesar la cola de mensajes y enviar confirmación
def procesar_mensajes(broker, cola_mensajes):
    producer = KafkaProducer(bootstrap_servers=broker)
    
    while central_activa or not cola_mensajes.empty():
        if not cola_mensajes.empty():
            cliente_id, destino = cola_mensajes.get()

            # Simular procesamiento del destino y cambiar el estado a "EN TAXI"
            with lock:
                tabla.loc[tabla['ID'] == cliente_id, 'ESTADO'] = 'EN TAXI'

            # Imprimir la tabla actualizada
            imprimir_tabla()

            # Enviar confirmación al cliente a través del tópico 'CENTRAL-CLIENTE'
            mensaje_confirmacion = f"ID:{cliente_id} IN"
            producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_confirmacion.encode('utf-8'))
            producer.flush()
            print(f"Confirmación enviada al cliente {cliente_id}: {mensaje_confirmacion}")

            time.sleep(5)  # Simula un pequeño retraso en el procesamiento de cada mensaje

            # Simular procesamiento del destino y cambiar el estado a "EN TAXI"
            with lock:
                tabla.loc[tabla['ID'] == cliente_id, 'ESTADO'] = 'HA LLEGADO'

            # Imprimir la tabla actualizada
            imprimir_tabla()

            # Enviar confirmación al cliente a través del tópico 'CENTRAL-CLIENTE'
            mensaje_confirmacion = f"ID:{cliente_id} OK"
            producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_confirmacion.encode('utf-8'))
            producer.flush()
            print(f"Confirmación enviada al cliente {cliente_id}: {mensaje_confirmacion}")

        time.sleep(5)  # Simula un pequeño retraso en el procesamiento de cada mensaje

    exit(0)  # Salir del hilo si la central está cerrando y la cola está vacía
    print("Procesamiento de la cola completado. Cerrando el hilo procesador...")

# Función principal
def iniciar_central(broker):
    # Establecer el manejador de la señal de cierre (Ctrl+C)
    signal.signal(signal.SIGINT, manejar_cierre)

    # Imprimir la tabla vacía al inicio
    imprimir_tabla()

    # Crear e iniciar los hilos
    hilo_lector = threading.Thread(target=hilo_lector_mensajes, args=(broker, cola_mensajes))
    hilo_procesador = threading.Thread(target=procesar_mensajes, args=(broker, cola_mensajes))
    
    hilo_lector.start()
    hilo_procesador.start()

    # Esperar a que ambos hilos terminen
    hilo_lector.join()
    hilo_procesador.join()

    print("Central cerrada correctamente.")

# Ejecución del programa
if __name__ == "__main__": 
    broker = '127.0.0.1:9092'  # Dirección del broker de Kafka
    iniciar_central(broker)


#=======================================================================================================================================================================
#=======================================================================================================================================================================

def handle_client(conn, addr):
    msg_length = int(conn.recv(HEADER).decode(FORMAT))
    msg = conn.recv(msg_length).decode(FORMAT)
    if msg == "3" or msg == "4" or msg == "5":
        print(f"El taxi con id {msg} está autentificado")
    else:
        print(f"Se ha intentado conectar el taxi con id {msg} pero no está en la bbdd")
        conn.send("Este taxi no está registrado".encode(FORMAT))
    conn.close()

def start():
    server.listen()
    CONEX_ACTIVAS = threading.active_count()-1
    print(CONEX_ACTIVAS)
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        if (CONEX_ACTIVAS <= MAX_CONEXIONES): 
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONEXIONES ACTIVAS] {CONEX_ACTIVAS}")
            print("CONEXIONES RESTANTES PARA CERRAR EL SERVICIO", MAX_CONEXIONES-CONEX_ACTIVAS)
        else:
            print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
            conn.send("OOppsss... DEMASIADAS CONEXIONES. Tendrás que esperar a que alguien se vaya".encode(FORMAT))
            conn.close()
            CONEX_ACTUALES = threading.active_count()-1


if(len(sys.argv)==4):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    start()
else:
    print("Los argumentos introducidos no son los correctos.El formato es:<IP gestor de colas> <puerto del broker del gestor de colas> <IP y puerto de la BBDD>")
