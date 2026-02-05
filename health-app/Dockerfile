# Health App Frontend - Docker image for GCP (Cloud Run, GKE, etc.)
# Multi-stage: build with Node, serve with Node + serve (no nginx)

# ---- Build ----
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Build args for API URL (set to backend URL for Cloud Run)
# If not provided, Vite will use .env.production
ARG VITE_API_URL

# Copy all files (including .env.production)
COPY . .

# Verify VITE_API_URL is set (for debugging)
RUN if [ -z "$VITE_API_URL" ]; then \
      echo "⚠️ VITE_API_URL not set via build arg, will use .env.production"; \
      cat .env.production 2>/dev/null || echo "⚠️ .env.production not found"; \
    else \
      echo "✅ Using VITE_API_URL from build arg: $VITE_API_URL"; \
    fi

# Build with production mode
# Only inject VITE_API_URL if the build arg is non-empty
RUN if [ -n "$VITE_API_URL" ]; then \
      VITE_API_URL="$VITE_API_URL" npm run build; \
    else \
      npm run build; \
    fi

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
