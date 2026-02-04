# Health Analytics Backend (FastAPI + PostgreSQL)

Backend for the health-app frontend. PostgreSQL only; schema is defined in `.sql` files.

## Database (.sql)

1. Create the database:

   ```bash
   createdb health_analytics
   ```

2. Apply the schema:

   ```bash
   cd backend
   psql -U postgres -d health_analytics -f db/schema.sql
   ```

See **db/README.md** for more detail. Tables: `users`, `check_ins`.

## Backend setup

1. Copy env and set your PostgreSQL URL:

   ```bash
   cd backend
   copy .env.example .env
   ```

   Edit `.env` and set:

   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/health_analytics
   SECRET_KEY=your-secret-key
   ```

2. Install and run:

   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

   Use `main:app` (not `app.main:app`). The app can create tables on startup if they don’t exist; **db/schema.sql** is the source of truth.

## API (matches frontend)

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Register (email, password, role, name?) |
| POST | /auth/login | Login → `{ token, user }` |
| GET | /auth/me | Current user (Bearer) |
| GET | /patients | List patients (admin: all; patient: self) |
| GET | /patients/{id} | Get one patient |
| GET | /check-ins?patient_id= | List check-ins (with scores) |
| POST | /check-ins | Create check-in |
| POST | /check-ins/sync-analytics | No-op |

Docs: http://localhost:8000/docs

## If GET /health returns 503

The API is up but **PostgreSQL is not reachable**. Do the following:

1. **Start PostgreSQL**  
   - Windows: open Services, start the "postgresql" service, or run `pg_ctl start` from your PostgreSQL bin folder.  
   - Or start it from pgAdmin / your PostgreSQL installer.

2. **Create the database** (if you haven’t):
   ```bash
   createdb -U postgres health_analytics
   ```
   Or in **psql**: `CREATE DATABASE health_analytics;`

3. **Check `backend/.env`**  
   Set the URL to match your real user and password:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/health_analytics
   ```
   If PostgreSQL runs on another port, change `5432`.

4. **Restart the backend** and call **GET /health** again. When it connects you’ll see `"database": "connected"`.
