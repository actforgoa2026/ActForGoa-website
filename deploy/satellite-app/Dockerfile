FROM node:24.21.0-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force
COPY server ./server
COPY shared ./shared
COPY dist-satellite ./dist-satellite
ENV NODE_ENV=production ADMIN_DATA_DIR=/data/admin
CMD ["node", "--import", "tsx", "server/satellite-web.ts"]
