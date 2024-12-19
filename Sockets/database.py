# Crear una tabla llamada 'taxis' con las columnas 'id', 'destino_a_cliente', 'destino_a_final', 'estado', 'coordX' y 'coordY'
#He añadido destino a cliente (para que salga en pantalla que va en direccion cliente) y destino a final (cuando haya recogido al cliente, en la tabla aparecerá el destino final)
#La central pasará toda la información a los taxis sobre el cliente, y el taxi ya tendra tanto la informacion para recoger como para dejar al cliente

import mysql.connector

# Conectar a la base de datos MySQL
conexion = mysql.connector.connect(
    host="localhost",  # Cambia por la IP del servidor si es remoto
    user="root",       # Usuario de MySQL
    password="1234",  # Contraseña configurada
    database="bbdd"  # Nombre de la base de datos
)

cursor = conexion.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS taxis, clientes, pos_inicial_cliente, destinos, encriptado, auditoria
    ''')

# Crear las tablas
cursor.execute('''
CREATE TABLE IF NOT EXISTS taxis (
    id INT PRIMARY KEY,
    destino_a_cliente VARCHAR(255),
    destino_a_final VARCHAR(255),
    estado INT,
    coordX INT NOT NULL,
    coordY INT NOT NULL,
    pasajero INT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id VARCHAR(255) PRIMARY KEY,
    destino VARCHAR(255) NOT NULL,
    estado VARCHAR(255) NOT NULL,
    coordX INT NOT NULL,
    coordY INT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pos_inicial_cliente (
    id VARCHAR(255) PRIMARY KEY,
    coordX INT NOT NULL,
    coordY INT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS encriptado (
    taxi INT PRIMARY KEY,
    token VARCHAR(64) ,
    clave VARCHAR(64)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS destinos (
    destino VARCHAR(255) PRIMARY KEY,
    coordX INT NOT NULL,
    coordY INT NOT NULL
)
''')

# Los estados tienen que ser INFO, ERROR, WARNING
cursor.execute('''
CREATE TABLE IF NOT EXISTS auditoria (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                     
    estado VARCHAR(255) NOT NULL,
    mensaje VARCHAR(255) NOT NULL
)
''')

# Estado 0 = Ciudad no congelada, Estado 1 = Ciudad congelada
cursor.execute('''
CREATE TABLE IF NOT EXISTS estado_ciudad (
    id INT PRIMARY KEY AUTO_INCREMENT,
    estado INT NOT NULL
)
''')

#================================================================================================
# INSERTS
cursor.execute('''
    UPDATE estado_ciudad SET estado = 0
''')

cursor.execute('''
    INSERT INTO pos_inicial_cliente (id, coordX, coordY) VALUES 
    ('a', 19, 19),
    ('b', 4, 8),
    ('c', 7, 11),
    ('d', 2, 17),
    ('e', 5, 13)
''')


cursor.execute('''
    INSERT INTO destinos (destino, coordX, coordY) VALUES
    ('H', 10, 5),
    ('N', 14, 5),
    ('X', 18, 5),
    ('U', 10, 10),
    ('L', 14, 10),
    ('T', 18, 10),
    ('Y', 10, 15),
    ('Z', 14, 15),
    ('W', 18, 15)
''')




cursor.execute('''
    INSERT INTO taxis (id, destino_a_cliente, destino_a_final, estado, coordX, coordY, pasajero) VALUES
    (1, NULL, NULL, NULL, 1, 1, 0),
    (2, NULL, NULL, NULL, 1, 1, 0),
    (3, NULL, NULL, NULL, 1, 1, 0),
    (4, NULL, NULL, NULL, 1, 1, 0),
    (5, NULL, NULL, NULL, 1, 1, 0)
''')



#================================================================================================

# Confirmar la creación de la tabla
conexion.commit()

cursor.close()

# Cerrar la conexión
conexion.close()




