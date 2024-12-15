import requests
import time


## INSTALAR ->>>>>>>> pip install sqlalchemy pymysql


# URL de EC_CTC
EC_CTC_URL = "http://127.0.0.1:5001/check_traffic"

# Función para cambiar la ciudad
def cambiar_ciudad():
    nueva_ciudad = input("Introduce el nombre de la ciudad: ")
    try:
        response = requests.post("http://127.0.0.1:5001/set_city", json={"city": nueva_ciudad})
        if response.status_code == 200:
            print(f"Ciudad cambiada a {nueva_ciudad}.")
        else:
            print("Error al cambiar la ciudad:", response.json())
    except requests.exceptions.RequestException as e:
        print("No se pudo cambiar la ciudad:", e)

# Menú de opciones
def menu():
    print("\n--- Menú EC_CTC ---")
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
            else:
                print("Error al consultar EC_CTC:", response.json())
        except requests.exceptions.RequestException as e:
            print("No se ha podido conectar con EC_CTC, reintentando...")

    elif opcion == "2":
        cambiar_ciudad()

    elif opcion == "3":
        print("Saliendo del programa.")
        exit

    else:
        print("Opción no válida. Por favor, elige una opción entre 1 y 3.")





####================================================================================================
"""
while True:
     try:
         menu()
         opcion = input("Elige una opción (1, 2, 3): ")

         if opcion == "1":
             try:
                 response = requests.get(EC_CTC_URL)
                 if response.status_code == 200:
                     data = response.json()
                     print("")
                     print(f"Estado del tráfico en {data['city']}: {data['status']} (Temperatura: {data['temperature']}°C)")
                 else:
                     print("Error al consultar EC_CTC:", response.json())
             except requests.exceptions.RequestException as e:
                 print("No se ha podido conectar con EC_CTC, reintentando...")

         elif opcion == "2":
             cambiar_ciudad()

         elif opcion == "3":
             print("Saliendo del programa.")
             break

         else:
             print("Opción no válida. Por favor, elige una opción entre 1 y 3.")

         #time.sleep(10)  # Esperar 10 segundos antes de la siguiente consulta

     except KeyboardInterrupt:
         #print("\nInterrupción detectada. Saliendo del programa...")
         break
"""