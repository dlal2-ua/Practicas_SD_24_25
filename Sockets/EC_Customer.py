import time
import threading
from confluent_kafka import Producer, Consumer, KafkaException
import sys # Se utiliza para acceder a parámetros y funciones específicas del sistema (en este caso, para acceder a los argumentos de la línea de comandos)
import signal


# Variable global para controlar la ejecución de los hilos
salir_programa = False
semaforo_terminacion = threading.Event()  # Señal para indicar cuando todos los destinos han sido procesados

# Manejador de la señal SIGINT para detener el programa con Ctrl+C
def manejar_ctrl_c(signal, frame):
    global salir_programa
    print("\nCtrl+C detectado, cerrando el programa...")
    salir_programa = True
    semaforo_terminacion.set()  # Asegurarse de que el programa se cierre


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

        # Si no se encontraron destinos para el cliente, devolver lista vacía
        if not destinos:
            return []

        return destinos

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

    # Enviar destinos uno por uno, esperando confirmación de OK antes de enviar el siguiente
    for i, destino in enumerate(destinos_cliente):
        if salir_programa:
            break

        enviar_a_kafka(producer, cliente_id, destino)

        # Para destinos intermedios, mantener el mensaje habitual
        print(f"Esperando confirmación de la central para el destino '{destino}'...")
        semaforo.acquire()  # Bloquear hasta recibir la confirmación del destino actual

        if i == len(destinos_cliente) - 1:
            semaforo_terminacion.set()
        
        print()  # Salto de línea para mejorar la legibilidad en la salida


# Hilo Consumidor que escucha el tópico 'CENTRAL-CLIENTE' y procesa mensajes en formato "ID:<cliente_id> OK"
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
    topic_cliente = f'CENTRAL-CLIENTE'
    consumer.subscribe([topic_cliente])


    try:
        while not salir_programa:
            msg = consumer.poll(timeout=0.2)  # Esperar por mensajes durante 0.2 segundos
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Procesar el mensaje en formato "ID:<cliente_id> OK"
                mensaje = msg.value().decode('utf-8')

                # Verificar si el mensaje sigue el formato esperado: "ID:<cliente_id> OK"
                if mensaje.startswith(f"ID:{cliente_id} OK"):
                    if not semaforo_terminacion.is_set():
                        # No es el último destino, continuar con el flujo normal
                        print(f"Cliente '{cliente_id}' recibió OK")
                        print()  # Salto de línea para mejorar la legibilidad en la salida
                        time.sleep(4)  # Esperar 4 segundos antes de enviar el siguiente destino
                        semaforo.release()  # Liberar el semáforo para que el productor envíe el siguiente destino
                    else:
                        break  # Terminar la espera, ya que es el último destino
                    
    except KafkaException as e:
        print(f"Error en el consumidor: {e}")
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
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

    # Esperar a que se completen todos los destinos
    semaforo_terminacion.wait()  # Esperar hasta que todos los destinos hayan sido enviados y confirmados

    # Establecer la bandera de salir para que los hilos terminen
    salir_programa = True

    # Asegurarse de que el semáforo se libere para que los hilos no se queden bloqueados
    semaforo.release()

    # Esperar a que ambos hilos terminen
    hilo_productor.join()
    hilo_consumidor.join()

    print("Todos los destinos han sido procesados. Programa terminado.")
