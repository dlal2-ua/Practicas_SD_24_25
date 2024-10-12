import time
from confluent_kafka import Producer  
import sqlite3
import sys # Se utiliza para acceder a parámetros y funciones específicas del sistema (en este caso, para acceder a los argumentos de la línea de comandos)


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


# Función para obtener el total de servicios y el primer destino del cliente
def obtener_info_cliente(cliente_id):
    try:
        # Conectarse a la base de datos
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Consulta SQL para obtener el total de servicios y el primer destino
        query_total = '''
        SELECT COUNT(*)
        FROM servicios
        WHERE id = ?;
        '''

        query_destino = '''
        SELECT destino
        FROM servicios
        WHERE id = ?
        LIMIT 1;
        '''

        # Ejecutar la consulta para contar los servicios
        cursor.execute(query_total, (cliente_id,))
        total_servicios = cursor.fetchone()[0]

        # Ejecutar la consulta para obtener el primer destino
        cursor.execute(query_destino, (cliente_id,))
        primer_destino = cursor.fetchone()[0] if total_servicios > 0 else None

        # Cerrar la conexión a la base de datos
        conn.close()

        return total_servicios, primer_destino

    except sqlite3.Error as e:
        print(f"Error al acceder a la base de datos: {e}")
        return None, None



# Función para enviar el destino al tópico de Kafka
def enviar_a_kafka(producer, cliente_id, destino):
    mensaje = f"Cliente {cliente_id} quiere ir a {destino}"             
    print(f"Enviando mensaje: {mensaje}")
    producer.produce('CLIENTES', key=cliente_id, value=mensaje)
    producer.flush()



# Función principal que conecta todo
def main(broker, cliente_id):
    # Obtener el total de servicios y el primer destino del cliente
    total_servicios_cliente, primer_destino = obtener_info_cliente(cliente_id)

    if total_servicios_cliente == 0 or primer_destino is None:
        print(f"El cliente {cliente_id} no tiene destinos.")
        return

    # Mostrar el total de servicios y el primer destino
    print(f"El cliente {cliente_id} tiene {total_servicios_cliente} servicios.")
    print(f"El primer destino del cliente es: {primer_destino}")

    # Configurar el productor Kafka
    producer_config = {
        'bootstrap.servers': broker
    }
    producer = Producer(producer_config)

    # Enviar el primer destino al tópico de Kafka
    enviar_a_kafka(producer, cliente_id, primer_destino)

    # Finalizar
    print(f"El destino '{primer_destino}' ha sido enviado al tópico de Kafka.")


def validar_cliente_id(cliente_id):
    if len(cliente_id) != 1 or not cliente_id.islower():
        print("Error: La ID del cliente debe ser un único carácter en minúscula.")
        sys.exit(1)



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Uso: python {sys.argv[0]} <broker_ip:puerto> <id_cliente>")  # Ejemplo: 127.0.0.1:9092
        sys.exit(1)

    # Obtener parámetros de línea de comando
    broker = sys.argv[1]
    cliente_id = sys.argv[2]

    # Validar que la ID del cliente sea un único carácter en minúscula
    validar_cliente_id(cliente_id)

    # Ejecutar el programa principal
    main(broker, cliente_id)
    time.sleep(4)  # Esperar 4 segundos antes de solicitar el siguiente servicio

