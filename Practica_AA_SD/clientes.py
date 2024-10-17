import time
import threading
from confluent_kafka import Producer, Consumer, KafkaException
import sys # Se utiliza para acceder a parámetros y funciones específicas del sistema (en este caso, para acceder a los argumentos de la línea de comandos)
import signal
from colorama import Fore, Style, init



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

"""
Cómo funciona:
    El cliente envía un mensaje de solicitud para ir a un destino.
    Espera la confirmación de la central que indica que el cliente fue recogido.
    Después de ser recogido, envía un mensaje indicando que llegó al destino.
    Espera la confirmación de que la central recibió el mensaje de llegada.
    Se repite este ciclo para cada destino hasta que todos hayan sido procesados.
"""

# Inicializar colorama (solo es necesario en Windows)
init(autoreset=True)

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

    for i, destino in enumerate(destinos_cliente):
        if salir_programa:
            break

        # Enviar el destino
        mensaje_ir_destino = f"Cliente '{cliente_id}' quiere ir a {destino}"
        print(mensaje_ir_destino)
        print(f"Esperando confirmación de recogida...")
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
            
            # Manejar error si se recibe "KO"
            if mensaje == f"ID:{cliente_id} KO":
                print()
                print(Fore.RED + f"Error: Fracaso en la recogida del cliente '{cliente_id}' para el destino {destino}.")
                print(Fore.GREEN + f"Saliendo de este destino y continuando con el siguiente...")
                print()
                break

            if mensaje == f"ID:{cliente_id} IN":
                print()
                print(Fore.GREEN + f"Confirmación recibida: Cliente recogido, yendo a {destino}")
                print("Esperando confirmación de llegada...")
                break

        # Si se ha recibido un "KO", pasar al siguiente destino
        if mensaje == f"ID:{cliente_id} KO":
            continue

        # Enviar mensaje de llegada
        #mensaje_llegada = f"Cliente '{cliente_id}' ha llegado a {destino}"
        #producer.produce('CLIENTES', key=cliente_id, value=mensaje_llegada)
        #producer.flush()

        # Esperar la confirmación de llegada (OK)
        while not salir_programa:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            mensaje = msg.value().decode('utf-8')
            
            # Manejar error si se recibe "KO", tanto por si no hay taxis disponibles como si no se ha podido llegar al destino
            if mensaje == f"ID:{cliente_id} KO":
                print()
                print(Fore.RED + f"Error: Fracaso en la llegada del cliente '{cliente_id}' a {destino}.")
                print(Fore.GREEN + f"Saliendo de este destino y continuando con el siguiente...")
                print()
                break

            if mensaje == f"ID:{cliente_id} OK":
                print()
                print(Fore.GREEN + f"Confirmación recibida: Cliente llegó a {destino}")
                print()
                break

        # Si se ha recibido un "KO", pasar al siguiente destino
        if mensaje == f"ID:{cliente_id} KO":
            continue

        # Si no es el último destino, esperar 4 segundos antes de procesar el siguiente destino
        if i < len(destinos_cliente) - 1 and not salir_programa:
            print("Esperando 4 segundos antes de ir al siguiente destino...")
            print()
            time.sleep(4)

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
        print(Fore.YELLOW + "Todos los destinos han sido procesados...")
        print() 
