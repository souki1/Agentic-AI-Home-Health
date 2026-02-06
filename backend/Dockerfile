# Health Analytics Backend - FastAPI
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run injects PORT=8080; app must listen on 0.0.0.0:PORT
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

# Listen on PORT so Cloud Run health check passes. DB is lazy-loaded so server can start even if DATABASE_URL is not yet available.
CMD ["python", "-c", "import os; port = int(os.environ.get('PORT', '8080')); print('Listening on', port); import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=port)"]
