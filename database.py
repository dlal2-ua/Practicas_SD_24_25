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
    INSERT INTO taxis (id, destino_a_cliente, destino_a_final, estado, coordX, coordY) VALUES
    (1, 'a', 'N', 0, 1, 1),
    (2, 'b', 'X', 0, 1, 1),
    (3, 'c', 'U', 0, 1, 1),
    (4, 'd', 'L', 0, 1, 1),
    (5, 'e', 'T', 0, 1, 1)
''')
               
cursor.execute('''
CREATE TABLE IF NOT EXISTS destinos(
    destino CHAR PRIMARY KEY,
    coordX INTEGER NOT NULL,
    coordY INTEGER NOT NULL
)
''')




#================================================================================================
# INSERTS
"""
cursor.execute('''
    INSERT INTO pos_inicial_cliente (id, coordX, coordY) VALUES 
    ('a', 10, 10),
    ('b', 20, 20),
    ('c', 30, 30),
    ('d', 40, 40),
    ('e', 50, 50)
''')

"""

cursor.execute('''
    INSERT INTO destinos (destino, coordX, coordY) VALUES
    ('H', 15, 19),
    ('N', 1, 20),
    ('X', 6, 6),
    ('U', 16, 11),
    ('L', 9, 9),
    ('T', 18, 3)
''')

#================================================================================================

# Confirmar la creación de la tabla
conexion.commit()

# Cerrar la conexión
conexion.close()





