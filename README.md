MEMORIA

Pasos para despliegue de la practica en 3 maquinas (1º Central, 2º Clientes y kafka, 3º Taxis):
  - 1º Central:
    · Cambiar la variable 'SERVER' por la ip de esta maquina
    · En los argumentos poner la ip de la maquina donde esta ejecutado kafka
    
  - 2º Clientes y kafka:
    · Meter en el disco C la carpeta de kafka -> entrar en config -> abrir el archivo server.properties y
          > Sustituir la linea donde pone "*listener=PLAINTEXT://localhost:9092* por "*listener=PLAINTEXT://LA IP DE LA MAQUINA:9092*
          > Sustituir la linea donde pone "*advertised.listener=PLAINTEXT://localhost:9092* por "*advertised.listener=PLAINTEXT://LA IP DE LA MAQUINA:9092*     
    · Abrir dos cmd y hacer 'cd ..' hasta llegar a :/C, y meterse en la carpeta de kafka con este comando 'cd <nombre_carpeta_kafka>
    · Después en un cmd ejecutar PRIMERO: **bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties** y en el otro cmd ejecutar: **bin\windows\kafka-server-start.bat .\config\server.properties**
    . Hecho esto, hay que meterse en la carpeta de sockets, y ejecutar: **python EC_Customer.py <ip de la maquina>:9092 <id cliente> <nombre_txt_servicios>**
    
  - 3º Taxis
    · Se tendrán que abrir dos terminales por cada taxi que se quiera desplegar (una para el taxi, y otra para el sensor)
    . En ambas terminales habrá que entrar en la carpeta sockets:
        > En una ejecutar este comando: python EC_DE.py <IP de la maquina de la central> <Puerto de la central> <Ip del broker> <ID del taxi>
        > En otra ejecutar este comando: python EC_S.py <IP local de la maquina> <Puerto del EC_DE>
        

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


