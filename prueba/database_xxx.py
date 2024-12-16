import sqlite3
#

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
    destino_a_cliente CHAR,
    destino_a_final CHAR,
    estado INTEGER ,
    coordX INTEGER NOT NULL,
    coordY INTEGER NOT NULL,
    pasajero INTEGER NOT NULL

)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id CHAR PRIMARY KEY,
    destino CHAR NOT NULL,
    estado STRING NOT NULL,
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
CREATE TABLE IF NOT EXISTS destinos(
    destino CHAR PRIMARY KEY,
    coordX INTEGER NOT NULL,
    coordY INTEGER NOT NULL
)
''')
       



#================================================================================================
# INSERTS

cursor.execute('''
    INSERT INTO pos_inicial_cliente (id, coordX, coordY) VALUES 
    ('a', 2, 6),
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

# Cerrar la conexión
conexion.close()





