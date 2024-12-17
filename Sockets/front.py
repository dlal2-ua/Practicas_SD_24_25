"""
from flask import Flask, render_template, Response
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from io import BytesIO
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Permitir conexiones desde otras aplicaciones


@app.route('/mapa')
def generar_mapa():
    try:
        # Obtener datos de la API Central
        taxis = requests.get('http://127.0.0.1:5000/api/taxis').json()
        clientes = requests.get('http://127.0.0.1:5000/api/clientes').json()
        destinos = requests.get('http://127.0.0.1:5000/api/destinos').json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API Central: {e}")
        return f"Error al conectar con la API Central: {e}", 500

    # Crear el mapa
    try:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 20)
        ax.set_xticks(range(21))
        ax.set_yticks(range(21))
        ax.grid(which='both', color='gray', linestyle='--', linewidth=0.5)
        ax.set_title('Mapa de la Ciudad')

        # Dibujar destinos
        for destino in destinos:
            ax.add_patch(Rectangle((destino['x'], destino['y']), 1, 1, color="blue", alpha=0.5))
            ax.text(destino['x'] + 0.5, destino['y'] + 0.5, destino['nombre'], color="black", ha="center", va="center")

        # Dibujar clientes
        for cliente in clientes:
            ax.add_patch(Rectangle((cliente['x'], cliente['y']), 1, 1, color="yellow"))
            ax.text(cliente['x'] + 0.5, cliente['y'] + 0.5, cliente['id'], color="black", ha="center", va="center")

        # Dibujar taxis
        for taxi in taxis:
            color = "green" if taxi['estado'] == 0 else ("red" if taxi['estado'] in [1, 2, 3] else "blue")
            ax.add_patch(Rectangle((taxi['x'], taxi['y']), 1, 1, color=color))
            ax.text(taxi['x'] + 0.5, taxi['y'] + 0.5, taxi['id'], color="white", ha="center", va="center")

        img_io = BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        plt.close(fig)

        return Response(img_io, mimetype='image/png')
    except Exception as e:
        print(f"Error al generar el mapa: {e}")
        return f"Error al generar el mapa: {e}", 500


# Ruta principal para mostrar el HTML que contiene el mapa
@app.route('/')
def mostrar_html():
    return render_template('mapa.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from funciones_generales import conectar_bd

app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

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
