FROM node:24-alpine AS base
ARG VITE_API_BASE_URL="http://localhost:8000"
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

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