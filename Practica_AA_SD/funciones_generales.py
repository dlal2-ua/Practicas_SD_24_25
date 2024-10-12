import sqlite3

# Función para insertar datos en la base de datos
def update_datos_taxi(id, destino, estado, coordX, coordY):
    # Conectar a la base de datos
    conexion = sqlite3.connect('../database.db')
    
    # Crear un cursor
    cursor = conexion.cursor()
    
    # Actualizar los datos en la tabla 'taxis'
    cursor.execute('''
    UPDATE taxis SET destino = ?, estado = ?, coordX = ?, coordY = ? WHERE id = ?
    ''', (destino, estado, coordX, coordY, id))
    
    # Confirmar los cambios
    conexion.commit()
    
    # Cerrar la conexión
    conexion.close()

    print(f"Datos actualizados correctamente en la tabla 'taxis' para el taxi {id}.")




def leer_existencia_taxi(id):
    try:
        # Conectar a la base de datos
        conexion = sqlite3.connect('../database.db')
        
        # Crear un cursor
        cursor = conexion.cursor()
        
        # Ejecutar la consulta para obtener los datos del taxi según el id
        cursor.execute('''
        SELECT * FROM taxis WHERE id = ?
        ''', (id,))
        
        # Obtener todos los resultados
        datos = cursor.fetchall()
        
        # Cerrar la conexión
        conexion.close()

        # Verificar si se encontró el taxi
        if len(datos) >= 1:
            print(f"Se encontraron múltiples taxis con el ID {id}.")
            return 1
        else:
            print(f'No hay taxis con el ID {id}')
            return 0


    except sqlite3.Error as e:
        print(f"Error al acceder a la base de datos: {e}")  # Imprime cualquier otro error de la base de datos
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")  # Captura cualquier otra excepción


# Función para insertar datos en la base de datos
def insert_datos_taxi(id, destino, estado, coordX, coordY):
    # Conectar a la base de datos
    conexion = sqlite3.connect('../database.db')
    
    # Crear un cursor
    cursor = conexion.cursor()
    
    # Insertar los datos en la tabla 'taxis'
    try:
        cursor.execute('''
        INSERT INTO taxis (id, destino, estado, coordX, coordY) VALUES (?, ?, ?, ?, ?)
        ''', (id, destino, estado, coordX, coordY))
        
        # Confirmar los cambios
        conexion.commit()
        
        print(f"Taxi con ID {id} insertado correctamente en la tabla 'taxis'.")
        
    except sqlite3.IntegrityError:
        print(f"Error: Ya existe un taxi con ID {id}. No se puede insertar.")
    except Exception as e:
        print(f"Se produjo un error al insertar los datos: {e}")
    finally:
        # Cerrar la conexión
        conexion.close()