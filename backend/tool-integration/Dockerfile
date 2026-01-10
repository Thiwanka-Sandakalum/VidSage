FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production --prefer-offline --no-audit --progress=false && npm cache clean --force;

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
