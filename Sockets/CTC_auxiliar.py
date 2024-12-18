import requests
import time
from EC_Central import temperatura, RedirectStdoutToAPI
from funciones_generales import insertar_auditoria


## INSTALAR ->>>>>>>> pip install sqlalchemy pymysql

#=======================================================================================================
# URL de la API
API_URL = "http://localhost:5000/api/logs"

# Instanciar y usar la clase
redirector = RedirectStdoutToAPI(API_URL)
redirector.start()
#=======================================================================================================

# URL de EC_CTC
EC_CTC_URL = "http://127.0.0.1:5001/check_traffic"

# Función para cambiar la ciudad
def cambiar_ciudad():
    nueva_ciudad = input("Introduce el nombre de la ciudad: ")
    try:
        response = requests.post("http://127.0.0.1:5001/set_city", json={"city": nueva_ciudad})
        if response.status_code == 200:
            print(f"Ciudad cambiada a {nueva_ciudad}.")
            redirector.log(f"Ciudad cambiada a {nueva_ciudad}.")
            insertar_auditoria("INFO", f"Ciudad cambiada a {nueva_ciudad}.")
        else:
            print("Error al cambiar la ciudad:", response.json())
            redirector.log(f"Error al cambiar la ciudad: {response.json()}")
            insertar_auditoria("ERROR", f"Error al cambiar la ciudad: {response.json()}")
    except requests.exceptions.RequestException as e:
        print("No se pudo cambiar la ciudad:", e)
        redirector.log("No se pudo cambiar la ciudad:", e)
        insertar_auditoria("ERROR", f"No se pudo cambiar la ciudad: {e}")

# Menú de opciones
def menu():
    print("1. Consultar estado del tráfico")
    print("2. Cambiar ciudad")
    print("3. Salir")

# Bucle principal para consultar el tráfico y mostrar el menú

def controlador_menu(opcion):
    if opcion == "1":
        try:
            response = requests.get(EC_CTC_URL)
            if response.status_code == 200:
                data = response.json()
                print(f"Estado del tráfico en {data['city']}: {data['status']} (Temperatura: {data['temperature']}°C)")
                redirector.log(f"Estado del tráfico en {data['city']}: {data['status']} (Temperatura: {data['temperature']}°C)")
                insertar_auditoria("INFO", f"Estado del tráfico en {data['city']}: {data['status']} (Temperatura: {data['temperature']}°C)")
            else:
                print("Error al consultar EC_CTC:", response.json())
                redirector.log(f"Error al consultar EC_CTC: {response.json()}")
                insertar_auditoria("ERROR", f"Error al consultar EC_CTC: {response.json()}")
        except requests.exceptions.RequestException as e:
            print("No se ha podido conectar con EC_CTC, reintentando...")
            redirector.log("No se ha podido conectar con EC_CTC, reintentando...")
            insertar_auditoria("ERROR", f"No se ha podido conectar con EC_CTC, reintentando...")

    elif opcion == "2":
        cambiar_ciudad()
        temperatura()

    elif opcion == "3":
        print("Saliendo del menu.")
        exit

    else:
        print("Opción no válida. Por favor, elige una opción entre 1 y 3.")
        redirector.log("Opción no válida. Por favor, elige una opción entre 1 y 3.")
        insertar_auditoria("WARNING", "Opción no válida. Por favor, elige una opción entre 1 y 3.")



# Función para obtener la temperatura de la ciudad
def coger_temperatura():
    try:
        response = requests.get(EC_CTC_URL)
        if response.status_code == 200:
            data = response.json()
            #print(data['temperature'])
            return int(data['temperature'])
        else:
            print("Error al consultar EC_CTC:", response.json())
    except requests.exceptions.RequestException as e:
        print("No se ha podido conectar con EC_CTC, reintentando...")