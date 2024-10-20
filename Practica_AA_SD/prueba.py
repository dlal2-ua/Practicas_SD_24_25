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


