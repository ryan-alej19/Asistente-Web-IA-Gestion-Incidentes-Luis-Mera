# Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

# Instalar dependencias
COPY package.json package-lock.json* ./
RUN npm install

# Copiar código fuente
COPY . .

# Exponer puerto (Configurable via .env)
EXPOSE 3001

# Iniciar aplicación
CMD ["npm", "start"]
