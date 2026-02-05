import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    server: {
      proxy: {
        // Forward /api/* to backend (backend routes are under /api)
        '/api': {
          target: env.VITE_API_URL?.replace(/\/api\/?$/, '') || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
    // Explicitly define env vars to expose to client
    define: {
      // Vite automatically exposes VITE_* vars, but we ensure it's available
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL),
    },
  }
})
