# Backend Environment Variables

All connection URLs and configuration come from environment variables (via `.env` file or Cloud Run env vars/secrets).

---

## Database Connection

**Option A: Direct connection string (DATABASE_URL)**

```env
DATABASE_URL=postgresql://user:password@host:5432/health_analytics
```

**Option B: Cloud SQL via Unix socket** (recommended for Cloud Run)

```env
INSTANCE_CONNECTION_NAME=project-id:region:instance-name
DB_USER=health_user
DB_PASS=your-password  # Set via Secret Manager in production
DB_NAME=health_analytics
```

If `INSTANCE_CONNECTION_NAME` is set, the backend uses Option B (Unix socket) and ignores `DATABASE_URL`.

---

## Authentication

```env
SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # Optional, default 7 days
```

---

## CORS (Frontend Origins)

```env
CORS_ORIGINS=http://localhost:5173,https://your-frontend.run.app
```

Comma-separated list of allowed frontend URLs. Required for Cloud Run.

---

## GCP Vertex AI RAG (Optional)

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
VECTOR_SEARCH_INDEX_ENDPOINT_ID=your-endpoint-id
VECTOR_SEARCH_INDEX_ID=your-index-id
VERTEX_EMBEDDING_MODEL=text-embedding-005
VERTEX_EMBEDDING_DIMENSIONS=768
VERTEX_RAG_LLM_MODEL=gemini-1.5-flash-001
VECTOR_SEARCH_TOP_K=10
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_CHUNK_STORE_PATH=./rag_chunks.json  # Optional
```

---

## Complete Example (.env for local dev)

```env
# Database (local PostgreSQL)
DATABASE_URL=postgresql://postgres:root@localhost:5432/health_analytics

# Auth
SECRET_KEY=your-local-secret-key

# CORS (local frontend)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# GCP RAG (optional)
GOOGLE_CLOUD_PROJECT=tech-83b89
GOOGLE_CLOUD_LOCATION=us-central1
VECTOR_SEARCH_INDEX_ENDPOINT_ID=your-endpoint-id
```

---

## Cloud Run Deployment

Set these via `gcloud run deploy`:

**Secrets (sensitive):**
- `DATABASE_URL` (if using Option A)
- `SECRET_KEY`
- `DB_PASS` (if using Cloud SQL Option B)

**Environment variables:**
- `CORS_ORIGINS`
- `INSTANCE_CONNECTION_NAME` (if using Cloud SQL)
- `DB_USER`, `DB_NAME` (if using Cloud SQL)
- `GOOGLE_CLOUD_PROJECT`, `VECTOR_SEARCH_INDEX_ENDPOINT_ID`, etc. (for RAG)

See `cloudbuild.yaml` for the exact deployment configuration.
