#!/bin/sh
# Entrypoint script to substitute backend URL in nginx config

set -e

# Default backend URL (can be overridden via env var)
BACKEND_URL=${BACKEND_URL:-http://localhost:8000}

# Replace placeholder in nginx config
sed -i "s|set \$backend_url.*|set \$backend_url \"${BACKEND_URL}\";|g" /etc/nginx/nginx.conf

# Start nginx
exec nginx -g "daemon off;"
