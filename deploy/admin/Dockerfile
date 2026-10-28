FROM node:24.21.0-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force
COPY server ./server
COPY shared ./shared
COPY public/data ./public/data
COPY src/content/guide-records.json ./src/content/guide-records.json
ENV NODE_ENV=production ADMIN_HOST=0.0.0.0 ADMIN_DATA_DIR=/data/admin
CMD ["npm", "start"]
