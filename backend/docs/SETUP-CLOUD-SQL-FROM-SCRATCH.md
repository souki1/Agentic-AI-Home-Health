# Set Up Cloud SQL From Scratch and Integrate With Backend

Use this guide after creating a new GCP project or when you've deleted the old Cloud SQL instance. Project: **tech-83b89**. Backend runs in **northamerica-northeast1**.

---

## Step 1: Create the Cloud SQL instance

**Console:**

1. Go to [Google Cloud Console](https://console.cloud.google.com) → **SQL**.
2. Click **Create instance** → **Choose PostgreSQL**.
3. **Instance ID:** `healtappdb` (or any name you prefer).
4. **Password:** Girish@123
5. **Region:** e.g. `us-central1` or `northamerica-northeast1`.
6. **Customize your instance** → **Connections:** enable **Public IP**.
7. Click **Create instance** and wait until it’s ready.

**Or with gcloud:**

```powershell
gcloud config set project tech-83b89
gcloud sql instances create healtappdb `
  --database-version=POSTGRES_15 `
  --tier=db-f1-micro `
  --region=us-central1 `
  --root-password=CHOOSE_A_STRONG_ROOT_PASSWORD
```

*(Replace `CHOOSE_A_STRONG_ROOT_PASSWORD` and adjust region if needed.)*

---

## Step 2: Create the database and app user

**Console:**

1. Open your instance (**healtappdb**) → **Databases**.
2. Click **Create database** → Name: `health_analytics` → **Create**
3. Go to **Users** → **Add user account**.
4. **User name:** `health_user`, **Password:** choose a password (e.g. `root` for dev) → **Add**.

**Or with gcloud:**

```powershell
gcloud sql databases create health_analytics --instance=healtappdb
gcloud sql users create health_user --instance=healtappdb --password=YourHealthUserPassword
```

Use the same password later in `DATABASE_URL`.

---

## Step 3: Allow Cloud Run to connect (public IP)

1. Open the instance → **Connections** (or **Overview** → **Connect to this instance**).
2. Under **Networking**, **Authorized networks** → **Add network**.
3. **Name:** e.g. `cloud-run`, **Network:** `0.0.0.0/0` (allows Cloud Run; you can restrict later).
4. Save.

---

## Step 4: Get the instance public IP

1. In **SQL** → click **healtappdb**.
2. On the overview, copy **Public IP address** (e.g. `34.171.27.98`). You’ll use it in the connection string.

---

## Step 5: Run the database schema (create tables)

You need to run `backend/db/schema.sql` once on the `health_analytics` database.

**Option A – Cloud Shell**

1. In GCP Console, open **Cloud Shell** (top right).
2. Upload `backend/db/schema.sql` or paste its contents into a file, e.g. `schema.sql`.
3. Run:

```bash
gcloud sql connect healtappdb --user=health_user --database=health_analytics
```

4. Enter the password for `health_user` when prompted.
5. In the `psql` prompt:

```sql
\i schema.sql
```

(Or paste the contents of `schema.sql` and run.) Then `\q` to quit.

**Option B – From your PC with Cloud SQL Auth Proxy**

1. [Install Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy#install).
2. Start the proxy (replace with your instance connection name, e.g. `tech-83b89:us-central1:healtappdb`):

```powershell
cloud-sql-proxy "tech-83b89:us-central1:healtappdb"
```

3. In another terminal, from the repo:

```powershell
$env:PGPASSWORD="YourHealthUserPassword"; psql -h 127.0.0.1 -U health_user -d health_analytics -f backend/db/schema.sql
```

---

## Step 6: Create or update secrets for Cloud Run

Use your **actual** public IP and **health_user** password.

**DATABASE_URL** (required for backend):

```powershell
gcloud config set project tech-83b89
echo -n "postgresql://health_user:YourHealthUserPassword@YOUR_PUBLIC_IP:5432/health_analytics?sslmode=require" | gcloud secrets versions add DATABASE_URL_SECRET --data-file=-
```

If `DATABASE_URL_SECRET` doesn’t exist yet:

```powershell
echo -n "postgresql://health_user:YourHealthUserPassword@YOUR_PUBLIC_IP:5432/health_analytics?sslmode=require" | gcloud secrets create DATABASE_URL_SECRET --data-file=-
```

**SECRET_KEY** (JWT; create if missing):

```powershell
echo -n "your-jwt-secret-key-change-in-production" | gcloud secrets create SECRET_KEY_SECRET --data-file=-
```

**DB_PASS** (used if you use socket later; optional when using only DATABASE_URL):

```powershell
echo -n "YourHealthUserPassword" | gcloud secrets create DB_PASS_SECRET --data-file=-
```

Replace `YourHealthUserPassword`, `YOUR_PUBLIC_IP`, and the JWT secret with real values.

---

## Step 7: Grant Cloud Run access to Cloud SQL (optional for TCP)

For TCP (public IP) you already allowed the network. For **Unix socket** later, grant the default compute SA:

```powershell
$projectNumber = (gcloud projects describe tech-83b89 --format="value(projectNumber)")
gcloud projects add-iam-policy-binding tech-83b89 `
  --member="serviceAccount:${projectNumber}-compute@developer.gserviceaccount.com" `
  --role="roles/cloudsql.client"
```

---

## Step 8: Point Cloud Build at your new instance (if name/region changed)

If you used a different instance name or region, update `backend/cloudbuild.yaml`:

- `_CLOUDSQL_INSTANCE`: `tech-83b89:REGION:INSTANCE_ID` (e.g. `tech-83b89:us-central1:healtappdb`).

---

## Step 9: Deploy the backend

From the **repo root**:

```powershell
cd E:\dataengineering\Agentic-AI-Home-Health
gcloud builds submit --config=backend/cloudbuild.yaml .
```

Wait for the build and deploy to finish.

---

## Step 10: Verify

```powershell
curl https://backend-79306395653.northamerica-northeast1.run.app/health
```

Expected: `{"status":"ok","database":"connected"}`.

Then open your frontend, register a user, and log in to confirm end-to-end.

---

## Checklist

- [ ] Cloud SQL instance created (e.g. `healtappdb`)
- [ ] Database `health_analytics` created
- [ ] User `health_user` created with a known password
- [ ] Public IP enabled and authorized network added (`0.0.0.0/0` or restricted)
- [ ] Schema applied (`backend/db/schema.sql`)
- [ ] Secret `DATABASE_URL_SECRET` set with `postgresql://health_user:PASSWORD@PUBLIC_IP:5432/health_analytics?sslmode=require`
- [ ] Secrets `SECRET_KEY_SECRET` and `DB_PASS_SECRET` exist
- [ ] Backend deployed via `gcloud builds submit --config=backend/cloudbuild.yaml .`
- [ ] `/health` returns `database":"connected"`
