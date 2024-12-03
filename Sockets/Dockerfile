# Usar una imagen de Python como base
FROM python:3.12.4

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /Sockets

# Copiar los archivos del proyecto al contenedor
COPY . /Sockets/

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer un puerto (si tu aplicación lo requiere)
# Ejemplo: si usas Flask en el puerto 5000
# EXPOSE 5000

COPY . .

# Definir el comando de inicio para ejecutar el programa
CMD ["python", "EC_Central.py"]
