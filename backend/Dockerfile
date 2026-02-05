# Health Analytics Backend - FastAPI
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# FastAPI on port 8000
ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

# Run uvicorn (main:app from main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
