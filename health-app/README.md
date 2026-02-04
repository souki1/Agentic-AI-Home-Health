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

**API URL Configuration:**

**For GCP Cloud Run (recommended):**
Build with the backend Cloud Run URL so the frontend makes direct calls:
```bash
# Get your backend URL first
BACKEND_URL=$(gcloud run services describe health-backend --region us-central1 --format="value(status.url)")

# Build with backend URL
docker build --build-arg VITE_API_URL=$BACKEND_URL -t health-app-frontend .

# Or in Cloud Build:
gcloud builds submit --config=cloudbuild.yaml . \
  --substitutions=_VITE_API_URL=$BACKEND_URL
```

**For local development with proxy:**
Use default `/api` and set `BACKEND_URL` when running:
```bash
docker run -p 8080:8080 \
  -e BACKEND_URL=http://localhost:8000 \
  health-app-frontend
```

**Important**: For Cloud Run, always build with `VITE_API_URL` set to your backend URL. The nginx proxy is only for local development or same-domain setups.

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
