FROM node:24-alpine AS base



FROM base AS dev
WORKDIR /app
COPY package*.json .
RUN npm install
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build


FROM nginx:stable-alpine AS prod

COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]