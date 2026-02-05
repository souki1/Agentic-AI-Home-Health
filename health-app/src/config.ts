const env = import.meta.env;

// Get VITE_API_URL from environment
// In dev: reads from .env.local
// In production build: reads from .env.production or build-time VITE_API_URL
const viteApiUrl = env.VITE_API_URL as string | undefined;
const raw = viteApiUrl?.trim()?.replace(/\/$/, "") ?? "";

// Determine API base URL
// Priority: VITE_API_URL env var > /api proxy (dev only)
let apiBaseUrl: string;
if (raw) {
  // Use explicit API URL from env
  apiBaseUrl = raw;
} else {
  // Fallback to /api proxy (only works in dev mode with npm run dev)
  apiBaseUrl = "/api";
  if (import.meta.env.PROD) {
    // In production, /api won't work - warn user
    console.error(
      "⚠️ VITE_API_URL is not set in production build. " +
      "API calls will fail. Set VITE_API_URL in .env.production or build args."
    );
  }
}

export const config = {
  apiBaseUrl,
} as const;

// Debug logging (always log API config for troubleshooting)
console.log(`[Config] Mode: ${import.meta.env.MODE}`);
console.log(`[Config] VITE_API_URL: ${viteApiUrl || "(not set)"}`);
console.log(`[Config] API Base URL: ${config.apiBaseUrl}`);

if (import.meta.env.PROD && !viteApiUrl) {
  console.error(
    "❌ CRITICAL: VITE_API_URL is not set in production build. " +
    "API calls will fail. Set VITE_API_URL in .env.production or build args."
  );
} else if (import.meta.env.PROD && viteApiUrl) {
  console.log(`✅ Production API URL configured: ${config.apiBaseUrl}`);
}

export const isApiConfigured = (): boolean => !!config.apiBaseUrl;
