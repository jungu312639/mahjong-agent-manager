# Build stage
FROM node:20-slim as build-stage

WORKDIR /app
# Copy package files
COPY web/frontend/package*.json ./
RUN npm install

# Copy frontend source and build
COPY web/frontend/ ./
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
