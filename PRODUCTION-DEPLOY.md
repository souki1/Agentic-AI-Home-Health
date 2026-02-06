# Production Deployment Guide – GCP Cloud Run

Deploy **frontend** and **backend** as **separate** Cloud Run services. This gives you independent scaling, easier updates, and clearer architecture.

---

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Frontend (React)  │────▶│   Backend (FastAPI)  │────▶│  Cloud SQL (PostgreSQL) │
│   Cloud Run         │     │   Cloud Run          │     │                      │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

- **Frontend**: SPA served by Cloud Run (static build)
- **Backend**: FastAPI on Cloud Run
- **Database**: Cloud SQL PostgreSQL (managed, persistent)

---

## Prerequisites

1. **GCP project** – [Create one](https://console.cloud.google.com/projectcreate)
2. **Billing** – Cloud Run and Cloud SQL require billing
3. **gcloud CLI** – [Install](https://cloud.google.com/sdk/docs/install)

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## Step 1: Enable APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## Step 2: Create Cloud SQL (PostgreSQL)

```bash
# Create instance (takes 5–10 min)
gcloud sql instances create health-analytics-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create health_analytics --instance=health-analytics-db

# Create user
gcloud sql users create health_user \
  --instance=health-analytics-db \
  --password=YOUR_SECURE_PASSWORD
```

Connection name (you’ll need it):

```bash
gcloud sql instances describe health-analytics-db --format="value(connectionName)"
# e.g. project-id:us-central1:health-analytics-db
```

---

## Step 3: Create Secrets

```bash
# DATABASE_URL for Cloud SQL (use Unix socket from Cloud Run)
echo -n "postgresql://health_user:YOUR_SECURE_PASSWORD@/health_analytics?host=/cloudsql/PROJECT_ID:us-central1:health-analytics-db" | \
  gcloud secrets create DATABASE_URL_SECRET --data-file=-

# Or for public IP:
# postgresql://health_user:PASSWORD@/health_analytics?host=PRIVATE_IP

# SECRET_KEY for JWT
echo -n "your-very-long-random-secret-key-change-this" | \
  gcloud secrets create SECRET_KEY_SECRET --data-file=-
```

Cloud Run connects via Unix socket. Use the connection name from Step 2 in the `host=/cloudsql/...` part.

---

## Step 4: Deploy Backend First

Deploy the backend before the frontend so you have the backend URL for the frontend build.

```bash
# Build and push
cd backend
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/cloud-run-source-deploy/backend:latest

# Deploy (replace YOUR_INSTANCE_CONNECTION_NAME)
gcloud run deploy backend \
  --image REGION-docker.pkg.dev/PROJECT_ID/cloud-run-source-deploy/backend:latest \
  --region northamerica-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --add-cloudsql-instances YOUR_INSTANCE_CONNECTION_NAME \
  --set-secrets DATABASE_URL=DATABASE_URL_SECRET:latest,SECRET_KEY=SECRET_KEY_SECRET:latest \
  --set-env-vars "CORS_ORIGINS=https://agentic-ai-home-health-79306395653.europe-west1.run.app,http://localhost:5173"
```

Copy the backend URL from the deploy output, e.g.  
`https://backend-XXXXXXXXXX.run.app`.

---

## Step 5: Deploy Frontend

Use the backend URL from Step 4 as `VITE_API_URL`:

```bash
cd health-app
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_VITE_API_URL=https://YOUR_BACKEND_URL,_REGION=europe-west1
```

Or build and deploy manually:

```bash
cd health-app
docker build --build-arg VITE_API_URL=https://YOUR_BACKEND_URL -t gcr.io/PROJECT_ID/agentic-ai-home-health:latest .
docker push gcr.io/PROJECT_ID/agentic-ai-home-health:latest
gcloud run deploy agentic-ai-home-health \
  --image gcr.io/PROJECT_ID/agentic-ai-home-health:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated
```

---

## Step 6: Point CORS to Your Frontend URL

After the frontend is deployed, set CORS on the backend:

```bash
gcloud run services update backend \
  --region northamerica-northeast1 \
  --set-env-vars "CORS_ORIGINS=https://YOUR_FRONTEND_URL,http://localhost:5173"
```

---

## Deploy Order Summary

| Order | Service | Why |
|-------|---------|-----|
| 1 | Backend | Needs to exist so you have its URL |
| 2 | Frontend | Build uses backend URL in `VITE_API_URL` |
| 3 | CORS | Backend must allow your frontend origin |

---

## GitHub Actions (Optional)

For automatic deploys on push:

1. Repo → **Settings → Secrets and variables → Actions**
2. Add **Variables**:
   - `GCP_PROJECT_ID`
   - `GCP_REGION` (e.g. `europe-west1`)
   - `VITE_API_URL` (backend URL, e.g. `https://backend-xxx.run.app`)
3. Add **Secrets**:
   - `GOOGLE_APPLICATION_CREDENTIALS_JSON` (base64 service account key)

Or use **Workload Identity** with `GCP_WORKLOAD_IDENTITY_PROVIDER` and `GCP_SERVICE_ACCOUNT`.

---

## Troubleshooting

| Issue | Action |
|-------|--------|
| 502 Bad Gateway | Check backend logs; ensure `PORT` (8080) is used |
| CORS errors | Add frontend URL to backend `CORS_ORIGINS` |
| DB connection fails | Confirm Cloud SQL instance and connection name; check secrets |
| Frontend calls wrong API | Rebuild frontend with correct `VITE_API_URL` |

---

## Quick Reference

```bash
# Backend
gcloud run deploy backend --image ... --region northamerica-northeast1 --add-cloudsql-instances PROJECT:REGION:INSTANCE

# Frontend
gcloud builds submit --config=health-app/cloudbuild.yaml --substitutions=_VITE_API_URL=https://backend-xxx.run.app
```
