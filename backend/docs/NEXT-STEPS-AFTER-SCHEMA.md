# Next Steps After Schema Import

You’ve created **healtappdb** and imported the schema. Do the following so the Cloud Run backend can use it.

---

## 1. Confirm database name

The import may have created or used a database. Our backend expects **`health_analytics`**.

- In Cloud SQL, check which database the schema was imported into (e.g. **Databases** for instance `healtappdb`).
- If the database is named something else (e.g. `postgres`), either:
  - Create a DB named `health_analytics` and import the schema there, or  
  - When deploying, set `DB_NAME` to that database name (see step 4).

---

## 2. Create DB user and Secret Manager secrets

Run in a terminal (replace placeholders):

```bash
gcloud config set project tech-83b89

# Create user on the instance (pick a strong password)
gcloud sql users create health_user --instance=healtappdb --password=YOUR_DB_PASSWORD

# Create secrets (Cloud Run will read these)
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create DB_PASS_SECRET --data-file=-
echo -n "your-jwt-secret-key" | gcloud secrets create SECRET_KEY_SECRET --data-file=-

# Optional: if you still use DATABASE_URL (e.g. for fallback), create it:
# echo -n "postgresql://health_user:YOUR_DB_PASSWORD@/health_analytics?host=/cloudsql/tech-83b89:us-central1:healtappdb" | gcloud secrets create DATABASE_URL_SECRET --data-file=-
```

If a secret already exists, use a new version instead of creating again:

```bash
echo -n "YOUR_DB_PASSWORD" | gcloud secrets versions add DB_PASS_SECRET --data-file=-
```

---

## 3. Grant Cloud Run access to Cloud SQL

```bash
PROJECT_NUMBER=$(gcloud projects describe tech-83b89 --format="value(projectNumber)")
gcloud projects add-iam-policy-binding tech-83b89 \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

(If your Cloud Run service uses a **custom** service account, use that email instead of the compute default.)

---

## 4. Deploy or update the backend

From the **repo root**:

```bash
gcloud builds submit --config=backend/cloudbuild.yaml .
```

This will:

- Build the backend image.
- Deploy to Cloud Run with:
  - `--add-cloudsql-instances=tech-83b89:us-central1:healtappdb`
  - Env: `INSTANCE_CONNECTION_NAME`, `DB_USER=health_user`, `DB_NAME=health_analytics`
  - Secrets: `DB_PASS`, `SECRET_KEY`, `DATABASE_URL`

If your database name is **not** `health_analytics`, set it when updating the service:

```bash
gcloud run services update backend \
  --region=northamerica-northeast1 \
  --set-env-vars="DB_NAME=your_actual_database_name"
```

---

## 5. Verify

1. Open your backend URL, e.g.  
   `https://backend-79306395653.northamerica-northeast1.run.app/health`  
   You should see something like `{"status":"ok","database":"connected"}` if the app can reach the DB.
2. Try logging in from the frontend; that uses the same DB.

---

## Checklist

- [ ] Database name confirmed (e.g. `health_analytics` or updated in env).
- [ ] User `health_user` created on instance `healtappdb`.
- [ ] Secrets created: `DB_PASS_SECRET`, `SECRET_KEY_SECRET` (and `DATABASE_URL_SECRET` if needed).
- [ ] Cloud Run service account has `roles/cloudsql.client`.
- [ ] Backend deployed with `gcloud builds submit --config=backend/cloudbuild.yaml .`
- [ ] `/health` returns database connected and login works from the app.
