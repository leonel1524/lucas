# docker build -t lucas:0.1.0 .
# Usamos una imagen de Python que ya viene con lo necesario
FROM python:3.11-slim

# Evita archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /lucas

# Saltamos el apt-get update a menos que sea estrictamente necesario
# Instalamos las librerías de Python directamente
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]