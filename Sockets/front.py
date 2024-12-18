from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from funciones_generales import conectar_bd
from CTC_auxiliar import *
from EC_Central import temperatura

app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

# Lista para almacenar los logs
logs = []

@app.route('/api/logs', methods=['POST'])
def recibir_logs():
    log = request.json.get("log", "")
    if log:
        logs.append(log)
        #print(f"Log recibido: {log}")
    return jsonify({"status": "success"}), 200

@app.route('/api/obtener_logs', methods=['GET'])
def obtener_logs():
    return jsonify({"logs": logs})

# Ruta principal para servir el HTML
@app.route('/')
def index():
    return render_template('mapa.html')  # Sirve el archivo HTML

# Ruta para unificar taxis, clientes y destinos
@app.route('/api/mapa', methods=['GET'])
def obtener_datos_mapa():
    conexion = conectar_bd()
    cursor = conexion.cursor()

    # Obtener taxis
    cursor.execute("SELECT id, coordX, coordY, estado, pasajero, destino_a_cliente, destino_a_final FROM taxis")
    taxis = cursor.fetchall()
    taxis_dict = [{"tipo": "taxi", "id": taxi[0], "x": taxi[1], "y": taxi[2], "estado": taxi[3], "pasajero": taxi[4], "destino_a_cliente": taxi[5], "destino_a_final": taxi[6]} for taxi in taxis]

    # Obtener clientes
    cursor.execute("SELECT id, coordX, coordY, destino, estado FROM clientes")
    clientes = cursor.fetchall()
    clientes_dict = [{"tipo": "cliente", "id": cliente[0], "x": cliente[1], "y": cliente[2], "destino": cliente[3], "estado": cliente[4]} for cliente in clientes]

    #Obtener clientes_pos_inicial
    cursor.execute("SELECT id, coordX, coordY FROM pos_inicial_cliente")
    clientes_pos_inicial = cursor.fetchall()
    clientes_pos_inicial_dict = [{"tipo": "cliente_pos_inicial", "id": cliente[0], "x": cliente[1], "y": cliente[2]} for cliente in clientes_pos_inicial]

    # Obtener destinos
    cursor.execute("SELECT destino, coordX, coordY FROM destinos")
    destinos = cursor.fetchall()
    destinos_dict = [{"tipo": "destino", "nombre": destino[0], "x": destino[1], "y": destino[2]} for destino in destinos]

    # Obtener estado de la ciudad
    cursor.execute("SELECT estado FROM estado_ciudad")  # Supongamos que la tabla se llama 'ciudad'
    estado_ciudad = cursor.fetchone()  # Se asume que solo hay una fila para la ciudad
    estado_ciudad_dict = [{"tipo": "ciudad", "estado": estado_ciudad}]

    # Combinar todos los datos
    mapa_data = taxis_dict + clientes_dict + destinos_dict + estado_ciudad_dict

    cursor.close()
    conexion.close()
    return jsonify(mapa_data)



@app.route('/api/menu', methods=['POST'])
def ejecutar_menu():
    data = request.get_json()
    opcion = data.get('opcion')
    ciudad = data.get('ciudad')  # Campo opcional para la ciudad

    if not opcion:
        return jsonify({"error": "No se proporcionó una opción válida"}), 400

    if opcion == "1":
        # Lógica para consultar el estado del tráfico
        print("1. Consultar estado del tráfico")
        consultar_temperatura()
        estado_trafico = "Tráfico fluido en todas las vías principales."
        return jsonify({"mensaje": estado_trafico})

    elif opcion == "2":
        if not ciudad:
            return jsonify({"error": "Debes proporcionar el nombre de la ciudad."}), 400
        print(f"2. Cambiar ciudad a {ciudad}")
        cambiar_ciudad_front(ciudad)
        temperatura()
        # Lógica para manejar el cambio de ciudad
        resultado = f"La ciudad ha sido cambiada a {ciudad}."
        return jsonify({"mensaje": resultado})

    else:
        return jsonify({"error": "Opción no válida."}), 400



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
