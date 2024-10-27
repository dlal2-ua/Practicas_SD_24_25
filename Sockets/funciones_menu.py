from kafka import KafkaConsumer,KafkaProducer 

def para(broker,id):
    producer = KafkaProducer(bootstrap_servers=broker)
    mensaje = str(id)  + ",Parar"
    producer.send('CENTRAL-TAXI', key=str(id).encode('utf-8'), value=mensaje.encode('utf-8'))
    producer.flush()

def reanudar(broker,id):
    producer = KafkaProducer(bootstrap_servers=broker)
    mensaje = str(id)  + ",Seguir"
    producer.send('CENTRAL-TAXI', key=str(id).encode('utf-8'), value=mensaje.encode('utf-8'))
    producer.flush()

