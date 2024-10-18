import sqlite3
from kafka import Consumer, KafkaError
from funciones_generales import update_datos_taxi, leer_existencia_taxi, insert_datos_taxi


# =================================================================================================
"""

# Configuración del consumidor Kafka
conf = {
    'bootstrap.servers': 'localhost:9092',  # Dirección del servidor Kafka
    'group.id': 'mygroup',  # Grupo de consumidores
    'auto.offset.reset': 'earliest'  # Leer desde el principio si no se encuentran offsets previos
}

# Crear una instancia del consumidor Kafka
consumer = Consumer(**conf)

# Suscribirse al tópico 'ALMENDRAS' donde los taxis envían sus datos
consumer.subscribe(['ALMENDRAS'])

try:
    # Bucle infinito para consumir mensajes de Kafka
    while True:
        # Esperar por un mensaje durante 1 segundo
        msg = consumer.poll(1.0)
        
        # Si no hay mensaje, continuar esperando
        if msg is None:
            continue
        
        # Si hay un error en el mensaje
        if msg.error():
            # Si es el final de la partición, imprimirlo y continuar
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"Fin de la partición {msg.partition()}")
            else:
                # Si es otro error, imprimir el error
                print(f"Error del consumidor: {msg.error()}")
            continue
        
        # Si no hay errores, procesar el mensaje recibido
        print(f"Recibido mensaje: {msg.value().decode('utf-8')} en el topic {msg.topic()}")
        
        # Aquí asumimos que el mensaje está formateado como "id,destino,estado,coordX,coordY"
        # Ejemplo: "1,Madrid,LIBRE,10.123,20.456"
        datos_taxi = msg.value().decode('utf-8').split(',')
        print(f"Datos del taxi: {datos_taxi}")
        # Suponiendo que 'datos_taxi' es una lista de cadenas
        datos_taxi = datos_taxi[0].split()  # Divide la cadena por espacios
        
        id = int(datos_taxi[0])  # Esto ahora debería funcionar si el primer elemento es un número
        destino_inicial = str(datos_taxi[1])
        destino_final = str(datos_taxi[2])
        estado = datos_taxi[3]
        coordX = float(datos_taxi[4])
        coordY = float(datos_taxi[5])

        if(leer_existencia_taxi(id) == 0):
            print("El taxi no existe en la base de datos")

        # Insertar los datos en la base de datos
        insert_datos_taxi(id, destino_inicial, destino_final, estado, coordX, coordY)
        
        
except KeyboardInterrupt:
    # Manejar la interrupción del teclado (Ctrl + C)
    print("Interrupción recibida, cerrando consumidor...")

finally:
    # Cerrar el consumidor para liberar recursos
    consumer.close()
    print("Consumidor cerrado.")

"""

# =================================================================================================



# Configuración del consumidor Kafka
conf = {
    'bootstrap.servers': 'localhost:9092',  # Dirección del servidor Kafka
    'group.id': 'mygroup',  # Grupo de consumidores
    'auto.offset.reset': 'earliest'  # Leer desde el principio si no se encuentran offsets previos
}

# Crear una instancia del consumidor Kafka
consumer = Consumer(**conf)

# Suscribirse a múltiples tópicos
consumer.subscribe(['CLIENTES', 'ALMENDRAS'])

try:
    # Bucle infinito para consumir mensajes de Kafka
    while True:
        # Esperar por un mensaje durante 1 segundo
        msg = consumer.poll(1.0)
        
        # Si no hay mensaje, continuar esperando
        if msg is None:
            continue
        
        # Si hay un error en el mensaje
        if msg.error():
            # Si es el final de la partición, imprimirlo y continuar
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"Fin de la partición {msg.partition()}")
            else:
                # Si es otro error, imprimir el error
                print(f"Error del consumidor: {msg.error()}")
            continue
        
        # Si no hay errores, procesar el mensaje recibido
        if msg.topic() == 'CLIENTES':
            print("-" * 50)  # Línea separadora para el tópico CLIENTES
        else:
            print("=" * 50)  # Línea separadora diferente para otros tópicos

        print(f"Recibido mensaje: {msg.value().decode('utf-8')} en el topic {msg.topic()}")

        if msg.topic() == 'CLIENTES':
            print("-" * 50)  # Línea separadora para el tópico CLIENTES
        else:
            print("=" * 50)  # Línea separadora diferente para otros tópicos
        
except KeyboardInterrupt:
    # Manejar la interrupción del teclado (Ctrl + C)
    print("Interrupción recibida, cerrando consumidor...")

finally:
    # Cerrar el consumidor para liberar recursos
    consumer.close()
    print("Consumidor cerrado.")

