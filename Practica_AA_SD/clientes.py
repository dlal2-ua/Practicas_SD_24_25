import time
from confluent_kafka import Producer  
import sqlite3

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

# Configuración del productor
conf = {
    'bootstrap.servers': '127.0.0.1:9092'  # Dirección del servidor Kafka, en este caso localhost
}

# --- Función principal ---
def main(broker, cliente_id, archivo_servicios):
    # Leer los servicios a solicitar
    servicios = leer_servicios(archivo_servicios)

    # Configurar el productor Kafka
    producer_config = {
        'bootstrap.servers': broker,
    }
    producer = Producer(producer_config)

    # Configurar el consumidor Kafka (para escuchar confirmaciones)
    consumer_config = {
        'bootstrap.servers': broker,
        'group.id': f'EC_Confirmation_{cliente_id}',
        'auto.offset.reset': 'earliest',
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([f'EC_Confirmation_{cliente_id}'])

    # Solicitar taxis por cada servicio del archivo
    for destino in servicios:
        solicitar_taxi(producer, cliente_id, destino)

        # Escuchar confirmación de que el servicio ha concluido
        if escuchar_confirmacion(consumer):
            print(f"Servicio hacia {destino} concluido.")
        
        # Esperar 4 segundos antes de solicitar el próximo servicio
        time.sleep(4)

    # Cerrar conexiones
    producer.flush()
    consumer.close()
    print("Todos los servicios solicitados han sido procesados.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Uso: python {sys.argv[0]} <broker> <id_cliente> <archivo_servicios>")
        sys.exit(1)

    broker = sys.argv[1]
    cliente_id = sys.argv[2]
    archivo_servicios = sys.argv[3]

    main(broker, cliente_id, archivo_servicios)