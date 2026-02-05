# Health App (React + TypeScript + Vite)

Frontend for the Health Analytics app.

## Deploy to GCP (Docker)

The image uses **Node + serve** (no nginx) and listens on port **8080** (Cloud Run default).

```bash
# Build (from health-app/)
docker build -t health-app-frontend .

# Run locally
docker run -p 8080:8080 health-app-frontend
# Open http://localhost:8080
```

**Cloud Run:**

```bash
# Build and push to Artifact Registry (set your project and region)
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/health-app .

# Deploy
gcloud run deploy health-app --image gcr.io/YOUR_PROJECT_ID/health-app --platform managed --region us-central1 --allow-unauthenticated
```

## Environment Configuration

The app uses environment files for different deployment scenarios:

### Local Development (`.env.local`)
- Used when running `npm run dev`
- Contains: `VITE_API_URL=http://localhost:8000`
- This file is gitignored (local only)

### Production (`.env.production`)
- Used when running `npm run build` (production builds)
- Contains: `VITE_API_URL=https://backend-79306395653.northamerica-northeast1.run.app`
- This file is committed to git (public API URL)

### Build Process

**Local Development:**
```bash
npm run dev  # Uses .env.local
```

**Production Build:**
```bash
npm run build  # Uses .env.production automatically
```

**Docker Build:**
The Dockerfile accepts `VITE_API_URL` as a build arg, which overrides `.env.production`:
```bash
docker build --build-arg VITE_API_URL=https://your-backend-url.run.app -t health-app-frontend .
```

**GitHub Actions / Cloud Build:**
- GitHub Actions workflow uses the production URL from `.env.production` by default
- Can be overridden via repository variables: `VITE_API_URL`
- Cloud Build (`cloudbuild.yaml`) has the production URL configured in substitutions

**Important**: When you push code and it builds automatically, it will use the production settings from `.env.production` file, ensuring the frontend connects to the production backend.

## Troubleshooting

### "Got HTML instead of JSON" Error

If you see this error: `Got HTML instead of JSON. Check API URL: /api/auth/login`

**This means the frontend can't reach the backend.** Here's how to fix it:

1. **Check if backend is running:**
   ```bash
   # In backend directory
   python -m uvicorn main:app --reload --port 8000
   # Or use the batch script:
   run_server.bat
   ```

2. **Verify .env.local exists and has correct URL:**
   ```bash
   # Should show: VITE_API_URL=http://localhost:8000
   cat .env.local
   ```

3. **Restart the dev server** (Vite needs restart to pick up .env changes):
   ```bash
   # Stop the dev server (Ctrl+C)
   # Then restart:
   npm run dev
   ```

4. **Check browser console** - you should see:
   ```
   [Config] VITE_API_URL: http://localhost:8000
   [Config] API Base URL: http://localhost:8000
   ```

5. **If using `/api` proxy** (VITE_API_URL not set):
   - This only works in development mode (`npm run dev`)
   - Make sure backend is running on `http://localhost:8000`
   - The proxy won't work in production builds

6. **For production builds:**
   - Always set `VITE_API_URL` in `.env.production` or build args
   - `/api` proxy doesn't work in production - you need the full backend URL

### Verify Backend Connection

Test if backend is accessible:
```bash
# Should return: {"status":"ok","database":"connected"}
curl http://localhost:8000/health
```

---

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
