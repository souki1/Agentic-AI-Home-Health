# Vertex AI setup for RAG chat (Cloud Run)

When `LLM_PROVIDER=vertex`, the backend uses **Vertex AI** (Gemini) for chat and for **text embeddings** (chat stored in SQL + pgvector). You must set **GOOGLE_CLOUD_PROJECT** and enable the Vertex AI API.

---

## 0. Cloud SQL: enable pgvector (for chat + vector search)

Chats are stored in PostgreSQL; embeddings use the **pgvector** extension in the same database.

1. In **Google Cloud Console** go to **SQL** → your **Cloud SQL** instance.
2. Open **Cloud Shell** or connect with any client (e.g. psql) as a user that can create extensions (e.g. `postgres` or a user with `cloudsqlsuperuser`).
3. Connect to the **database** your app uses (the one in `DATABASE_URL`).
4. Run once:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
5. After that, the app can create and use `conversations` and `chat_messages` (with `embedding vector(768)`).

If the app runs as a DB user that **cannot** create extensions, you must run the above as `postgres` (or another superuser) once. The app will then create the tables on startup.

---

---

## 1. Set the GCP project ID

The backend reads **GOOGLE_CLOUD_PROJECT** (your Google Cloud project ID, e.g. `tech-83b89` or `my-project-123`).

### Option A: Cloud Run (production)

Set it so the deployed service gets it:

- **GitHub Actions:** In the repo go to **Settings → Secrets and variables → Actions → Variables**. Add or set:
  - **GOOGLE_CLOUD_PROJECT** = your GCP project ID (e.g. `tech-83b89`).
  - (Optional) **GOOGLE_CLOUD_LOCATION** = `us-central1` (default).
- The workflow also falls back to **GCP_PROJECT_ID** if **GOOGLE_CLOUD_PROJECT** is not set.

- **Manual deploy:** When you run `gcloud run deploy`, pass the env var:
  ```bash
  gcloud run deploy backend ... --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,LLM_PROVIDER=vertex,VERTEX_MODEL=gemini-2.0-flash-001,GOOGLE_CLOUD_LOCATION=us-central1
  ```

- **Cloud Console:** Cloud Run → your **backend** service → **Edit & deploy new revision** → **Variables and secrets** → add **GOOGLE_CLOUD_PROJECT** = your project ID, **LLM_PROVIDER** = `vertex`, **VERTEX_MODEL** = `gemini-2.0-flash-001`, **GOOGLE_CLOUD_LOCATION** = `us-central1`.

### Option B: Local (prod-like)

If you run the backend locally with Vertex (e.g. using `.env.production`):

- In **backend/.env.production** set:
  ```env
  GOOGLE_CLOUD_PROJECT=your-gcp-project-id
  GOOGLE_CLOUD_LOCATION=us-central1
  LLM_PROVIDER=vertex
  VERTEX_MODEL=gemini-2.0-flash-001
  ```
- Replace `your-gcp-project-id` with your actual project ID (e.g. `tech-83b89`).

---

## 2. Enable Vertex AI API in GCP

1. Open [Google Cloud Console](https://console.cloud.google.com).
2. Select the **same project** as **GOOGLE_CLOUD_PROJECT**.
3. Go to **APIs & Services → Library** (or [Enable API](https://console.cloud.google.com/apis/library)).
4. Search for **Vertex AI API**.
5. Open it and click **Enable**.

(You may also need **Generative Language API** for Gemini; enabling **Vertex AI API** is the main one.)

---

## 3. Permissions (Cloud Run)

The Cloud Run service account must be allowed to use Vertex AI (chat **and** embeddings):

1. **IAM & Admin → IAM**.
2. Find the Cloud Run service account (e.g. `PROJECT_NUMBER-compute@developer.gserviceaccount.com`).
3. Add role **Vertex AI User** (`roles/aiplatform.user`) for that project. This covers both Gemini (chat) and the Text Embedding API (chat vector search).

Or in one command (replace `PROJECT_ID` and `SERVICE_ACCOUNT_EMAIL`):

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/aiplatform.user"
```

---

## 4. Quick check

- **Local with Ollama (no GCP needed):** In **backend/.env.local** use `LLM_PROVIDER=ollama` and run Ollama. No Vertex setup required.
- **Cloud Run with Vertex:** Set **GOOGLE_CLOUD_PROJECT** (and optionally **GOOGLE_CLOUD_LOCATION**) in the service, enable Vertex AI API, grant the service account **Vertex AI User**. Then redeploy or add the env vars and deploy a new revision.

After this, "Chat error: GOOGLE_CLOUD_PROJECT must be set for Vertex AI" should be resolved.
