from kafka import KafkaProducer, KafkaConsumer
from threading import Thread
import time

# Función para actuar como consumidor
def consume_messages():
    consumer = KafkaConsumer('CLIENTES', bootstrap_servers='127.0.0.1:9092')
    for message in consumer:
        print(f"Mensaje recibido: {message.value.decode('utf-8')}")

# Función para actuar como productor
def produce_messages():
    producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
    while True:
        mensaje = input("Ingresa un mensaje para enviar: ")
        producer.send('CENTRAL-CLIENTE', mensaje.encode('utf-8'))
        producer.flush()
        time.sleep(1)


# Crear hilos para ejecutar productor y consumidor simultáneamente
if __name__ == "__main__":
    consumer_thread = Thread(target=consume_messages)
    producer_thread = Thread(target=produce_messages)

    # Iniciar ambos hilos
    consumer_thread.start()
    producer_thread.start()

    # Esperar que ambos hilos terminen (esto ocurre cuando terminen de ejecutarse sus loops)
    consumer_thread.join()
    producer_thread.join()


