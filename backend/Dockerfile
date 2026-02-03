# Dockerfile de Producción para Render

FROM python:3.11-slim

# 2. Directorio de trabajo
WORKDIR /app

# Variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar código fuente
COPY . .

# 5. Recopilar archivos estáticos (Build time)
# Nota: La base de datos no está disponible aquí, asi que asegura que collectstatic no la necesite
RUN python manage.py collectstatic --no-input

# 7. Exponer puerto (Documentación)
# Render inyecta la variable PORT en tiempo de ejecución
EXPOSE 10000

# 6 y 8. Ejecutar migraciones e iniciar Gunicorn
# Usamos sh -c para encadenar los comandos correctamente y usar la variable de entorno $PORT
CMD sh -c "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"
