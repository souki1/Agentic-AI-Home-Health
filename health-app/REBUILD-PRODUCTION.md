# Rebuild Production Frontend

If you're seeing "Got HTML instead of JSON" errors in production, the frontend was likely built without the correct `VITE_API_URL`. Follow these steps to rebuild and redeploy:

## Quick Fix: Rebuild with Cloud Build

From the **repo root**, run:

```bash
gcloud builds submit --config=health-app/cloudbuild.yaml . \
  --substitutions=_VITE_API_URL=https://backend-79306395653.northamerica-northeast1.run.app,_REGION=europe-west1,_SERVICE_NAME=agentic-ai-home-health
```

This will:
1. Build the Docker image with the correct `VITE_API_URL`
2. Push to Artifact Registry
3. Deploy to Cloud Run

## Verify the Build

After deployment, check the browser console on your production site. You should see:

```
[Config] Mode: production
[Config] VITE_API_URL: https://backend-79306395653.northamerica-northeast1.run.app
[Config] API Base URL: https://backend-79306395653.northamerica-northeast1.run.app
✅ Production API URL configured: https://backend-79306395653.northamerica-northeast1.run.app
```

If you see `VITE_API_URL: (not set)` or `API Base URL: /api`, the build didn't include the URL correctly.

## Manual Docker Build (Alternative)

If Cloud Build isn't available, build locally:

```bash
cd health-app

# Build with production backend URL
docker build \
  --build-arg VITE_API_URL=https://backend-79306395653.northamerica-northeast1.run.app \
  -t gcr.io/YOUR_PROJECT_ID/agentic-ai-home-health:latest \
  .

# Push to Artifact Registry
docker push gcr.io/YOUR_PROJECT_ID/agentic-ai-home-health:latest

# Deploy to Cloud Run
gcloud run deploy agentic-ai-home-health \
  --image gcr.io/YOUR_PROJECT_ID/agentic-ai-home-health:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated
```

## Check Current Deployment

To see what's currently deployed:

```bash
gcloud run services describe agentic-ai-home-health \
  --region europe-west1 \
  --format="value(status.url)"
```

## Verify Backend is Running

Make sure the backend is accessible:

```bash
curl https://backend-79306395653.northamerica-northeast1.run.app/health
```

Should return: `{"status":"ok","database":"connected"}`

## Common Issues

1. **Build arg not passed**: Make sure `--build-arg VITE_API_URL=...` is included
2. **Wrong service name**: Use `agentic-ai-home-health` (not `health-app`)
3. **Wrong region**: Use `europe-west1` for frontend
4. **CORS issues**: Backend CORS must allow frontend origin
