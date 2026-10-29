FROM node:20-slim
RUN npm install -g pnpm@10
WORKDIR /src
# pnpm-workspace.yaml debe copiarse antes del install: declara allowBuilds
# (esbuild). Sin él, pnpm bloquea los build scripts y falla con
# ERR_PNPM_IGNORED_BUILDS.
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./
RUN pnpm install
COPY . .
# Importante: Vite necesita --host para responder fuera del contenedor
CMD ["pnpm", "run", "dev", "--host"]