import time
from confluent_kafka import Producer, Consumer, KafkaException
import sys # Se utiliza para acceder a parámetros y funciones específicas del sistema (en este caso, para acceder a los argumentos de la línea de comandos)
import signal
from colorama import Fore, Style, init


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

# Función para verificar si la central está activa
def verificar_central_activa(producer, consumer, cliente_id):
    global salir_programa

    mensaje_central_activa = "Central activa?"
    while not salir_programa:
        print(Fore.YELLOW + "Verificando si la central está activa...")
        print()
        producer.produce('CLIENTES', key=cliente_id, value=mensaje_central_activa)
        producer.flush()

        tiempo_inicio = time.time()
        while time.time() - tiempo_inicio < 15 and not salir_programa:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            mensaje = msg.value().decode('utf-8')

            if mensaje == "Central está operativa":
                print(Fore.GREEN + "Central confirmada como operativa.")
                print()
                return True

        print(Fore.RED + "No se recibió confirmación de la central en 5 segundos. Reintentando...\n")

    return False




# Función para enviar destino al tópico de Kafka y esperar confirmación de taxi asignado
def enviar_destinos_kafka(broker, cliente_id, destinos_cliente):
    global salir_programa

    if not destinos_cliente:
        print(f"El cliente {cliente_id} no tiene destinos y/o no existe.")
        return

    producer = Producer({'bootstrap.servers': broker})
    consumer = Consumer({
        'bootstrap.servers': broker,
        'group.id': f'grupo_consumidor_{cliente_id}',
        'auto.offset.reset': 'latest'
    })

    topic_cliente = ['CENTRAL-CLIENTE', 'TAXI-CLIENTE']
    consumer.subscribe(topic_cliente)


    # Verificar si la central está activa antes de proceder
    if not verificar_central_activa(producer, consumer, cliente_id):
        print(Fore.RED + "Error: No se pudo verificar si la central está operativa. Saliendo...")
        return

    for i, destino in enumerate(destinos_cliente):
        if salir_programa:
            break




        mensaje_enviado = False
        contador_sin_respuesta = 0  # Contador de veces que no se recibe confirmación

        while not mensaje_enviado and not salir_programa:
            # Enviar el destino
            mensaje_ir_destino = f"Cliente '{cliente_id}' quiere ir a {destino}"
            print(mensaje_ir_destino)
            print(f"Esperando asignación de taxi...")

            # Enviar mensaje al tópico 'CLIENTES'
            producer.produce('CLIENTES', key=cliente_id, value=mensaje_ir_destino)
            producer.flush()

            # Esperar asignación de taxi (ASIGNADO)
            tiempo_inicio = time.time()
            tiempo_ultimo_mensaje = time.time()  # Inicializar el temporizador para el mensaje de espera

            while time.time() - tiempo_inicio < 15 and not salir_programa:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    # Cada 10 segundos, imprime un mensaje de espera
                    if time.time() - tiempo_ultimo_mensaje >= 20:
                        contador_sin_respuesta += 1
                        print("No se recibió mensaje, esperando asignación de taxi...")
                        print()
                        tiempo_ultimo_mensaje = time.time()  # Reiniciar el temporizador de mensaje

                    # Si no se recibe respuesta después de 3 intentos, pasar al siguiente destino
                    if contador_sin_respuesta >= 3:
                        print(Fore.YELLOW + f"No se recibió confirmación después de 3 intentos para el destino {destino}. Pasando al siguiente destino...\n")
                        mensaje_enviado = True
                        break
                    continue

                if msg.error():
                    raise KafkaException(msg.error())

                mensaje = msg.value().decode('utf-8')
                print(mensaje)
                
                # Si el mensaje indica que el cliente ya está en servicio
                if mensaje == "YA_ESTAS_EN_SERVICIO":
                    print(Fore.RED + f"El cliente {cliente_id} ya está en un servicio. No se puede solicitar otro servicio.")
                    salir_programa = True  # Cierra el terminal del cliente
                    break
                

                if f"ID:{cliente_id} ASIGNADO" in mensaje:
                    taxi_asignado = mensaje.split('TAXI:')[1]  # Extraer el taxi asignado
                    print()
                    print(Fore.GREEN + f"Confirmación recibida: Taxi {taxi_asignado} asignado")
                    print()
                    print(f"Esperando confirmación de recogida por el {taxi_asignado}...")
                    mensaje_enviado = True
                    break

            if not mensaje_enviado:
                print(Fore.YELLOW + "No se recibió confirmación en 5 segundos. Reintentando...\n")
                time.sleep(1)

        # Esperar confirmación de recogida (IN) o continuar si se recibió "KO"
        contador_sin_respuesta = 0
        tiempo_ultimo_mensaje = time.time()
        while not salir_programa:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                if time.time() - tiempo_ultimo_mensaje >= 40:
                    contador_sin_respuesta += 1
                    print("No se recibió mensaje, esperando confirmación de recogida...")
                    print()
                    tiempo_ultimo_mensaje = time.time()

                if contador_sin_respuesta >= 3:
                    print(Fore.YELLOW + f"No se recibió confirmación de recogida después de 3 intentos para el destino {destino}. Pasando al siguiente destino...\n")
                    break
                continue

            if msg.error():
                raise KafkaException(msg.error())

            mensaje = msg.value().decode('utf-8')

            if mensaje == f"ID:{cliente_id} IN":
                print(Fore.GREEN + f"Confirmación recibida: Cliente recogido por {taxi_asignado}, yendo a {destino}")
                print()
                print(f"Esperando confirmación de recogida por el {taxi_asignado}...")
                mensaje_enviado = True
                break

            if mensaje == f"ID:{cliente_id} KO":
                print(Fore.RED + f"Error: Fracaso en la recogida del cliente '{cliente_id}' por {taxi_asignado}.")
                print(Fore.GREEN + "Saliendo de este destino y continuando con el siguiente...\n")
                break

        # Procesar confirmación de llegada (OK)
        contador_sin_respuesta = 0
        tiempo_ultimo_mensaje = time.time()
        while not salir_programa:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                if time.time() - tiempo_ultimo_mensaje >= 40:
                    contador_sin_respuesta += 1
                    print("No se recibió mensaje, esperando confirmación de llegada al destino...")
                    print()
                    tiempo_ultimo_mensaje = time.time()

                if contador_sin_respuesta >= 3:
                    print(Fore.YELLOW + f"No se recibió confirmación de llegada después de 3 intentos para el destino {destino}. Pasando al siguiente destino...\n")
                    break
                continue

            if msg.error():
                raise KafkaException(msg.error())

            mensaje = msg.value().decode('utf-8')

            if mensaje == f"ID:{cliente_id} OK":
                print(Fore.GREEN + f"Confirmación recibida: Cliente llegó a {destino}")
                print()
                break

            if mensaje == f"ID:{cliente_id} KO":
                print(Fore.RED + f"Error: Fracaso en la llegada del cliente '{cliente_id}' a {destino}.")
                print(Fore.GREEN + "Saliendo de este destino y continuando con el siguiente...\n")
                break

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
