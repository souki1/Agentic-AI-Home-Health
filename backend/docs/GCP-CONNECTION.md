# How to Connect the Backend to Google Cloud (Vertex AI RAG)

Follow these steps to connect your backend to GCP so the RAG pipeline (embeddings, Vector Search, Gemini) works.

---

## No API key for Vector Search

**Vertex AI Vector Search does not use an API key.** You do **not** put a "Vector Search API key" in `.env`.

Authentication uses:

- **Project ID** (`GOOGLE_CLOUD_PROJECT`)
- **Vector Search endpoint ID** (`VECTOR_SEARCH_INDEX_ENDPOINT_ID`) — this is the ID of your *deployed index endpoint* in the Vertex AI console, not a secret key
- **Google credentials**: either `gcloud auth application-default login` (local) or `GOOGLE_APPLICATION_CREDENTIALS` pointing to a service account JSON (server)

So in `.env` you only set `GOOGLE_CLOUD_PROJECT` and `VECTOR_SEARCH_INDEX_ENDPOINT_ID` (and optional settings). No separate Vector Search API key is used or needed.

---

## 1. Install Google Cloud CLI (if you don’t have it)

- **Windows**: [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (run the installer).
- **macOS**: `brew install google-cloud-sdk`
- **Linux**: See [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install)

Then open a new terminal and run:

```bash
gcloud init
```

Sign in with your Google account and pick (or create) a **project**. Note the **Project ID** (e.g. `my-project-123`).

---

## 2. Create or select a GCP project

- In [Google Cloud Console](https://console.cloud.google.com/), create a project or select an existing one.
- Copy the **Project ID** (not the display name). You’ll use it in `.env` as `GOOGLE_CLOUD_PROJECT`.

---

## 3. Enable required APIs

In the Cloud Console, go to **APIs & Services → Library** and enable:

- **Vertex AI API**
- **Vertex AI Vector Search API** (if you use Vector Search)

Or use the CLI (replace `YOUR_PROJECT_ID` with your project ID):

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com
```

---

## 4. Authenticate so the backend can call Google

The backend uses **Application Default Credentials (ADC)**. Google client libraries (Vertex AI, Vector Search) read them automatically.

### Option A: Local development (your own user)

Run once:

```bash
gcloud auth application-default login
```

A browser window opens; sign in with the same Google account that has access to the project. Credentials are saved locally (e.g. under your user folder). The backend will use them when you run `uvicorn` on your machine.

### Option B: Production / server (service account)

1. In Cloud Console go to **IAM & Admin → Service accounts** and create a service account (e.g. `backend-rag`).
2. Grant it roles:
   - **Vertex AI User** (Vertex AI API, embeddings, Gemini)
   - **Vertex AI Vector Search User** (if you use Vector Search)
   - Optionally **Storage** if you read index/chunk data from GCS.
3. Create a **key** (JSON) and download it.
4. On the server, set the environment variable **before** starting the backend:

   **Windows (PowerShell):**
   ```powershell
   $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\your-service-account-key.json"
   ```

   **Windows (CMD):**
   ```cmd
   set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your-service-account-key.json
   ```

   **Linux / macOS:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json
   ```

5. Start the backend (e.g. `uvicorn main:app --port 8000`). It will use this key to talk to Vertex AI.

---

## 5. Set backend `.env` for RAG

In `backend/.env` add (use your real values):

```env
# Required for RAG
GOOGLE_CLOUD_PROJECT=your-project-id
VECTOR_SEARCH_INDEX_ENDPOINT_ID=your-endpoint-id

# Optional (defaults shown)
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_EMBEDDING_MODEL=text-embedding-005
VERTEX_EMBEDDING_DIMENSIONS=768
VERTEX_RAG_LLM_MODEL=gemini-1.5-flash-001
VECTOR_SEARCH_TOP_K=10
```

- **GOOGLE_CLOUD_PROJECT**: Your GCP Project ID from step 2.
- **VECTOR_SEARCH_INDEX_ENDPOINT_ID**: The ID of your **deployed** Vector Search index endpoint (from Vertex AI → Vector Search in the console). If you haven’t built an index yet, create and deploy one first; then put its endpoint ID here.

Pydantic Settings reads these from the environment; names in `.env` must be **UPPER_SNAKE_CASE** (e.g. `GOOGLE_CLOUD_PROJECT`).

---

## 6. Verify the connection

1. Start the backend from the `backend` folder:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. Call the RAG status endpoint:
   ```bash
   curl http://localhost:8000/rag/status
   ```

   - If you see `"configured": true`, the backend has the required env vars and is ready to call GCP (assuming the Vector Search endpoint exists and ADC is set).
   - If you see `503` and `"configured": false`, check that `GOOGLE_CLOUD_PROJECT` and `VECTOR_SEARCH_INDEX_ENDPOINT_ID` are set in `.env` and that you restarted the server after changing `.env`.

3. If you get auth errors when calling **POST /rag/query**, ensure:
   - You ran `gcloud auth application-default login` (local) or set `GOOGLE_APPLICATION_CREDENTIALS` (server).
   - The project ID in `.env` matches the project where the APIs are enabled and the Vector Search endpoint lives.

---

## Summary

| Step | What to do |
|------|------------|
| 1 | Install `gcloud` and run `gcloud init` |
| 2 | Create/select a project and note the **Project ID** |
| 3 | Enable **Vertex AI API** (and Vector Search if needed) |
| 4 | **Local:** `gcloud auth application-default login` **Server:** set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON key |
| 5 | In `backend/.env` set `GOOGLE_CLOUD_PROJECT` and `VECTOR_SEARCH_INDEX_ENDPOINT_ID` (and optional RAG vars) |
| 6 | Restart the backend and call **GET /rag/status** to confirm |

After this, the backend is connected to Google Cloud and can use Vertex AI for the RAG pipeline.
