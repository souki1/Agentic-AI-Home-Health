# Cloud SQL connection (health-analytics-db)

- **Connection name:** `tech-83b89:us-central1:health-analytics-db`
- **Public IP:** `136.114.209.49`
- **Port:** `5432`
- **User:** `postgres`
- **Password:** `Root123.`
- **Database (app):** `health_analytics`

## 1. Cloud Run (use this in Secret Manager)

Backend must use the **Unix socket** URL so Cloud Run can connect:

```
postgresql://postgres:Root123.@/health_analytics?host=/cloudsql/tech-83b89:us-central1:health-analytics-db
```

- Secret name: `DATABASE_URL_SECRET`
- In Cloud Run: set env **DATABASE_URL** from this secret (version **latest**).
- In Cloud Run **Connections**, add Cloud SQL instance: **health-analytics-db**.

## 2. Direct connection (from your PC / Cloud Shell)

Use only if your IP is in Cloud SQL **Authorized networks**:

```
postgresql://postgres:Root123.@136.114.209.49:5432/health_analytics
```

To add your IP: Cloud SQL → health-analytics-db → **Connections** → **Authorized networks** → **Add network** (your IP or `0.0.0.0/0` for testing only).

## 3. Quick test from your machine (if authorized)

From `backend` folder:

```bash
python -c "
import psycopg2
conn = psycopg2.connect(
    host='136.114.209.49', port=5432, dbname='health_analytics',
    user='postgres', password='Root123.'
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM public.users')
print('Users count:', cur.fetchone()[0])
cur.close()
conn.close()
"
```
