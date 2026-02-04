const env = import.meta.env;

// Use VITE_API_URL if set, otherwise /api (Vite proxy to backend in dev)
const raw = (env.VITE_API_URL as string)?.trim()?.replace(/\/$/, "") ?? "";
export const config = {
  apiBaseUrl: raw || "/api",
} as const;

export const isApiConfigured = (): boolean => !!config.apiBaseUrl;
