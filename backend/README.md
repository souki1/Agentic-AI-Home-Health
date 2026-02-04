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

## RAG (Vertex AI)

The backend can run a **RAG pipeline** using GCP Vertex AI: chunking, embeddings, Vector Search, and Gemini for answers.

**→ How to connect to Google Cloud:** see **[docs/GCP-CONNECTION.md](docs/GCP-CONNECTION.md)** (auth, APIs, `.env`).

1. **Configure GCP** in `.env`:
   - `GOOGLE_CLOUD_PROJECT` – your GCP project ID  
   - `VECTOR_SEARCH_INDEX_ENDPOINT_ID` – deployed Vector Search endpoint  
   - Optional: `GOOGLE_CLOUD_LOCATION`, `VERTEX_EMBEDDING_MODEL`, `VERTEX_EMBEDDING_DIMENSIONS`, `VERTEX_RAG_LLM_MODEL`, `VECTOR_SEARCH_TOP_K`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`

2. **Chunk lookup**: the pipeline needs a mapping from chunk ID → text. Either:
   - Set `RAG_CHUNK_STORE_PATH` to a JSON file path (object `{"chunk_id": "text"}` or array `[{"id": "...", "text": "..."}]`). The app loads it at startup.  
   - Or populate the in-memory store programmatically (e.g. from your index-build step).

3. **Endpoints**:
   - **GET /rag/status** – whether RAG is configured and chunk count (no auth).  
   - **POST /rag/query** – body `{ "question": "...", "top_k": 10 }`; returns `{ "answer": "...", "sources": [{ "chunk_id", "text" }] }` (requires auth).  
   - **POST /rag/ingest** – body `{ "text": "...", "source": "guidelines", "title": "..." }`; chunks and stores document in DB (admin only).

4. **Ingest health documents**:
   ```bash
   python scripts/ingest_health_documents.py
   ```
   This loads example health guidelines (home care, chronic conditions, post-surgery) into the `rag_chunks` table.

5. **Build Vector Search index**:
   ```bash
   python scripts/build_vector_index.py
   ```
   This reads chunks from the database, embeds them with Vertex AI, and writes `rag_index_embeddings.jsonl`. Upload this to GCS, then create/update your Vector Search index in the Vertex AI console pointing to the GCS file. Deploy the index to an endpoint and set `VECTOR_SEARCH_INDEX_ENDPOINT_ID` in `.env`.

6. **Query RAG**: After the index is deployed, use **POST /rag/query** to ask questions about health records and guidelines. The pipeline retrieves relevant chunks, builds a prompt, and generates answers using Gemini.

**Note**: Chunks are stored in the `rag_chunks` PostgreSQL table. The lookup checks the database first, then falls back to in-memory/file store. Prompting and evaluation can be done in **Vertex AI Studio** (see project docs if present).
