from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from funciones_generales import conectar_bd

app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

# Lista para almacenar los logs
logs = []

@app.route('/api/logs', methods=['POST'])
def recibir_logs():
    log = request.json.get("log", "")
    if log:
        logs.append(log)
        print(f"Log recibido: {log}")
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

    # Combinar todos los datos
    mapa_data = taxis_dict + clientes_dict + destinos_dict

    cursor.close()
    conexion.close()
    return jsonify(mapa_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
