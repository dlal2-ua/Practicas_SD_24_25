import os
import time
import pandas as pd
import sqlite3

# Conectar a la base de datos SQLite
def conectar_bd():
    conexion = sqlite3.connect('database.db')  # Cambia a la ruta de tu base de datos
    return conexion

# Obtener los datos de la tabla taxis desde la base de datos
def obtener_taxis(conexion):
    query = "SELECT id, destino_a_cliente, estado FROM taxis"
    df_taxis = pd.read_sql_query(query, conexion)
    return df_taxis

"""
# Obtener los datos de la tabla clientes desde la base de datos
def obtener_clientes(conexion):
    query = "SELECT id, destino, estado FROM clientes"
    df_clientes = pd.read_sql_query(query, conexion)
    return df_clientes
"""

def obtener_destinos(conexion):
    query = "SELECT destino, coordX, coordY FROM destinos"
    df_destinos = pd.read_sql_query(query, conexion)
    return df_destinos



# Función para limpiar la terminal
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# Función para imprimir el "mapa" en la terminal
def imprimir_mapa(df_taxis): #, df_clientes
    limpiar_pantalla()

    print("*** EASY CAB Release 1 ***")
    
    # Imprimir tabla de Taxis
    print("\nTaxis:")
    print("+----+---------+-----------------+")
    print("| Id | Destino | Estado          |")
    print("+----+---------+-----------------+")
    for _, row in df_taxis.iterrows():
        print(f"| {row['id']:2} | {row['destino_a_cliente']:7} | {row['estado']:15} |")
    print("+----+---------+-----------------+")

"""
    # Imprimir tabla de Clientes
    print("\nClientes:")
    print("+----+---------+-----------------+")
    print("| Id | Destino | Estado          |")
    print("+----+---------+-----------------+")
    for _, row in df_clientes.iterrows():
        print(f"| {row['id']:2} | {row['destino']:7} | {row['estado']:15} |")
    print("+----+---------+-----------------+")
"""

"""
# Monitorizar cambios en la base de datos
def monitorizar_bd():
    conexion = conectar_bd()

    

    # Inicialmente, cargar los datos de la base de datos
    df_taxis = obtener_taxis(conexion)
    #df_clientes = obtener_clientes(conexion)
    
    # Imprimir el mapa inicial
    imprimir_mapa(df_taxis) #, df_clientes
 
    # Variables para comparar cambios
    num_taxis = len(df_taxis)
    #num_clientes = len(df_clientes)

    # Bucle para monitorizar continuamente la base de datos
    while True:
        # Leer de nuevo los datos de la base de datos
        df_taxis_actual = obtener_taxis(conexion)
        #df_clientes_actual = obtener_clientes(conexion)

        # Si ha cambiado el número de taxis o clientes, refrescar el mapa
        if len(df_taxis_actual) != num_taxis: # or len(df_clientes_actual) != num_clientes
            num_taxis = len(df_taxis_actual)
            #num_clientes = len(df_clientes_actual)
            imprimir_mapa(df_taxis_actual) #, df_clientes_actual

        # Esperar 5 segundos antes de revisar de nuevo
        time.sleep(10)


# Comenzar a monitorizar la base de datos
monitorizar_bd()


"""
conexion = conectar_bd()
destino = obtener_destinos(conexion)
print(" Destinos:")
print("+---------+--------+---------+")
print("| Destino | CoordX | CoordY  |")
print("+---------+--------+---------+")

# Ajustar el ancho de las columnas para que queden bien alineadas
for _, row in destino.iterrows():
    print(f"| {row['destino']:<7} | {row['coordX']:<6} | {row['coordY']:<7} |")

print("+---------+--------+---------+")
