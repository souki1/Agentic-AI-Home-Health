# Backend (Health Analytics)

Simple FastAPI + SQLite backend. Optional: use PostgreSQL by setting `DATABASE_URL` in `.env`.

## Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Or without venv (if packages are installed): `uvicorn main:app --reload --port 8000`

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

## Env

Copy `.env.example` to `.env`. Defaults use SQLite; no extra setup.

## Endpoints

- `GET /health` — liveness
- `POST /auth/register` — register (email, password, role)
- `POST /auth/login` — login (JSON: email, password)
- `GET /auth/me` — current user (Bearer)
- `GET /patients`, `GET /patients/{id}`
- `GET /check-ins?patient_id=...`, `POST /check-ins`, `POST /check-ins/sync-analytics`
- `POST /seed` — add demo patients
