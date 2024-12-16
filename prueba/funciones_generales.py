import mysql.connector
import pandas as pd
from sqlalchemy import create_engine


#================================================

## INSTALAR ->>>>>>>> pip install sqlalchemy pymysql

# Conectar a la base de datos MySQL
def conectar_bd():
    conexion = mysql.connector.connect(
        host="localhost",  # Cambia por la IP del servidor MySQL si es remoto
        user="root",  # Usuario de MySQL
        password="1234",  # Contraseña configurada
        database="bbdd"  # Nombre de la base de datos
    )
    
    return conexion


# Configuración global para SQLAlchemy
def obtener_engine():
    usuario = "root"
    contraseña = "1234"
    servidor = "localhost"
    puerto = "3306"
    base_datos = "bbdd"
    return create_engine(f"mysql+pymysql://{usuario}:{contraseña}@{servidor}:{puerto}/{base_datos}")

#================================================

def coordX_taxi(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT coordX FROM taxis WHERE id = {id_taxi} ")
    coordenada = cursor.fetchall()[0][0]
    cursor.close()
    conexion.close()
    return int(coordenada)
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
    cursor.execute(f"SELECT coordY FROM taxis WHERE id = {id_taxi} ")
    coordenada = cursor.fetchall()[0][0]
    cursor.close()
    conexion.close()
    return int(coordenada)

def sacar_taxi(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET estado = NULL, destino_a_cliente = NULL, destino_a_final = NULL, coordX = 1, coordY = 1, pasajero = 0 WHERE id = {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def pasajero_dentro(id_taxi,cliente,Destino):
    c = cliente[0]
    d = Destino[0]
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET destino_a_cliente = %s, destino_a_final = %s  WHERE id = %s",(c,d,id_taxi))
    conexion.commit()
    cursor.close()
    conexion.close()
def pasajero_fuera(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET destino_a_cliente = NULL, destino_a_final = NULL  WHERE id = {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def buscar_taxi_activo(msg):
    engine = obtener_engine()
    query = f"SELECT id FROM taxis WHERE id = {msg} AND (estado = 0 OR estado = 1 OR estado = 2 OR estado = 3)"
    df_busqueda = pd.read_sql_query(query, engine)
    return not df_busqueda.empty  # Retorna True si encuentra el taxi, False si no
    
def autentificar_taxi(id_taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET estado = 1 WHERE id = {id_taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()


def buscar_taxi_arg(msg):
    engine = obtener_engine()
    query = f"SELECT id FROM taxis WHERE id = {msg} AND estado IS NULL"
    df_busqueda = pd.read_sql_query(query, engine)
    return not df_busqueda.empty  # Retorna True si encuentra el taxi, False si no
def obtener_cliente(id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT destino_a_cliente FROM taxis WHERE id = {id}")
    pasajero = cursor.fetchone()
    cursor.close()
    conexion.close()
    return pasajero[0]
def existe_pasajero(id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT pasajero FROM taxis WHERE id = %s", (id,))
    resultado = cursor.fetchone()
    if resultado is not None:
        return resultado[0] == 1
    return False


def obtener_destino_final_de_taxi(taxi_id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT destino_a_final FROM taxis WHERE id = {taxi_id}")
    destino = cursor.fetchone()
    cursor.close()
    conexion.close()
    return destino
def obtener_destinos_bien():
    conexion = conectar_bd()
    query = "SELECT destino FROM destinos"
    cursor = conexion.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    destinos = [fila[0] for fila in resultados]
    return destinos
def existe_destino(destino):
    destinos = obtener_destinos_bien()
    existe = False
    for d in destinos:
        if d == destino:
            existe = True
    return existe
def hay_pasajero(taxi_id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT pasajero FROM taxis WHERE id = {taxi_id}")
    pasajero = cursor.fetchone()
    cursor.close()
    conexion.close()
    if pasajero == 1:
        return True
    else:
        return False
def cambiar_destino(taxi_id,destino):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET destino_a_final = %s WHERE id = %s",(destino,taxi_id))
    conexion.commit()
    cursor.close()
    conexion.close()
def central_para_taxi(taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET estado = 3 WHERE id = {taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def central_sigue_taxi(taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET estado = 0 WHERE id = {taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
def parado_sensor(taxi):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE taxis SET estado = 2 WHERE id = {taxi}")
    conexion.commit()
    cursor.close()
    conexion.close()
###========= FUNCIONES DE BASE DE DATOS =========###

# Función para obtener destinos desde la base de datos

def cambiarPosInicialCliente(conexion, id, coordX, coordY):
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE pos_inicial_cliente SET coordX = %s, coordY = %s WHERE id = %s", (coordX, coordY, id))
        conexion.commit()
    except mysql.connector.Error as e:
        print(f"Error al actualizar coordenadas iniciales del cliente en la base de datos: {e}")

def agregarCliente(conexion, id, destino, estado, coordX, coordY):
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO clientes (id, destino, estado, coordX, coordY) VALUES (%s, %s, %s, %s, %s)", (id, destino, estado, coordX, coordY))
        conexion.commit()
    except mysql.connector.Error as e:
        print(f"Error al insertar cliente en la base de datos: {e}")

def buscarCliente(conexion, id):
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
        return cursor.fetchone() is not None
    except mysql.connector.Error as e:
        print(f"Error al buscar cliente en la base de datos: {e}")
        return False



def cambiarEstadoCliente(conexion, id, estado):
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE clientes SET estado = %s WHERE id = %s", (estado, id))
        conexion.commit()
    except mysql.connector.Error as e:
        print(f"Error al actualizar estado del cliente en la base de datos: {e}")




def agregarCoordCliente(conexion, id, coordX, coordY):
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE clientes SET coordX = %s, coordY = %s WHERE id = %s", (coordX, coordY, id))
        conexion.commit()
    except mysql.connector.Error as e:
        print(f"Error al actualizar coordenadas del cliente en la base de datos: {e}")



def obtener_destinos(conexion):
    
    # Crear el motor SQLAlchemy
    engine = obtener_engine()

    query = "SELECT destino, coordX, coordY FROM destinos"
    df_destinos = pd.read_sql_query(query, engine)
    destinos_dict = {row['destino']: (row['coordX'], row['coordY']) for _, row in df_destinos.iterrows()}
    return destinos_dict


# Función para liberar un taxi después de completar el viaje
def liberar_taxi(conexion, taxi_id):
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET estado = 1 WHERE id = %s", (taxi_id,))
    conexion.commit()  # Asegurar que los cambios se guarden en la base de datos



# Función para obtener un taxi disponible desde la base de datos
def obtener_taxi_disponible(conexion):
    cursor = conexion.cursor()

    # Consulta para seleccionar un taxi disponible (estado = 1)
    cursor.execute("SELECT id FROM taxis WHERE estado = 1 LIMIT 1")
    taxi = cursor.fetchone()

    # Si se encuentra un taxi disponible, cambiar su estado a ocupado (0)
    if taxi:
        taxi_id = taxi[0]
        cursor.execute("UPDATE taxis SET estado = 0 WHERE id = %s", (taxi_id,))
        conexion.commit()  # Asegurar que los cambios se guarden en la base de datos
        return taxi_id
    else:
        return None  # No hay taxis disponibles


def obtener_pos_inicial_cliente(cliente_id):
    # Establecer una nueva conexión a la base de datos para cada hilo
    engine = obtener_engine()
   
    # Usar parámetros en la consulta para evitar inyección SQL
    query = "SELECT coordX, coordY FROM pos_inicial_cliente WHERE id = %s"
    df_pos_inicial = pd.read_sql_query(query, engine, params=(cliente_id,))
    
    if not df_pos_inicial.empty:
        # Convertir coordX y coordY a enteros
        coordX = int(df_pos_inicial['coordX'][0])
        coordY = int(df_pos_inicial['coordY'][0])
        return coordX, coordY
    else:
        print(f"No se encontraron coordenadas para el cliente {cliente_id}.")
        return None, None  # Manejo del error



# Función para obtener las coordenadas del destino desde la base de datos
def obtener_destino_coords(conexion, destino):
    query = "SELECT coordX, coordY FROM destinos WHERE destino = %s"
    cursor = conexion.cursor()
    cursor.execute(query, (destino,))
    resultado = cursor.fetchone()

    if resultado:
        return int(resultado[0]), int(resultado[1])  # Retornar coordX y coordY
    else:
        print(f"No se encontraron coordenadas para el destino {destino}")
        return None
    
def obtener_taxis(conexion):
    cursor = conexion.cursor()
    query = """
        SELECT id, coordX, coordY, estado
        FROM taxis;
    """
    cursor.execute(query)
    taxis = cursor.fetchall()
    
    # Asegúrate de que esta línea está alineada correctamente
    taxis_modificados = [(taxi_id, int(coordX), int(coordY), estado) for taxi_id, coordX, coordY, estado in taxis]  # Convertimos a enteros
    return taxis_modificados



# Función para obtener los datos del taxi de la base de datos
def obtener_datos_taxi(conexion, taxi_id):
    cursor = conexion.cursor()
    # Supongamos que la base de datos tiene los campos necesarios para ambos destinos y el estado del pasajero
    cursor.execute("SELECT destino_a_cliente, destino_a_final, estado, coordX, coordY, pasajero FROM taxis WHERE id = %s", (taxi_id,))
    resultado = cursor.fetchone()

    if resultado:
        destino_al_cliente, destino_a_final, estado, coordX, coordY, estado_pasajero = resultado
        return destino_al_cliente, destino_a_final, estado, int(coordX), int(coordY), estado_pasajero
    return None, None, None, None, None, None

def subir_pasajero(conexion, taxi_id):
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET pasajero = 1 WHERE id = %s", (taxi_id,))
    conexion.commit()  # Asegurar que los cambios se guarden en la base de datos

def bajar_pasajero(conexion, taxi_id):
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET pasajero = 0 WHERE id = %s", (taxi_id,))
    conexion.commit()  # Asegurar que los cambios se guarden en la base de datos


# Función para obtener la información de los taxis desde la base de datos
def obtener_taxis_desde_bd(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT id, destino_a_cliente, coordX, coordY, estado, pasajero FROM taxis")
    taxis = cursor.fetchall()
    return taxis  # Devuelve una lista de tuplas con los datos de cada taxi


def cliente_en_servicio(conexion, cliente_id):
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM taxis 
        WHERE destino_a_cliente = %s AND estado = 0
    """, (cliente_id,))
    
    # Si COUNT(*) es mayor que 0, significa que existe al menos un taxi con esas condiciones
    resultado = cursor.fetchone()[0] > 0
    return resultado


def taxi_siguiente_servicio_tabla(conexion, taxi_id):
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET destino_a_cliente = NULL, destino_a_final = NULL WHERE id = %s", (taxi_id,))
    conexion.commit()  # Asegurar que los cambios se guarden en la base de datos


###======================================
###======================================

#     FUNCION PRACTICA 2

def cambiar_estado_TAXI_ciudad_ko(taxi_id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET estado = 4 where id = %s", (taxi_id,))
    conexion.commit()  # Asegurar que los cambios se guarden en la base de datos
    cursor.close()  # Cerrar el cursor después de realizar la operación


def cambiar_estado_TAXI_ciudad_ok():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET estado = 0")
    conexion.commit()  # Asegurar que los cambios se guarden en la base de datos
    cursor.close()  # Cerrar el cursor después de realizar la operación

def obtener_datos_TAXI_ciudad():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, coordX, coordY, destino_a_cliente, estado FROM taxis")
    taxi = cursor.fetchall()
    cursor.close()
    conexion.close()
    return taxi

def cambiarEstadoCliente(estado):
    conexion = conectar_bd()
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE clientes SET estado = %s", (estado,))
        conexion.commit()
    except mysql.connector.Error as e:
        print(f"Error al actualizar estado del cliente en la base de datos: {e}")