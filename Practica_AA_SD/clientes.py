import time
import threading
from confluent_kafka import Producer, Consumer, KafkaException
import sys # Se utiliza para acceder a parámetros y funciones específicas del sistema (en este caso, para acceder a los argumentos de la línea de comandos)
import signal


"""
Pasos a implementar:

    1º Configuración de Kafka: El cliente debe conectarse al broker 
    Kafka que se pasa como argumento, junto con el ID del cliente.

    2º Lectura del archivo de servicios: Cada cliente debe leer de 
    un archivo la lista de servicios (destinos) que quiere solicitar.

    3º Publicación de eventos: El cliente enviará solicitudes de taxi a la 
    central (tema Kafka "EC_Central") con el destino donde quiere ir.

    4º Escuchar confirmaciones: Cuando el servicio finalice, se debe notificar al cliente. 
    Esto implicará que el cliente suscriba a un tema Kafka, por ejemplo, "EC_Confirmation_{client_id}".

    5º Gestión de nuevos servicios: Si el cliente tiene más servicios 
    en la lista, debe esperar 4 segundos antes de solicitar el siguiente.


"""

"""
Grupo de consumidores:

 -   El grupo de consumidores ya no se pasa como argumento. En su lugar, se genera un nombre de grupo único en función de la ID del cliente: group.id = f'grupo_consumidor_{cliente_id}'. Esto asegura que cada cliente tiene su propio grupo de consumidores.

 -   Alternativamente, si quieres que varios clientes compartan un grupo, podrías establecer un grupo por un conjunto de clientes, pero en este ejemplo, se ha hecho único por cada cliente.

Filtro de mensajes:

    -Se mantiene el filtrado de mensajes en el consumidor, donde se compara la clave (key) del mensaje recibido con la ID del cliente. Solo se procesa el mensaje si las claves coinciden, ignorando los demás mensajes.
Uso del grupo:

Dado que cada cliente tiene su propio grupo de consumidores basado en su ID, no es necesario especificar manualmente un grupo.
"""

"""
Flujo de ejecución:
    El productor envía un mensaje con el destino del cliente al tópico CLIENTES, usando la ID del cliente como clave (key).
    El consumidor escucha el tópico CENTRAL y procesa solo los mensajes cuya clave coincida con la ID del cliente, asegurándose de que cada cliente reciba solo los mensajes que le corresponden
"""

"""
Semáforo para sincronización:

    Se ha añadido un semáforo (threading.Semaphore) para sincronizar el envío de los destinos. El productor espera hasta que el consumidor libere el semáforo, lo que ocurre cuando se recibe un mensaje OK desde la central.
    Productor:

    El productor envía un destino y luego espera a que el semáforo se libere (tras recibir la confirmación de la central). Una vez recibido el OK, procede al siguiente destino. Esto se repite hasta que se hayan enviado todos los destinos.
    Consumidor:

    El consumidor escucha el tópico CENTRAL-CLIENTE y verifica si el mensaje recibido es del formato ID:<cliente_id> OK. Cuando el mensaje corresponde al cliente y es válido, libera el semáforo, permitiendo al productor enviar el siguiente destino.

"""


# Variable global para controlar la ejecución de los hilos
salir_programa = False
semaforo_terminacion = threading.Event()  # Señal para indicar cuando todos los destinos han sido procesados

# Manejador de la señal SIGINT para detener el programa con Ctrl+C
def manejar_ctrl_c(signal, frame):
    global salir_programa
    print("\nCtrl+C detectado, cerrando el programa...")
    salir_programa = True  # Establecer la bandera para salir
    semaforo_terminacion.set()  # Notificar que se debe cerrar

# Función para obtener todos los destinos del cliente desde un fichero
def obtener_info_cliente(cliente_id, fichero):
    destinos = []

    try:
        # Abrir el fichero y leer línea por línea
        with open(fichero, 'r') as f:
            lineas = f.readlines()

        # Procesar el archivo, buscando el cliente y sus destinos
        cliente_encontrado = False
        for linea in lineas:
            linea = linea.strip()  # Eliminar espacios y saltos de línea

            if not cliente_encontrado:
                # Buscar el cliente (en minúsculas)
                if linea == cliente_id:
                    cliente_encontrado = True
            else:
                # Buscar destinos en mayúsculas para el cliente
                if linea.isupper():
                    destinos.append(linea)
                elif linea.islower():
                    # Si encontramos otra letra en minúsculas, significa que es otro cliente, terminamos
                    break

        return destinos  # Devolver la lista de destinos

    except FileNotFoundError:
        print(f"Error: El fichero '{fichero}' no existe.")
        return []
    except Exception as e:
        print(f"Error al procesar el fichero: {e}")
        return []

# Función para enviar el destino al tópico de Kafka (Producer)
def enviar_a_kafka(producer, cliente_id, destino):
    mensaje = f"Cliente '{cliente_id}' quiere ir a {destino}"             
    print(mensaje)
    producer.produce('CLIENTES', key=cliente_id, value=mensaje)
    producer.flush()

# Hilo Productor que envía destinos uno a uno al tópico 'CLIENTES'
def hilo_productor_kafka(broker, cliente_id, destinos_cliente, semaforo):
    global salir_programa

    # Si no hay destinos, terminar el hilo productor
    if not destinos_cliente:
        print(f"El cliente {cliente_id} no tiene destinos y/o no existe.")
        return

    print(f"El cliente {cliente_id} tiene {len(destinos_cliente)} destinos.")

    # Configurar el productor Kafka
    producer_config = {
        'bootstrap.servers': broker
    }
    producer = Producer(producer_config)

    # Enviar destinos uno por uno, esperando confirmación de IN y OK
    for i, destino in enumerate(destinos_cliente):
        if salir_programa:
            break  # Salir del bucle si se ha recibido la señal de salida

        # 1. El cliente pide ir al destino
        mensaje_ir_destino = f"Cliente '{cliente_id}' quiere ir a {destino}"
        print(mensaje_ir_destino)
        producer.produce('CLIENTES', key=cliente_id, value=mensaje_ir_destino)
        producer.flush()

        # 2. Esperar la confirmación de recogida (IN)
        print(f"Esperando confirmación de recogida para el destino '{destino}'...")
        semaforo.acquire()  # Bloquear hasta recibir la confirmación de IN

        # 3. Después de la confirmación de recogida, mostrar el mensaje de recogida
        print(f"CLIENTE RECOGIDO, YENDO A '{destino}'")

        # 4. Enviar mensaje de llegada (OK)
        mensaje_llegada = f"Cliente '{cliente_id}' ha llegado a {destino}"
        producer.produce('CLIENTES', key=cliente_id, value=mensaje_llegada)
        producer.flush()

        # 5. Esperar la confirmación de llegada (OK)
        print(f"Esperando confirmación de llegada para el destino '{destino}'...")
        semaforo.acquire()  # Bloquear hasta recibir la confirmación de OK

        # 6. Confirmar que el cliente llegó al destino
        print(f"CLIENTE EN EL DESTINO '{destino}'")

        if i == len(destinos_cliente) - 1:
            semaforo_terminacion.set()  # Señalar que se ha completado el último destino

        print()  # Salto de línea para mejorar la legibilidad en la salida

# Hilo Consumidor que escucha el tópico 'CENTRAL-CLIENTE' y procesa mensajes en formato "ID:<cliente_id> IN" y "ID:<cliente_id> OK"
def hilo_consumidor_kafka(broker, cliente_id, semaforo):
    global salir_programa

    # Configuración del consumidor Kafka
    consumer_config = {
        'bootstrap.servers': broker,
        'group.id': f'grupo_consumidor_{cliente_id}',  # Grupo de consumidores basado en la ID del cliente
        'auto.offset.reset': 'earliest'  # Empezar desde el principio si no hay offset
    }

    # Suscribirse al tópico específico para el cliente
    consumer = Consumer(consumer_config)
    topic_cliente = 'CENTRAL-CLIENTE'
    consumer.subscribe([topic_cliente])

    try:
        while not salir_programa:
            msg = consumer.poll(timeout=0.02)  # Esperar por mensajes durante 0.02 segundos
            if msg is None:
                continue  # Si no hay mensajes, continuar

            if msg.error():
                raise KafkaException(msg.error())  # Manejo de errores del consumidor

            # Procesar el mensaje recibido
            mensaje = msg.value().decode('utf-8')

            # Verificar si es un mensaje de recogida (IN)
            if mensaje.startswith(f"ID:{cliente_id} IN"):
                semaforo.release()  # Liberar el semáforo para que el productor envíe el siguiente destino

            # Verificar si es un mensaje de llegada (OK)
            elif mensaje.startswith(f"ID:{cliente_id} OK"):
                semaforo.release()  # Liberar el semáforo para que el productor continúe o termine
                if semaforo_terminacion.is_set():
                    break  # Terminar la espera, ya que es el último destino
                    
    except KafkaException as e:
        print(f"Error en el consumidor: {e}")
    finally:
        # Cerrar el consumidor
        consumer.close()

# Validar que la ID del cliente sea un único carácter en minúscula
def validar_cliente_id(cliente_id):
    if len(cliente_id) != 1 or not cliente_id.islower():
        print("Error: La ID del cliente debe ser un único carácter en minúscula.")
        sys.exit(1)

# Función principal
if __name__ == "__main__":
    # Configurar el manejador de la señal Ctrl+C
    signal.signal(signal.SIGINT, manejar_ctrl_c)

    if len(sys.argv) != 4:
        print(f"Uso: python {sys.argv[0]} <broker_ip:puerto> <id_cliente> <fichero>")
        sys.exit(1)

    # Obtener parámetros de línea de comando
    broker = sys.argv[1]
    cliente_id = sys.argv[2]
    fichero = sys.argv[3]

    # Validar la ID del cliente
    validar_cliente_id(cliente_id)

    # Obtener todos los destinos del cliente
    destinos_cliente = obtener_info_cliente(cliente_id, fichero)

    # Crear un semáforo para coordinar la comunicación entre productor y consumidor
    semaforo = threading.Semaphore(0)

    # Crear los hilos para el productor y consumidor
    hilo_productor = threading.Thread(target=hilo_productor_kafka, args=(broker, cliente_id, destinos_cliente, semaforo))
    hilo_consumidor = threading.Thread(target=hilo_consumidor_kafka, args=(broker, cliente_id, semaforo))

    # Iniciar los hilos
    hilo_productor.start()
    hilo_consumidor.start()

    # Esperar a que se completen todos los destinos o se presione Ctrl+C
    try:
        semaforo_terminacion.wait()  # Esperar hasta que todos los destinos hayan sido enviados y confirmados
    except KeyboardInterrupt:
        print("Interrupción detectada, cerrando el programa...")
        salir_programa = True  # Establecer la bandera para salir
        semaforo_terminacion.set()  # Notificar que se debe cerrar

    # Asegurarse de que el semáforo se libere para que los hilos no se queden bloqueados
    semaforo.release()

    # Esperar a que ambos hilos terminen
    hilo_productor.join()
    hilo_consumidor.join()

    print("Todos los destinos han sido procesados. Programa terminado.")
