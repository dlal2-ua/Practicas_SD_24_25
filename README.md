
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
   - 

   - Seguridad
           - Autentificar entre taxi y registry
           - Auditoria de eventos de central
           - Cifrado de datos entre central y taxis
   - Central
      - Consumo de API_rest de un gestor de tráfico de la ciudad
      - 

## Instalar Flask
```
pip install flask
```































