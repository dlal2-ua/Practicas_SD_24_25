
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


# **Cosas que implementar (Práctica 2)**

## **1. Comunicación entre componentes**
- **Comunicar EC_CTC con la central.**
- **Añadir módulo EC_CTC:**
  - Comunicación mediante API REST.
- **Añadir EC_Registry:**
  - Registrar nuevos taxis y dar de baja a los existentes.
  - Comunicación entre taxis y Registry mediante API REST.
- **Crear un Frontend:**
  - Mostrar la información del sistema de forma visual.

---

## **2. Seguridad**
- **Autenticación entre Taxi y Registry.**
- **Auditoría de eventos en la central (SIEM):**
  - **Logs generados con la siguiente información:**
    - Fecha y hora del evento.
    - Origen del evento (IP del Taxi o del Usuario).
    - Acción realizada (autenticaciones, incidencias, bloqueos, errores, etc.).
    - Parámetros o descripción detallada del evento.
- **Cifrado de datos:**
  - Implementación de un canal seguro entre la Central y los Taxis:
    - **Cifrado asimétrico:** Opciones como SSL/TLS, autenticación SASL o ACL mediante Kafka.

---

## **3. Central**
- **Consumo de API REST del gestor de tráfico de la ciudad.**
- **Autenticación entre EC_Central y los Taxis:**
  - Opcionalmente implementar una API REST adicional.
- **Cifrado en el canal de comunicación:**
  - Utilizar un enfoque asimétrico.
  - **Opciones de Kafka:** 
    - Cifrado SSL/TLS.
    - Autenticación SSL o SASL.
    - Autenticación ACL.
- **Registro de auditoría:**
  - Generar logs con los eventos relevantes.

---

## **4. API_Central**
- **Crear una API REST:**
  - Soporte para métodos como `GET`, `PUT`, `DELETE`.
  - Permitir a cualquier componente externo consultar el estado de:
    - Taxis.
    - Usuarios.
    - Mapa en curso.
- **Información proporcionada al Frontend:**
  - Datos sobre taxis, usuarios, mensajes de error, estado de EC_CTC, etc.

---

## **5. EC_Registry**
- **Funcionalidad limitada a alta y baja de taxis:**
  - Antes de autenticarse o prestar servicio, los taxis deben:
    - Registrarse con su ID (alta).
    - Darse de baja según sea necesario.
  - **Mensajes de error:** Acciones realizadas sin registro previo deben generar un error.
- **Comunicación segura:**
  - Utilizar API REST sobre canales seguros (HTTPS, SSL, RSA, etc.).

---

## **6. Base de Datos**
- **Acceso compartido:**
  - Tanto la Central como el Registry tendrán acceso a la base de datos.

---

## **7. Digital Engine (EC_DE)**
- **Menú funcional:**
  - Opciones para conectarse y registrarse en EC_Registry.
- **Implementación:**
  - Proceso gestionado mediante una API.
- **Seguridad:**
  - Comunicación y autenticación seguras.

---

## **8. City Traffic Control (EC_CTC)**
- **Respuestas basadas en condiciones:**
  - **`OK`**: Si se puede circular.
  - **`KO`**: Si no se puede circular y los taxis deben volver a base.
- **Menú interactivo:**
  - Permitir cambiar la ciudad en cualquier momento sin necesidad de reiniciar el sistema.
- **Condiciones de circulación:**
  - Consultar la temperatura de la ciudad desde el servidor del clima:
    - Si la temperatura > 0°C: **`KO`**.
    - Si la temperatura ≤ 0°C: **`OK`**.
  



## Instalar Flask
```
pip install flask
```































