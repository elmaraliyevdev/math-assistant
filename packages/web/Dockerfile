FROM node:22-alpine AS build

# Preserve monorepo layout so sync-brand-assets can resolve ../../ from packages/web
WORKDIR /workspace/packages/web
COPY packages/web/package*.json ./
RUN npm ci
COPY packages/web .
COPY packages/brand /workspace/packages/brand
COPY logo.svg logo-white.svg black-logo-icon.svg white-logo-icon.svg /workspace/

ARG VITE_SITE_URL=https://app.mathstudio.app
ARG VITE_API_BASE_URL=/api
ENV VITE_SITE_URL=$VITE_SITE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:alpine
COPY --from=build /workspace/packages/web/dist /usr/share/nginx/html
COPY packages/web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
