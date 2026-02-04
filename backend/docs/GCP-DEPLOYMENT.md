# GCP Cloud Run Deployment Guide

This guide covers deploying both frontend and backend to Google Cloud Run.

---

## Architecture

- **Frontend**: Cloud Run service (health-app) - serves React SPA
- **Backend**: Cloud Run service (health-backend) - FastAPI + PostgreSQL
- **Database**: Cloud SQL (PostgreSQL) or managed PostgreSQL
- **Communication**: Frontend calls backend directly (no nginx proxy needed)

---

## Prerequisites

1. **GCP Project** with billing enabled
2. **Cloud SQL** instance (PostgreSQL) or external PostgreSQL
3. **Artifact Registry** repository (created automatically by Cloud Build)
4. **Service Account** with permissions:
   - Cloud Run Admin
   - Cloud SQL Client (if using Cloud SQL)
   - Secret Manager Secret Accessor (for secrets)

---

## Step 1: Set up Cloud SQL (PostgreSQL)

```bash
# Create Cloud SQL instance
gcloud sql instances create health-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create health_analytics --instance=health-db

# Create user
gcloud sql users create health_user \
  --instance=health-db \
  --password=YOUR_SECURE_PASSWORD

# Get connection name (needed for Cloud Run)
gcloud sql instances describe health-db --format="value(connectionName)"
# Output: PROJECT_ID:REGION:health-db
```

---

## Step 2: Create Secrets in Secret Manager

```bash
# Database URL (for Cloud SQL via Unix socket)
echo -n "postgresql://health_user:YOUR_PASSWORD@/health_analytics?host=/cloudsql/PROJECT_ID:REGION:health-db" | \
  gcloud secrets create DATABASE_URL_SECRET --data-file=-

# Or for external PostgreSQL:
echo -n "postgresql://user:pass@host:5432/health_analytics" | \
  gcloud secrets create DATABASE_URL_SECRET --data-file=-

# JWT Secret
echo -n "your-super-secret-jwt-key-change-in-production" | \
  gcloud secrets create SECRET_KEY_SECRET --data-file=-
```

---

## Step 3: Deploy Backend

```bash
cd backend

# Build and push
gcloud builds submit --config=cloudbuild.yaml .

# Or deploy manually:
gcloud run deploy health-backend \
  --image REGION-docker.pkg.dev/PROJECT_ID/cloud-run-source-deploy/health-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets DATABASE_URL=DATABASE_URL_SECRET:latest,SECRET_KEY=SECRET_KEY_SECRET:latest \
  --set-env-vars CORS_ORIGINS="https://health-app-XXX.run.app,https://health-app-XXX.run.app" \
  --add-cloudsql-instances PROJECT_ID:REGION:health-db \
  --service-account YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com

# Get backend URL
BACKEND_URL=$(gcloud run services describe health-backend --region us-central1 --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"
```

**Important**: Replace `YOUR_SERVICE_ACCOUNT` with a service account that has Cloud SQL Client role.

---

## Step 4: Deploy Frontend

**Option A: Direct API calls (recommended)**

Build with backend URL embedded:

```bash
cd health-app

# Build with backend URL
docker build --build-arg VITE_API_URL=$BACKEND_URL -t health-app-frontend .

# Push and deploy
gcloud builds submit --config=cloudbuild.yaml . \
  --substitutions=_VITE_API_URL=$BACKEND_URL

# Or deploy manually:
gcloud run deploy health-app \
  --image REGION-docker.pkg.dev/PROJECT_ID/cloud-run-source-deploy/health-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Option B: Nginx proxy (if you prefer `/api`)**

```bash
gcloud run deploy health-app \
  --image REGION-docker.pkg.dev/PROJECT_ID/cloud-run-source-deploy/health-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars BACKEND_URL=$BACKEND_URL
```

---

## Step 5: Update Backend CORS

After deploying frontend, get its URL and update backend CORS:

```bash
FRONTEND_URL=$(gcloud run services describe health-app --region us-central1 --format="value(status.url)")

gcloud run services update health-backend \
  --region us-central1 \
  --set-env-vars CORS_ORIGINS="$FRONTEND_URL,http://localhost:5173"
```

---

## Step 6: Initialize Database Schema

```bash
# Connect to Cloud SQL
gcloud sql connect health-db --user=health_user

# Run schema
\i db/schema.sql

# Or use Cloud SQL Proxy locally:
cloud-sql-proxy PROJECT_ID:REGION:health-db
# Then: psql -h 127.0.0.1 -U health_user -d health_analytics -f db/schema.sql
```

---

## Environment Variables Summary

### Backend (Cloud Run)

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Secret | PostgreSQL connection string |
| `SECRET_KEY` | Secret | JWT secret |
| `CORS_ORIGINS` | Env var | Comma-separated frontend URLs |
| `GOOGLE_CLOUD_PROJECT` | Env var | GCP project ID (for RAG) |
| `VECTOR_SEARCH_INDEX_ENDPOINT_ID` | Env var | Vector Search endpoint (for RAG) |
| `INSTANCE_CONNECTION_NAME` | Env var | Cloud SQL connection name (if using Cloud SQL) |

### Frontend (Cloud Run)

| Variable | Build arg | Description |
|----------|-----------|-------------|
| `VITE_API_URL` | Build time | Backend URL (Option A) |
| `BACKEND_URL` | Runtime | Backend URL for nginx proxy (Option B) |

---

## Troubleshooting

### 502 Bad Gateway

- **Check backend URL**: Ensure `BACKEND_URL` or `VITE_API_URL` points to the correct backend Cloud Run URL
- **Check CORS**: Backend must allow frontend origin in `CORS_ORIGINS`
- **Check backend logs**: `gcloud run services logs read health-backend --region us-central1`

### Database Connection Errors

- **Cloud SQL**: Ensure `INSTANCE_CONNECTION_NAME` is set and Cloud Run has Cloud SQL connection
- **External DB**: Ensure `DATABASE_URL` is correct and Cloud Run can reach it (VPC connector if needed)

### CORS Errors

- Add frontend URL to backend `CORS_ORIGINS` env var
- Ensure no trailing slashes in URLs

---

## CI/CD

See:
- `backend/cloudbuild.yaml` - Cloud Build config for backend
- `health-app/cloudbuild.yaml` - Cloud Build config for frontend
- `.github/workflows/backend-deploy.yml` - GitHub Actions for backend
- `.github/workflows/frontend-deploy.yml` - GitHub Actions for frontend
