# Imagen base de Python 3.10 slim
FROM python:3.10-slim

# Evitar prompts de apt
ENV DEBIAN_FRONTEND=noninteractive

# Establecer directorio de trabajo en el contenedor
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Actualizar pip y librerías necesarias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usará Flask
EXPOSE 8080

# Variable de entorno para que Flask sepa el host
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Comando para ejecutar la aplicación
CMD ["python", "run.py"]