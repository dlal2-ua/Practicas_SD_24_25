from kafka import KafkaProducer, KafkaConsumer
from threading import Thread
import time

"""
DEMO DE CENTRAL PARA PROBAR CLIENTES:

    -Decisión: La tabla de clientes cuando se ejecuta la central aparece vacía, pero al recibir un mensaje de un cliente, 
    se actualiza la tabla con el ID del cliente, el destino y el estado del mensaje.
    -El estado del mensaje se actualiza cuando haya un taxi libre y se le asocie al cliente.


    El hilo encargado de recibir mensajes (hilo_lector_mensajes) recibe mensajes de los clientes a través del tópico CLIENTES y pasa los datos del cliente y destino a la cola.
    Otro hilo (procesar_mensajes) procesa la cola y actualiza el estado del cliente, luego envía una confirmación.

    Hemos decidido que:
        -Si la central recibe un mensaje de cierre, primero procesa todos los mensajes que están en la cola, luego se asegura de que los hilos se terminen limpiamente 
        y finalmente cierra la central. Esto evita perder cualquier mensaje en tránsito.
        
    
"""

"""
# Función para actuar como consumidor
def consume_messages():
    consumer = KafkaConsumer('CLIENTES', bootstrap_servers='127.0.0.1:9092')
    for message in consumer:
        print(f"Mensaje recibido: {message.value.decode('utf-8')}")

# Función para actuar como productor
def produce_messages():
    producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
    while True:
        mensaje = input("Ingresa un mensaje para enviar: ")
        producer.send('CENTRAL-CLIENTE', mensaje.encode('utf-8'))
        producer.flush()
        time.sleep(1)


# Crear hilos para ejecutar productor y consumidor simultáneamente
if __name__ == "__main__":
    consumer_thread = Thread(target=consume_messages)
    producer_thread = Thread(target=produce_messages)

    # Iniciar ambos hilos
    consumer_thread.start()
    producer_thread.start()

    # Esperar que ambos hilos terminen (esto ocurre cuando terminen de ejecutarse sus loops)
    consumer_thread.join()
    producer_thread.join()

"""

from kafka import KafkaConsumer, KafkaProducer
import threading
import time
import queue
import pandas as pd
import signal
import sys

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

# Función para actualizar e imprimir la tabla de clientes
def actualizar_tabla(cliente_id, destino):
    global tabla
    with lock:
        # Verificar si el cliente ya está en la tabla
        if cliente_id in tabla['ID'].values:
            # Actualizar el destino y estado del cliente existente
            tabla.loc[tabla['ID'] == cliente_id, ['DESTINO', 'ESTADO']] = [destino, 'EN ESPERA']
        else:
            # Agregar un nuevo cliente a la tabla si no existe
            nueva_fila = pd.DataFrame({
                "ID": [cliente_id],
                "DESTINO": [destino],
                "ESTADO": ["EN ESPERA"]
            })
            tabla = pd.concat([tabla, nueva_fila], ignore_index=True)

        # Imprimir la tabla actualizada
        print("\nTabla de Clientes:")
        print("+---------+---------+------------+")
        print("|   ID    | DESTINO |   ESTADO   |")
        print("+---------+---------+------------+")
        for _, row in tabla.iterrows():
            print(f"|   {row['ID']:<5}  | {row['DESTINO']:<7} | {row['ESTADO']:<10} |")
        print("+---------+---------+------------+")

# Función para recibir mensajes de clientes y actualizar la tabla
def hilo_lector_mensajes(broker, cola_mensajes):
    consumer = KafkaConsumer(
        'CLIENTES',
        bootstrap_servers=broker,
        auto_offset_reset='earliest',
        group_id='grupo_lectores'
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

        # Actualizar la tabla
        actualizar_tabla(cliente_id, destino)

        # Simula un pequeño retraso entre mensajes
        time.sleep(1)

# Función para procesar la cola de mensajes y enviar confirmación
def procesar_mensajes(broker, cola_mensajes):
    producer = KafkaProducer(bootstrap_servers=broker)
    
    while central_activa or not cola_mensajes.empty():
        if not cola_mensajes.empty():
            cliente_id, destino = cola_mensajes.get()

            # Simular procesamiento del destino y cambiar el estado a "PROCESADO"
            with lock:
                tabla.loc[tabla['ID'] == cliente_id, 'ESTADO'] = 'PROCESADO'

            # Enviar confirmación al cliente a través del tópico 'CENTRAL-CLIENTE'
            mensaje_confirmacion = f"ID:{cliente_id} OK"
            producer.send('CENTRAL-CLIENTE', key=cliente_id.encode('utf-8'), value=mensaje_confirmacion.encode('utf-8'))
            producer.flush()
            print(f"Confirmación enviada al cliente {cliente_id}: {mensaje_confirmacion}")

        time.sleep(2)  # Simula un pequeño retraso en el procesamiento de cada mensaje

    print("Procesamiento de la cola completado. Cerrando el hilo procesador...")

# Función principal
def iniciar_central(broker):
    # Establecer el manejador de la señal de cierre (Ctrl+C)
    signal.signal(signal.SIGINT, manejar_cierre)

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


