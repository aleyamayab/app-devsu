FROM python:3.11-slim

# Evita archivos .pyc y asegura logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema para la aplicación.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

# Puerto que se usara
EXPOSE 8000

# Healthcheck usando el endpoint de salud de la API
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8000/api/health/ || exit 1

# Arranque (devserver, como acordamos)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
