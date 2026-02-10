FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Migrar base de datos al iniciar
# Exponer puerto
EXPOSE 8000

# Comando de inicio (para demo/desarrollo)
CMD ["sh", "-c", "python manage.py migrate --run-syncdb && python manage.py runserver 0.0.0.0:8000"]
