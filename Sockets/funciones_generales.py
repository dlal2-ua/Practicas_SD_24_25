import sqlite3
import pandas as pd

#================================================================================================

# Conectar a la base de datos SQLite
def conectar_bd():
    conexion = sqlite3.connect('database.db')  # Cambia a la ruta de tu base de datos
    return conexion

#================================================================================================

def coordX_taxi(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT coordX FROM taxis WHERE id == {id_taxi} ")
    coordenada = cursor.fetchall()[0][0]
    cursor.close()
    conexion.close()
    return coordenada
def nueva_pos_taxi (id_taxi,x,y):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET coordX = {x}, coordY = {y} WHERE id = {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def coordY_taxi(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT coordY FROM taxis WHERE id == {id_taxi} ")
    coordenada = cursor.fetchall()[0][0]
    cursor.close()
    conexion.close()
    return coordenada
def sacar_taxi(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET estado = NULL, destino_a_cliente = NULL, destino_a_final = NULL, coordX = 1, coordY = 1 WHERE id = {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def pasajero_dentro(id_taxi,cliente,Destino):
    c = cliente[0]
    d = Destino[0]
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET destino_a_cliente = ?, destino_a_final = ?  WHERE id == ?",(c,d,id_taxi))
    conexion.commit()
    cursor.close()
    conexion.close()
def pasajero_fuera(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET destino_a_cliente = NULL, destino_a_final = NULL  WHERE id == {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def buscar_taxi_activo(msg):
    conexion = conectar_bd()
    query = f"SELECT id FROM taxis WHERE id == {msg} AND estado==0 or estado==1"
    df_busqueda = pd.read_sql_query(query,conexion)
    if df_busqueda.empty:
        conexion.close()
        return False
    else:
        conexion.close()
        return True