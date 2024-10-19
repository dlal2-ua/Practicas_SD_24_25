import os
import time
import pandas as pd
import sqlite3
from funciones_generales import conectar_bd

import matplotlib.pyplot as plt
import numpy as np


"""
Explicación:
    Consulta SQL: Se ejecuta la consulta para obtener los destinos y sus coordenadas (coordX, coordY).
    DataFrame: Los resultados de la consulta se almacenan en un DataFrame de pandas (df_destinos).
    Conversión a diccionario: Utilizo un diccionario por comprensión para transformar cada fila del DataFrame en un par clave-valor, donde la clave es el nombre_destino y el valor es una tupla (coordX, coordY).
        row['destino']: El nombre del destino.
        (row['coordX'], row['coordY']): Las coordenadas del destino como una tupla.
    Impresión: El diccionario resultante se imprime, mostrando el formato deseado.
"""

conexion = conectar_bd()

def obtener_destinos(conexion):
    query = "SELECT destino, coordX, coordY FROM destinos"
    
    # Leer los datos de la base de datos y almacenarlos en un DataFrame
    df_destinos = pd.read_sql_query(query, conexion)
    
    # Convertir el DataFrame en un diccionario {nombre_destino: (x, y)}
    destinos_dict = {row['destino']: (row['coordX'], row['coordY']) for _, row in df_destinos.iterrows()}
    
    return destinos_dict

#================================================================================================
# Obtener el diccionario de destinos
destinos = obtener_destinos(conexion)

# Imprimir el diccionario con salto de línea para cada entrada
for nombre_destino, coordenadas in destinos.items():
    print(f"{nombre_destino}: {coordenadas}")
#================================================================================================

# Suponiendo que este es el color para todos los destinos
color_destinos = "deepskyblue"

# Tamaño de la cuadrícula
grid_size = 20  # Mantener el tamaño original de la cuadrícula

# Crear el gráfico para el mapa
fig, ax = plt.subplots(figsize=(8, 8))

# Configurar los límites para la cuadrícula, desde 0.5 hasta grid_size + 0.5 para que no se corten los bordes
ax.set_xlim(0.1, grid_size)
ax.set_ylim(0.1, grid_size)

# Configurar las líneas de la cuadrícula
ax.set_xticks(np.arange(1, grid_size + 1))
ax.set_yticks(np.arange(1, grid_size + 1))
ax.grid(True)

# Ocultar etiquetas de los ejes para un aspecto más limpio
ax.set_xticklabels([])
ax.set_yticklabels([])

# Invertir el eje y para coincidir con la orientación original de la imagen
ax.invert_yaxis()

# Eliminar las marcas de los ejes
ax.tick_params(axis='both', which='both', length=0)

# Agregar cuadrados de color azul y etiquetas para cada destino
for label, (x, y) in destinos.items():
    ax.add_patch(plt.Rectangle((x - 1, y - 1), 1, 1, color=color_destinos))  # Pintar el cuadrado de azul
    ax.text(x - 0.5, y - 0.5, label, va='center', ha='center', fontsize=10, color="black")  # Agregar la etiqueta en el centro

# Mostrar el mapa actualizado
plt.show()