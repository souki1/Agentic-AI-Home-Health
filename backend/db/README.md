# Database (PostgreSQL)

Schema and scripts for the Health Analytics backend.

## Setup

1. Create the database:

   ```bash
   createdb health_analytics
   ```

2. Apply the schema:

   ```bash
   psql -U postgres -d health_analytics -f db/schema.sql
   ```

   Or from the project root:

   ```bash
   cd backend
   psql -U postgres -d health_analytics -f db/schema.sql
   ```

3. Set `DATABASE_URL` in `backend/.env` to match your user and password, e.g.:

   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/health_analytics
   ```

- **db/drop.sql** – Drops `check_ins` and `users` (use for a clean reset before re-running schema.sql).

The FastAPI app can still run `Base.metadata.create_all()` on startup so tables are created if missing; the `.sql` files are the source of truth for the schema and for manual or CI deployment.
