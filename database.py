import sqlite3

# Conectar (o crear) una base de datos llamada 'database.db'
conexion = sqlite3.connect('database.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conexion.cursor()

# Crear una tabla llamada 'taxis' con las columnas 'id', 'destino_a_cliente', 'destino_a_final', 'estado', 'coordX' y 'coordY'
#He añadido destino a cliente (para que salga en pantalla que va en direccion cliente) y destino a final (cuando haya recogido al cliente, en la tabla aparecerá el destino final)
#La central pasará toda la información a los taxis sobre el cliente, y el taxi ya tendra tanto la informacion para recoger como para dejar al cliente

cursor.execute('''
CREATE TABLE IF NOT EXISTS taxis (
    id INTEGER PRIMARY KEY,
    destino_a_cliente CHAR NOT NULL,
    destino_a_final CHAR NOT NULL,
    estado BOOLEAN NOT NULL,
    coordX INTEGER NOT NULL,
    coordY INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id CHAR PRIMARY KEY,
    destino CHAR NOT NULL,
    estado BOOLEAN NOT NULL,
    coordX INTEGER NOT NULL,
    coordY INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pos_inicial_cliente(
    id CHAR PRIMARY KEY,
    coordX INTEGER NOT NULL,
    coordY INTEGER NOT NULL
)
''')

cursor.execute('''
    INSERT INTO pos_inicial_cliente (id, coordX, coordY) VALUES 
    ('a', 10, 10),
    ('b', 20, 20),
    ('c', 30, 30),
    ('d', 40, 40),
    ('e', 50, 50)
''')
               
cursor.execute('''
CREATE TABLE IF NOT EXISTS servicios(
    id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,  
    id CHAR NOT NULL,                              
    destino CHAR NOT NULL,
    coordX INTEGER NOT NULL,
    coordY INTEGER NOT NULL
)
''')


cursor.execute('''
INSERT INTO servicios (id, destino, coordX, coordY) VALUES
('a', 'F', 10, 10),
('b', 'G', 20, 20),
('c', 'X', 30, 30),
('a', 'Y', 40, 40)
''')


# Confirmar la creación de la tabla
conexion.commit()

# Cerrar la conexión
conexion.close()


#================================================================================================




#================================================================================================



