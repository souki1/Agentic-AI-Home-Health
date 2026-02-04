# Health App Frontend - Docker image for GCP (Cloud Run, GKE, etc.)
# Multi-stage: build with Node, serve with nginx on PORT 8080

# ---- Build ----
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Build args for API URL (optional; default /api for same-origin proxy)
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build

# ---- Production ----
FROM nginx:1.27-alpine AS production

# Cloud Run uses PORT env (default 8080); nginx will listen on 8080
ENV PORT=8080
EXPOSE 8080

# Replace default config with our custom one
RUN rm -rf /etc/nginx/conf.d /usr/share/nginx/html

# Copy nginx config (listens on 8080, SPA fallback)
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Optional: run as non-root (Cloud Run often runs as root; uncomment if your runtime needs it)
# RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx
# USER nginx

CMD ["nginx", "-g", "daemon off;"]
