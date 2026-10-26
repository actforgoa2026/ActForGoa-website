FROM node:24.21.0-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force
COPY server ./server
COPY shared ./shared
ENV NODE_ENV=production REPORT_HOST=0.0.0.0 REPORT_DATA_DIR=/data/private
CMD ["npm", "start"]
