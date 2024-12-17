
"""
Este archivo será una API Flask que interactúa con la base de datos y la Central.

Funciones clave:
Obtener taxis, clientes, y destinos desde la base de datos.
Proveer estos datos al frontend mediante una API REST.

"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from funciones_generales import conectar_bd

app = Flask(__name__)
CORS(app)  # Permitir conexiones desde otras aplicaciones

# Ruta para obtener información de taxis
@app.route('/api/taxis', methods=['GET'])
def obtener_taxis():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, coordX, coordY, estado FROM taxis")
    taxis = cursor.fetchall()
    cursor.close()
    conexion.close()
    taxis_dict = [{"id": taxi[0], "x": taxi[1], "y": taxi[2], "estado": taxi[3]} for taxi in taxis]
    return jsonify(taxis_dict)

# Ruta para obtener información de clientes
@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, coordX, coordY, destino, estado FROM clientes")
    clientes = cursor.fetchall()
    cursor.close()
    conexion.close()
    clientes_dict = [{"id": cliente[0], "x": cliente[1], "y": cliente[2], "destino": cliente[3], "estado": cliente[4]} for cliente in clientes]
    return jsonify(clientes_dict)

# Ruta para obtener información de destinos
@app.route('/api/destinos', methods=['GET'])
def obtener_destinos():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT destino, coordX, coordY FROM destinos")
    destinos = cursor.fetchall()
    cursor.close()
    conexion.close()
    destinos_dict = [{"nombre": destino[0], "x": destino[1], "y": destino[2]} for destino in destinos]
    return jsonify(destinos_dict)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
