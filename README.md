
## KAFKA
```
%KAFKA_HOME%\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```
```
%KAFKA_HOME%\bin\windows\kafka-server-start.bat .\config\server.properties
```
```
pip install git+https://github.com/dpkp/kafka-python.git
```

## Crear un topico en kafka
```
bin\windows\kafka-topics.bat --create --topic SD --bootstrap-server localhost:9092
```
## Ver los topicos de kafka
```
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```

winget install --id Git.Git -e --source winget


# MEMORIA

## Pasos para despliegue de la práctica en 3 máquinas

### 1º Central
- Cambiar la variable `SERVER` por la IP de esta máquina.
- En los argumentos, poner la IP de la máquina donde está ejecutado Kafka.

### 2º Clientes y Kafka
1. Meter en el disco C la carpeta de Kafka.
2. Entrar en `config` y abrir el archivo `server.properties`.
   - Sustituir la línea:
     ```
     listener=PLAINTEXT://localhost:9092
     ```
     por:
     ```
     listener=PLAINTEXT://LA IP DE LA MAQUINA:9092
     ```
   - Sustituir la línea:
     ```
     advertised.listener=PLAINTEXT://localhost:9092
     ```
     por:
     ```
     advertised.listener=PLAINTEXT://LA IP DE LA MAQUINA:9092
     ```

3. Abrir dos terminales (cmd) y hacer `cd ..` hasta llegar a `C:\`, luego entrar en la carpeta de Kafka:
   ```bash
   cd <nombre_carpeta_kafka>


# Cosas que implementar (PRACTICA 2)
   - Comunicar EC_CTC con la central
   - Añadir modulo EC_CTC (se comunica via API)
   - Añadir EC_Registry (registrar nuevo taxi y dar de baja) (Comunica con los taxis via API REST)
   - Crear front

   - Seguridad
           - Autentificar entre taxi y registry
           - Auditoria de eventos de central
           - Cifrado de datos entre central y taxis
   - Central
      - Consumo de API_rest de un gestor de tráfico de la ciudad
      - Implementación de la autenticación entre EC_Central y los Taxis  (se puede implementar una API rest entre Taxi y Central si queremos (Opcional))
      - Implementación de cifrado en el canal entre EC_Central y los Taxis (Hacerlo asimetrico) (Kafka tiene 3 cifrados [Cifrado SSL/TLS, Autentificacion SSL o SASL, Autentifiacion ACL] SE VALORA POSITIVAMENTE)
      - Registro de auditoria (Hacer unos logs) (SIEM (Security Information and Event Management))
         · Fecha y hora
         · Quién y desde dónde se produce el evento: IP de la máquina que genera el evento (ej. IP del taxi, IP del Usuario)
         · Qué acción se realiza: Autenticación o intentos de autenticación fallidos o no, Incidencias durante el servicio, cambio de la situación del tráfico, usuarios o taxis bloqueados, errores, etc.
         · Parámetros o descripción del evento
      
   - API_Central
      - Crear un API_Rest con los metodos (GET, PUT, DELETE, ....) (Permitirá desde cualquier componente externo consultar el estado de los Taxis, Usuarios y el mapa en curso)
      - Debe pasar al front toda la información de lo que pasa en la práctica (taxis, usuarios, mensajes de error, estado del CTC, etc).
        
   - EC_Registry
      - Solo dispondrá de las opciones de alta y baja de un taxi
      - Antes de autenticación y antes de prestar un servicio, tienen que hacer una petición para darse de alta/baja según su ID
      - Si hace cualquier cosas sin previo registro, mostrar mensaje de error

   - Comuniación entre taxis y su registro se hará por API_Rest
   - Esta comunicación se hará en un canal seguro (HTTPS, SSL, RSA,...)

   - Base de Datos:
      · Pueden acceder tanto Central como Registry

   - Digital Engine (EC_DE)
      · En un menú
           · Para poder conectarse y registrarse a EC_Registry
           · Proceso implementado en una API
           · Conexion y autentificación de manera segura

   - City Traffic Control (EC_CTC)
      - Devuelve OK en caso de que se pueda circular
      - Devuelve KO en caso de que NO se pueda circular y los Taxis deban volver a base
      - Hay que implementar un MENÚ para introducir la ciudad donde se presta el servicio
            · Se conectará al servidor del clima y se le solicitará esta ciudad
            · Si la temperatura > 0 grados, EC_CTC devolverá KO a la central, sino OK
            ```markdown
           <span style="color:red">IMPORTANTE</span>
           <span style="color:yellow"> La ciudad podrá ser cambiada en cualquier momento con el menú, sin necesidad de reiniciar ninguna parte del sistema. </span>
            ```


## Instalar Flask
```
pip install flask
```































