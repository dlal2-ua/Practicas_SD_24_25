MEMORIA

Proceso de realización:
  -Crear la central
    · Parte del codigo que gestione la conectividad central-taxi y central-cliente (kafka)
    · Que imprima el mapa y tabla de información
    · Autentificar los taxis (sockets)
  
  -Crear los taxis
    · Posición inicial de todos en la casilla [1,1]
    ·
  -Crear los clientes
   · Todos lo clientes pueden leer todos los mensajes de kafka
  
  -Crear la base de datos
    
  -Crear tabla de información y el mapa
    · Poner los colores correspodiente y de forma dinamica
    · Que al entrar o salir un taxi se vea reflejado en la tabla

En relacion con la base de datos [BBDD]:
-Hemos decidido hacer una base de datos usando SQLite dado que en comparación con el fichero, el manejo de datos con sql es mucho más sencillo y fácil de obtener la información
-Hemos decidido estos campos para la base de datos:
·El id del taxi (uniques)
·El Destino (char)
·El estado (booleano)
    - Cuando el taxi está ocupado tomará el valor de 0
    - Cuando el taxi está libre tomará el valor de 1
·La coordenada (int)



-Coordenada X
-Coordenada Y

En relacion al taxi:
-Hemos decidido que el digital engine sera el servidor por lo tanto en los argumentos del digital engine no vamos a poner que esten ni la ip ni el puerto del servidor,
con lo que el servidor no hace falta que conozca la ip ni el puerto del cliente.




%KAFKA_HOME%\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties

%KAFKA_HOME%\bin\windows\kafka-server-start.bat .\config\server.properties

pip install git+https://github.com/dpkp/kafka-python.git



bin\windows\kafka-topics.bat --create --topic SD --bootstrap-server localhost:9092
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def get_local_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ip_info = addresses[netifaces.AF_INET][0]
            ip_address = ip_info['addr']
            if not ip_address.startswith("127."):  # Ignorar la dirección loopback
                return ip_address
    return "No se encontró una dirección IP válida.

