FROM node:20-slim
RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install
COPY . .
# Importante: Vite necesita --host para responder fuera del contenedor
CMD ["pnpm", "run", "dev", "--host"]