from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Configuración inicial
OPENWEATHER_API_KEY = "7448f35136de362e3dbdf21f10c8105b"  # Reemplaza con tu API Key de OpenWeather
DEFAULT_CITY = "Madrid"  # Ciudad por defecto
selected_city = DEFAULT_CITY


# Ruta para cambiar la ciudad
@app.route('/set_city', methods=['POST'])
def set_city():
    global selected_city
    data = request.json
    new_city = data.get("city")
    if new_city:
        selected_city = new_city
        return jsonify({"message": f"Ciudad actualizada a {selected_city}"}), 200
    else:
        return jsonify({"error": "Debes proporcionar un nombre de ciudad"}), 400


# Ruta para obtener el estado del tráfico
@app.route('/check_traffic', methods=['GET'])
def check_traffic():
    try:
        # Llama a la API de OpenWeather para obtener la temperatura de la ciudad
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={selected_city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(weather_url)
        response_data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "No se pudo obtener el clima de la ciudad"}), 500

        # Obtén la temperatura de la respuesta
        temperature = response_data['main']['temp']

        # Determina si el tráfico es viable o no
        if temperature < 0:
            return jsonify({"status": "KO", "temperature": temperature, "city": selected_city}), 200
        else:
            return jsonify({"status": "OK", "temperature": temperature, "city": selected_city}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta para consultar la ciudad actual
@app.route('/get_city', methods=['GET'])
def get_city():
    return jsonify({"city": selected_city}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
