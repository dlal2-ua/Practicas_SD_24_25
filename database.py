import sqlite3

# Conectar (o crear) una base de datos llamada 'database.db'
conexion = sqlite3.connect('database.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conexion.cursor()

# Crear una tabla llamada 'taxis' con las columnas 'id', 'destino', 'estado', 'coordX' y 'coordY'
cursor.execute('''
CREATE TABLE IF NOT EXISTS taxis (
    id INTEGER PRIMARY KEY,
    destino CHAR NOT NULL,
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


# Confirmar la creación de la tabla
conexion.commit()

# Cerrar la conexión
conexion.close()


#================================================================================================




#================================================================================================



