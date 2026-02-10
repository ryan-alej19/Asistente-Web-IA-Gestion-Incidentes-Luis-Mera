FROM node:18-slim

WORKDIR /app

# Instalar dependencias
COPY package*.json .
RUN npm install

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 3000

# Comando de inicio
CMD ["npm", "start"]
