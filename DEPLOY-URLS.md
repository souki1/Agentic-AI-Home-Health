# Your Cloud Run URLs

| Service  | URL |
|----------|-----|
| **Frontend** | https://agentic-ai-home-health-79306395653.europe-west1.run.app |
| **Backend**  | https://backend-79306395653.northamerica-northeast1.run.app |

---

## Fix 502 / CORS: One-time setup

### 1. Update backend CORS (allow frontend origin)

```bash
gcloud run services update backend \
  --region northamerica-northeast1 \
  --set-env-vars CORS_ORIGINS="https://agentic-ai-home-health-79306395653.europe-west1.run.app,http://localhost:5173"
```

### 2. Rebuild and redeploy frontend (bake in backend URL)

From **repo root**:

```bash
gcloud builds submit --config=health-app/cloudbuild.yaml . \
  --substitutions=_VITE_API_URL=https://backend-79306395653.northamerica-northeast1.run.app,_REGION=europe-west1,_SERVICE_NAME=agentic-ai-home-health
```

Or from **health-app/** with Docker:

```bash
cd health-app
docker build --build-arg VITE_API_URL=https://backend-79306395653.northamerica-northeast1.run.app -t gcr.io/YOUR_PROJECT_ID/agentic-ai-home-health:latest .
docker push gcr.io/YOUR_PROJECT_ID/agentic-ai-home-health:latest
gcloud run deploy agentic-ai-home-health --image gcr.io/YOUR_PROJECT_ID/agentic-ai-home-health:latest --region europe-west1 --platform managed --allow-unauthenticated
```

After step 1 and 2, the frontend at  
https://agentic-ai-home-health-79306395653.europe-west1.run.app/login  
will call the backend at  
https://backend-79306395653.northamerica-northeast1.run.app  
and CORS will allow it.
