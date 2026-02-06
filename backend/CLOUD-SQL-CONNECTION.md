# Cloud SQL (PostgreSQL) – run SQL and connect Cloud Run

- **Connection name:** `tech-83b89:us-central1:health-analytics-db`
- **Public IP:** `136.114.209.49`
- **Port:** `5432`
- **User:** `postgres`
- **Password:** `Root123.`
- **Database (app):** `health_analytics`

---

## Part 1: Run SQL in Cloud SQL (PostgreSQL)

### Option A: Google Cloud Console (no local setup)

1. Open [Cloud Console](https://console.cloud.google.com) → **SQL** → select instance **health-analytics-db**.
2. Open **Cloud SQL Studio** (or the instance → **Connect** → **Open Cloud Shell**).
3. Or use **Query** tab / **Cloud SQL Studio** to run SQL in the browser.

### Option B: `gcloud sql connect` (Cloud Shell or local with Cloud SQL Proxy)

```bash
gcloud sql connect health-analytics-db --user=postgres --database=health_analytics
# Enter password when prompted, then run SQL:
# SELECT * FROM users;
# \q to quit
```

### Option C: From your PC (IP must be in Authorized networks)

**Using `psql`** (if installed):

```bash
psql "postgresql://postgres:Root123.@136.114.209.49:5432/health_analytics" -c "SELECT id, email, role FROM users;"
```

**Using Python** (from `backend` folder):

```bash
python -c "
import psycopg2
conn = psycopg2.connect(
    host='136.114.209.49', port=5432, dbname='health_analytics',
    user='postgres', password='Root123.'
)
cur = conn.cursor()
cur.execute('SELECT id, email, role FROM users')
for r in cur.fetchall():
    print(r)
cur.close()
conn.close()
"
```

To allow your IP: **Cloud SQL** → **health-analytics-db** → **Connections** → **Authorized networks** → **Add network**.

---

## Part 2: Connect Cloud Run to PostgreSQL (Cloud SQL)

Cloud Run talks to Cloud SQL via a **Unix socket**, not the public IP. Do the following in the **same GCP project** where the backend Cloud Run service runs (e.g. where the service URL is `backend-79306395653.europe-west1.run.app`).

### Step 1: Create the secret (DATABASE_URL for Cloud Run)

1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager).
2. **Create secret** → Name: **`DATABASE_URL_SECRET`**.
3. Secret value = this **exact** string (Unix socket URL; change password if needed):

   ```
   postgresql://postgres:Root123.@/health_analytics?host=/cloudsql/tech-83b89:us-central1:health-analytics-db
   ```

4. Save. Use version **latest** when wiring to Cloud Run.

### Step 2: Wire the secret into Cloud Run

The GitHub Actions workflow already does this if the secret exists:

- `--set-secrets DATABASE_URL=DATABASE_URL_SECRET:latest`
- `--add-cloudsql-instances tech-83b89:us-central1:health-analytics-db`

So you need to:

1. Ensure **DATABASE_URL_SECRET** exists in the **same project** as the Cloud Run service (see Step 1).
2. Redeploy the backend (push to the branch that runs the workflow, or run the deploy job manually).

If you deploy with `gcloud` yourself, run:

```bash
gcloud run deploy backend \
  --image YOUR_IMAGE_URL \
  --region europe-west1 \
  --set-secrets DATABASE_URL=DATABASE_URL_SECRET:latest,SECRET_KEY=SECRET_KEY_SECRET:latest \
  --add-cloudsql-instances tech-83b89:us-central1:health-analytics-db
```

### Step 3: Confirm Cloud Run has the Cloud SQL connection

- **Cloud Run** → your **backend** service → **Connections** (or **Configuration** → **Connections**).
- The Cloud SQL instance **tech-83b89:us-central1:health-analytics-db** (or **health-analytics-db**) should be listed. If not, add it and redeploy.

### Step 4: Test

- Call login: `POST https://backend-79306395653.europe-west1.run.app/api/auth/login` with a new email.
- Then run SQL in Cloud SQL (Part 1) and check that the new user exists in the `users` table.

---

## Reference: connection strings

| Use case | URL |
|----------|-----|
| **Cloud Run** (Secret Manager) | `postgresql://postgres:Root123.@/health_analytics?host=/cloudsql/tech-83b89:us-central1:health-analytics-db` |
| **Direct (PC / Cloud Shell)** | `postgresql://postgres:Root123.@136.114.209.49:5432/health_analytics` |
