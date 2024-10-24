import sqlite3

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
    cursor.execute(f"UPDATE taxis SET estado = NULL WHERE id = {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def pasajero_dentro(id_taxi,pasajero):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET pasajero = {pasajero} WHERE id == {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()