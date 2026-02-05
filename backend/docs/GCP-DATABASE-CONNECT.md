# Connect Database to GCP (Cloud SQL)

This guide connects your backend to **Cloud SQL for PostgreSQL** so the Cloud Run backend uses a managed database.

**Your instance:** `tech-83b89:us-central1:healtappdb` (project: tech-83b89, region: us-central1).

---

## Fix: "database unreachable" / socket not found → Use DATABASE_URL (TCP)

If the backend returns **"connection to server on socket ... No such file or directory"**, use a **TCP connection** instead of the Unix socket. The backend prefers `DATABASE_URL` when set.

### 1. Get your instance public IP

- GCP Console → **SQL** → open instance **healtappdb** → copy **Public IP address**.
- If there is no public IP: **Edit** the instance → **Connections** → enable **Public IP** → save.

### 2. Allow Cloud Run to connect (authorized network)

- On the same instance → **Connections** → **Networking**.
- **Add network**: Name e.g. `cloud-run`, Network `0.0.0.0/0` (or restrict to your Cloud Run region later). Save.

### 3. Create or update the DATABASE_URL secret

Use this format (replace `YOUR_PUBLIC_IP` and `YOUR_DB_PASSWORD`):

```
postgresql://health_user:YOUR_DB_PASSWORD@YOUR_PUBLIC_IP:5432/health_analytics?sslmode=require
```

**Create the secret (first time):**

```bash
gcloud config set project tech-83b89
echo -n "postgresql://health_user:YOUR_DB_PASSWORD@YOUR_PUBLIC_IP:5432/health_analytics?sslmode=require" | gcloud secrets create DATABASE_URL_SECRET --data-file=-
```

**Update the secret (if it already exists):**

```bash
echo -n "postgresql://health_user:YOUR_DB_PASSWORD@YOUR_PUBLIC_IP:5432/health_analytics?sslmode=require" | gcloud secrets versions add DATABASE_URL_SECRET --data-file=-
```

### 4. Redeploy the backend

So Cloud Run uses the new code (which prefers `DATABASE_URL`) and the secret:

```bash
# From repo root
gcloud builds submit --config=backend/cloudbuild.yaml .
```

Or push to `main` if you use GitHub Actions for the backend. After deploy, `/health` should return `{"status":"ok","database":"connected"}`.

---

### Quick commands for this instance

```bash
# 1. Create DB user and database (if not done)
gcloud config set project tech-83b89
gcloud sql databases create health_analytics --instance=healtappdb
gcloud sql users create health_user --instance=healtappdb --password=YOUR_DB_PASSWORD

# 2. Store DB password in Secret Manager (required for Cloud Run)
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create DB_PASS_SECRET --data-file=-

# 3. Grant Cloud Run access to Cloud SQL
PROJECT_NUMBER=$(gcloud projects describe tech-83b89 --format="value(projectNumber)")
gcloud projects add-iam-policy-binding tech-83b89 \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# 4. Deploy/update backend with Cloud SQL (cloudbuild uses tech-83b89:us-central1:healtappdb)
# From repo root:
gcloud builds submit --config=backend/cloudbuild.yaml .
```

---

## Option A: Cloud SQL + Unix socket (recommended for Cloud Run)

Cloud Run connects to Cloud SQL via a **Unix socket**. No public IP needed.

### Step 1: Create a Cloud SQL instance

```bash
# Set your project and region (use same region as Cloud Run for lower latency)
export PROJECT_ID=your-project-id
export REGION=northamerica-northeast1   # or europe-west1, etc.

gcloud config set project $PROJECT_ID

# Create PostgreSQL 15 instance (smallest tier for dev)
gcloud sql instances create health-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password=CHOOSE_A_STRONG_ROOT_PASSWORD
```

For production, use a larger tier (e.g. `db-g1-small`) and consider High Availability.

### Step 2: Create the database and user

```bash
# Create database
gcloud sql databases create health_analytics --instance=health-db

# Create a dedicated user (not root)
gcloud sql users create health_user \
  --instance=health-db \
  --password=CHOOSE_A_STRONG_PASSWORD
```

### Step 3: Get the instance connection name

```bash
gcloud sql instances describe health-db --format="value(connectionName)"
```

Example output: `your-project-id:northamerica-northeast1:health-db`  
Save this as `INSTANCE_CONNECTION_NAME`.

### Step 4: Run the schema (create tables)

**Option 4a: From your machine using Cloud SQL Auth Proxy**

```bash
# Install Cloud SQL Auth Proxy: https://cloud.google.com/sql/docs/postgres/connect-auth-proxy

# Start proxy (replace with your connection name)
cloud-sql-proxy "PROJECT_ID:REGION:health-db" &

# Connect and run schema
PGPASSWORD=CHOOSE_A_STRONG_PASSWORD psql -h 127.0.0.1 -U health_user -d health_analytics -f backend/db/schema.sql

# Stop proxy when done
pkill cloud-sql-proxy
```

**Option 4b: From Cloud Shell (no proxy needed)**

1. In GCP Console, open **Cloud Shell**.
2. Upload `backend/db/schema.sql` or paste its contents.
3. Run:
   ```bash
   gcloud sql connect health-db --user=health_user --database=health_analytics
   ```
4. When prompted, enter the password for `health_user`.
5. In the `psql` prompt:
   ```sql
   \i schema.sql
   ```
   Or paste the contents of `schema.sql` and run.

### Step 5: Grant the Cloud Run service account access to Cloud SQL

```bash
# Get the default Cloud Run service account (or your custom one)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export CLOUD_RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant Cloud SQL Client role so Cloud Run can connect
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${CLOUD_RUN_SA}" \
  --role="roles/cloudsql.client"
```

If you use a **custom** service account for Cloud Run, use that email instead of `CLOUD_RUN_SA`.

### Step 6: Store the database password in Secret Manager

```bash
# Create secret for DB password (used with Unix socket)
echo -n "CHOOSE_A_STRONG_PASSWORD" | gcloud secrets create DB_PASS_SECRET --data-file=-

# Optional: also create SECRET_KEY for JWT if not done yet
echo -n "your-jwt-secret-key" | gcloud secrets create SECRET_KEY_SECRET --data-file=-
```

### Step 7: Deploy backend with Cloud SQL connection

Update your Cloud Run service to use the instance and secrets:

```bash
export INSTANCE_CONNECTION_NAME="PROJECT_ID:REGION:health-db"   # from Step 3

gcloud run services update backend \
  --region=northamerica-northeast1 \
  --add-cloudsql-instances=$INSTANCE_CONNECTION_NAME \
  --set-env-vars="INSTANCE_CONNECTION_NAME=${INSTANCE_CONNECTION_NAME},DB_USER=health_user,DB_NAME=health_analytics" \
  --set-secrets="DB_PASS=DB_PASS_SECRET:latest,SECRET_KEY=SECRET_KEY_SECRET:latest,DATABASE_URL=DATABASE_URL_SECRET:latest"
```

**Note:** If you already use `DATABASE_URL` from a secret, you can keep it for backward compatibility, but when `INSTANCE_CONNECTION_NAME` is set, the backend will use the Unix socket URL built from `DB_USER`, `DB_PASS`, `DB_NAME` (see `backend/database.py`). So you must set `DB_PASS` (via secret) and the env vars above.

Minimal update (only add Cloud SQL + DB credentials):

```bash
# Replace with your actual connection name, e.g. myproject:northamerica-northeast1:health-db
INSTANCE_CONNECTION_NAME="your-project-id:northamerica-northeast1:health-db"

gcloud run services update backend \
  --region=northamerica-northeast1 \
  --add-cloudsql-instances=$INSTANCE_CONNECTION_NAME \
  --set-env-vars="INSTANCE_CONNECTION_NAME=${INSTANCE_CONNECTION_NAME},DB_USER=health_user,DB_NAME=health_analytics" \
  --set-secrets="DB_PASS=DB_PASS_SECRET:latest"
```

Ensure `DATABASE_URL_SECRET` and `SECRET_KEY_SECRET` are still set if your deploy used them; add `DB_PASS=DB_PASS_SECRET:latest` so the app can build the socket URL.

### Step 8: Update Cloud Build (optional)

To have future deploys add the Cloud SQL instance automatically, set the substitution in `backend/cloudbuild.yaml`:

```yaml
substitutions:
  _CLOUDSQL_INSTANCE: "your-project-id:northamerica-northeast1:health-db"
```

And in the deploy step, add back:

```yaml
- --add-cloudsql-instances
- ${_CLOUDSQL_INSTANCE}
```

Then pass the DB password via Secret Manager as above (Cloud Build doesn’t need to change; only Cloud Run service config).

---

## Option B: Use DATABASE_URL only (public IP or proxy)

If you prefer a single connection string (e.g. for an existing Cloud SQL instance with public IP or via proxy):

1. Build the connection string:
   - **Public IP:**  
     `postgresql://health_user:PASSWORD@PUBLIC_IP:5432/health_analytics`
   - **Private IP / VPC:**  
     Use the private IP and ensure Cloud Run has a VPC connector if needed.

2. Store it in Secret Manager:
   ```bash
   echo -n "postgresql://health_user:PASSWORD@PUBLIC_IP:5432/health_analytics" | \
     gcloud secrets create DATABASE_URL_SECRET --data-file=-
   ```

3. Deploy Cloud Run with:
   ```bash
   gcloud run services update backend \
     --region=northamerica-northeast1 \
     --set-secrets="DATABASE_URL=DATABASE_URL_SECRET:latest,SECRET_KEY=SECRET_KEY_SECRET:latest"
   ```

4. Do **not** set `INSTANCE_CONNECTION_NAME` so the backend uses `DATABASE_URL` from the secret.

For **public IP**, enable it on the instance and (recommended) restrict authorized networks. For **private IP**, use a VPC connector and no public IP.

---

## Summary: What the backend expects

The backend **prefers `DATABASE_URL` (TCP)** when set; otherwise it uses the Cloud SQL Unix socket.

| Connection type | Env / Secret | Required |
|-----------------|--------------|----------|
| **DATABASE_URL (TCP)** | `DATABASE_URL` (secret) | Preferred when set; use for "socket not found" fix |
| **Cloud SQL (Unix socket)** | `INSTANCE_CONNECTION_NAME` (env) | Used only when DATABASE_URL is not set |
| | `DB_USER`, `DB_NAME` (env) | Yes for socket |
| | `DB_PASS` (secret) | Yes for socket |
| | Cloud Run: `--add-cloudsql-instances=...` | Yes for socket |

---

## Quick checklist

- [ ] Cloud SQL instance created
- [ ] Database `health_analytics` and user `health_user` created
- [ ] Schema applied (`backend/db/schema.sql`)
- [ ] Secret `DB_PASS_SECRET` (and optionally `SECRET_KEY_SECRET`) created
- [ ] Cloud Run service account has `roles/cloudsql.client`
- [ ] Cloud Run service updated with `--add-cloudsql-instances` and env/secrets above

After that, your backend on GCP is connected to the database.
