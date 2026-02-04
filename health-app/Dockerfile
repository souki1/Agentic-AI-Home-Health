# Health App Frontend - Docker image for GCP (Cloud Run, GKE, etc.)
# Multi-stage: build with Node, serve with Node + serve (no nginx)

# ---- Build ----
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Build args for API URL (set to backend URL for Cloud Run)
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build

# ---- Production (Node + serve) ----
FROM node:22-alpine AS production

WORKDIR /app

# Only need serve to host static files (smaller image)
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/dist ./dist

# Cloud Run uses PORT env (default 8080)
ENV PORT=8080
EXPOSE 8080

# serve: -s = SPA fallback (all routes -> index.html), -l = port
CMD ["sh", "-c", "serve dist -s -l ${PORT:-8080}"]
