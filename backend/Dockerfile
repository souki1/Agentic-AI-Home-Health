# Health Analytics Backend - FastAPI
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run uses PORT=8080; Docker Compose uses 8000
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

# Run uvicorn; Cloud Run sets PORT=8080 (read in Python for reliability)
CMD ["python", "-c", "import os; import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=int(os.environ.get('PORT', '8080')))"]
