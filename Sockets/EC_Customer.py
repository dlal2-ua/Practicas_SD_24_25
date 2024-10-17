import time
import threading
from confluent_kafka import Producer, Consumer, KafkaException
import sys # Se utiliza para acceder a parámetros y funciones específicas del sistema (en este caso, para acceder a los argumentos de la línea de comandos)
import signal



"""
Cómo funciona:
    El cliente envía un mensaje de solicitud para ir a un destino.
    Espera la confirmación de la central que indica que el cliente fue recogido.
    Después de ser recogido, envía un mensaje indicando que llegó al destino.
    Espera la confirmación de que la central recibió el mensaje de llegada.
    Se repite este ciclo para cada destino hasta que todos hayan sido procesados.
"""

# Variable global para controlar la ejecución del programa
salir_programa = False

# Manejador de la señal SIGINT para detener el programa con Ctrl+C
def manejar_ctrl_c(signal, frame):
    global salir_programa
    print("\nCtrl+C detectado, cerrando el programa...")
    salir_programa = True

# Función para obtener todos los destinos del cliente desde un fichero
def obtener_info_cliente(cliente_id, fichero):
    destinos = []
    try:
        with open(fichero, 'r') as f:
            lineas = f.readlines()

        cliente_encontrado = False
        for linea in lineas:
            linea = linea.strip()
            if not cliente_encontrado:
                if linea == cliente_id:
                    cliente_encontrado = True
            else:
                if linea.isupper():
                    destinos.append(linea)
                elif linea.islower():
                    break
        return destinos
    except FileNotFoundError:
        print(f"Error: El fichero '{fichero}' no existe.")
        return []
    except Exception as e:
        print(f"Error al procesar el fichero: {e}")
        return []

# Función para enviar destino al tópico de Kafka y esperar confirmación
def enviar_destinos_kafka(broker, cliente_id, destinos_cliente):
    global salir_programa

    if not destinos_cliente:
        print(f"El cliente {cliente_id} no tiene destinos y/o no existe.")
        return

    producer = Producer({'bootstrap.servers': broker})
    consumer = Consumer({
        'bootstrap.servers': broker,
        'group.id': f'grupo_consumidor_{cliente_id}',
        'auto.offset.reset': 'earliest'
    })

    topic_cliente = 'CENTRAL-CLIENTE'
    consumer.subscribe([topic_cliente])

    for destino in destinos_cliente:
        if salir_programa:
            break

        # Enviar el destino
        mensaje_ir_destino = f"Cliente '{cliente_id}' quiere ir a {destino}"
        print(mensaje_ir_destino)
        producer.produce('CLIENTES', key=cliente_id, value=mensaje_ir_destino)
        producer.flush()

        # Esperar la confirmación de recogida (IN)
        while not salir_programa:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            mensaje = msg.value().decode('utf-8')
            if mensaje == f"ID:{cliente_id} IN":
                print(f"Confirmación recibida: Cliente recogido, yendo a {destino}")
                break

        # Enviar mensaje de llegada
        mensaje_llegada = f"Cliente '{cliente_id}' ha llegado a {destino}"
        producer.produce('CLIENTES', key=cliente_id, value=mensaje_llegada)
        producer.flush()

        # Esperar la confirmación de llegada (OK)
        while not salir_programa:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            mensaje = msg.value().decode('utf-8')
            if mensaje == f"ID:{cliente_id} OK":
                print(f"Confirmación recibida: Cliente llegó a {destino}")
                print()
                break

    consumer.close()

# Validar que la ID del cliente sea un único carácter en minúscula
def validar_cliente_id(cliente_id):
    if len(cliente_id) != 1 or not cliente_id.islower():
        print("Error: La ID del cliente debe ser un único carácter en minúscula.")
        sys.exit(1)

# Función principal
if __name__ == "__main__":
    signal.signal(signal.SIGINT, manejar_ctrl_c)

    if len(sys.argv) != 4:
        print(f"Uso: python {sys.argv[0]} <broker_ip:puerto> <id_cliente> <fichero>")
        sys.exit(1)

    broker = sys.argv[1]
    cliente_id = sys.argv[2]
    fichero = sys.argv[3]

    validar_cliente_id(cliente_id)
    destinos_cliente = obtener_info_cliente(cliente_id, fichero)

    enviar_destinos_kafka(broker, cliente_id, destinos_cliente)

    if not salir_programa:
        print("Todos los destinos han sido procesados. Programa terminado.")
        print() 
