FROM node:22-alpine AS build

WORKDIR /app
COPY packages/web/package*.json ./
RUN npm ci
COPY packages/web .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY packages/web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
