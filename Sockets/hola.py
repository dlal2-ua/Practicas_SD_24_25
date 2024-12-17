
import io
import sys
import threading
import time
import requests

class RedirectStdoutToAPI:
    def __init__(self, api_url):
        self.api_url = api_url
        self.buffer = io.StringIO()
        self.original_stdout = sys.stdout
        self.stop_thread = False

    def start(self):
        """Redirige sys.stdout al buffer"""
        sys.stdout = self.buffer
        self.thread = threading.Thread(target=self._send_to_api, daemon=True)
        self.thread.start()

    def stop(self):
        """Restaura sys.stdout y detiene el thread"""
        sys.stdout = self.original_stdout
        self.stop_thread = True
        self.thread.join()

    def _send_to_api(self):
        """Envía datos impresos al buffer hacia la API"""
        while not self.stop_thread:
            output = self.buffer.getvalue()
            if output:
                try:
                    # Enviar a la API
                    requests.post(self.api_url, json={"log": output})
                    # Limpia el buffer después de enviar
                    self.buffer.truncate(0)
                    self.buffer.seek(0)
                except requests.RequestException as e:
                    print(f"Error al enviar a la API: {e}", file=self.original_stdout)
            time.sleep(1)  # Ajusta el intervalo según sea necesario

# URL de la API a la que enviarás los logs
API_URL = "http://localhost:5000/api/logs"

# Configurar la redirección
redirector = RedirectStdoutToAPI(API_URL)
redirector.start()

try:
    # Código que genera impresiones
    print("Este es un mensaje para el frontend.")
    for i in range(10):
        print(f"Contador: {i}")
        time.sleep(0.5)
finally:
    # Detener la redirección
    redirector.stop()