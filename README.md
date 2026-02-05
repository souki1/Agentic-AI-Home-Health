# Agentic-AI-Home-Health
Learning project based on agentic AI and data engineering.

## Running the app (frontend + backend)

1. **Backend (FastAPI + PostgreSQL)**  
   Create DB: `createdb health_analytics` (or `CREATE DATABASE health_analytics;` in psql).  
   Then:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   Or: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
   API: http://localhost:8000 — Docs: http://localhost:8000/docs

2. **Frontend (Vite/React)**  
   ```bash
   cd health-app
   npm install
   npm run dev
   ```
   App: http://localhost:5173

The frontend uses `VITE_API_URL=http://localhost:8000` (see `health-app/.env.example` — copy to `.env.local`). CORS is set for localhost so the backend accepts requests from the Vite dev server.
