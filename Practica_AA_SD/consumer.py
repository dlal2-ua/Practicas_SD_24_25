from confluent_kafka import Consumer, KafkaError

# Configuración del consumidor
conf = {
    'bootstrap.servers': 'localhost:9092',  # Dirección del servidor Kafka
    'group.id': 'mygroup',  # Identificador del grupo de consumidores
    'auto.offset.reset': 'earliest'  # Leer desde el principio si no se encuentran offsets previos
}

# Crea una instancia del consumidor con la configuración dada
consumer = Consumer(**conf)

# Suscribirse al tópico 'ALMENDRAS'
consumer.subscribe(['ALMENDRAS'])

try:
    # Bucle infinito para consumir mensajes
    while True:
        # Espera por un mensaje durante 1 segundo
        msg = consumer.poll(1.0)
        
        # Si no hay mensaje, continúa esperando
        if msg is None:
            continue
        
        # Si hay un error en el mensaje
        if msg.error():
            # Si es el final de la partición, lo imprime y continúa
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"Fin de la partición {msg.partition()}")
            else:
                # Si es otro error, lo imprime
                print(f"Error del consumidor: {msg.error()}")
            continue
        
        # Si no hay errores, imprime el mensaje recibido
        print(f"Recibido mensaje: {msg.value().decode('utf-8')} en el topic {msg.topic()}")
        
except KeyboardInterrupt:
    # Manejar la interrupción del teclado (Ctrl + C)
    print("Interrupción recibida, cerrando consumidor...")

finally:
    # Cerrar el consumidor para liberar recursos
    consumer.close()
    print("Consumidor cerrado.")
