# Agentic-AI-Home-Health
Learning project based on agentic AI and data engineering.

## Running the app (frontend + backend)

1. **Backend (FastAPI)**  
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload --port 8000
   ```
   API: http://localhost:8000 — Docs: http://localhost:8000/docs

2. **Frontend (Vite/React)**  
   ```bash
   cd health-app
   npm install
   npm run dev
   ```
   App: http://localhost:5173

The frontend uses `VITE_API_URL=http://localhost:8000` (see `health-app/.env`). CORS is configured so the backend accepts requests from the Vite dev server origin.
