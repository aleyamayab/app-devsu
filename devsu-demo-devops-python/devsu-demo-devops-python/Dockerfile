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

# Crea directorio para archivos estáticos con permisos para el usuario 1000
RUN mkdir -p /app/staticfiles && chown -R 1000:1000 /app/staticfiles && chmod -R 755 /app/staticfiles

# Copia script de arranque
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Puerto que se usara
EXPOSE 8000

# Healthcheck usando el endpoint de salud de la API
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8000/api/health/ || exit 1

# Usa entrypoint para ejecutar collectstatic antes de arrancar
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
