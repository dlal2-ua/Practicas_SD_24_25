import time
from confluent_kafka import Producer  # Importa la librería Confluent Kafka para el productor
from faker import Faker  # Faker es una librería para generar datos falsos
import sqlite3


""""
# Configuración del productor
conf = {
    'bootstrap.servers': '127.0.0.1:9092'  # Dirección del servidor Kafka, en este caso localhost
}


# Crea una instancia del productor con la configuración anterior
producer = Producer(**conf)
fake = Faker()  # Instancia para generar datos falsos (nombres en este caso)

# Función que actúa como callback para verificar si el mensaje fue entregado exitosamente o no
def delivery_report(err, msg):
    #Callback que informa si el mensaje fue enviado exitosamente o no.
    if err is not None:
        print(f"Error enviando el mensaje: {err}")  # Si hay un error, lo imprime
    else:
        print(f"Mensaje enviado a {msg.topic()} [{msg.partition()}]")  # Muestra el éxito de la entrega

# Enviar 10 mensajes con nombres falsos
for _ in range(10):  # Bucle para enviar 10 mensajes
    name = fake.name()  # Genera un nombre falso
    # Produce un mensaje al topic 'PLAYERS', con clave 'key' y el nombre como valor codificado en UTF-8
    producer.produce('ALMENDRAS', key='key', value=name.encode('utf-8'), callback=delivery_report)
    producer.poll(0)  # Procesa la cola de entrega de mensajes
    print(f"Produciendo: {name}")  # Imprime el nombre que se está enviando
    time.sleep(0.001)  # Espera un pequeño intervalo de tiempo entre mensajes

# Asegura que todos los mensajes pendientes sean enviados antes de cerrar el productor
producer.flush()
print('***THE END***')  # Mensaje final para indicar que el proceso ha terminado


#====================================================================

"""
import time
from confluent_kafka import Producer  # Importa la librería Confluent Kafka para el productor

# Configuración del productor
conf = {
    'bootstrap.servers': '127.0.0.1:9092'  # Dirección del servidor Kafka, en este caso localhost
}

# Crea una instancia del productor con la configuración anterior
producer = Producer(**conf)

# Función que actúa como callback para verificar si el mensaje fue entregado exitosamente o no
def delivery_report(err, msg):
    """"""
    if err is not None:
        print(f"Error enviando el mensaje: {err}")  # Si hay un error, lo imprime
    else:
        print(f"Mensaje enviado a {msg.topic()} [{msg.partition()}]")  # Muestra el éxito de la entrega

# Bucle infinito para permitir el envío de nombres manualmente
while True:
    # Solicita al usuario ingresar un nombre
    name = input("Ingresa un nombre (o escribe 'salir' para terminar): ")
    
    # Verifica si el usuario quiere salir
    if name.lower() == 'salir':
        break
    
    # Produce un mensaje al topic 'ALMENDRAS', con clave 'key' y el nombre como valor codificado en UTF-8
    producer.produce('ALMENDRAS', key='key', value=name.encode('utf-8'), callback=delivery_report)
    producer.poll(0)  # Procesa la cola de entrega de mensajes
    print(f"Produciendo: {name}")  # Imprime el nombre que se está enviando
    time.sleep(0.001)  # Espera un pequeño intervalo de tiempo entre mensajes

# Asegura que todos los mensajes pendientes sean enviados antes de cerrar el productor
producer.flush()
print('***THE END***')  # Mensaje final para indicar que el proceso ha terminado

#====================================================================
