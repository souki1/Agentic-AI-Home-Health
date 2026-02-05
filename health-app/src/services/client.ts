import { config } from "../config";
import { AUTH_STORAGE_KEY } from "../context/AuthContext";

export class ApiError extends Error {
  readonly status: number;
  readonly body?: unknown;
  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function parseErrorResponse(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const j = JSON.parse(text) as { detail?: string };
    return typeof j.detail === "string" ? j.detail : text || `HTTP ${res.status}`;
  } catch {
    return text || `HTTP ${res.status}`;
  }
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
  auth: boolean = true
): Promise<T> {
  const base = config.apiBaseUrl;
  if (!base) throw new ApiError("VITE_API_URL is not set", 0);
  const url = path.startsWith("http") ? path : `${base}${path}`;
  
  // Debug: log API calls in development
  if (import.meta.env.DEV) {
    console.log(`[API] ${options.method || "GET"} ${url}`);
  }
  let token: string | undefined;
  if (auth) {
    try {
      const raw = localStorage.getItem(AUTH_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as { token?: { access_token?: string } };
        token = parsed?.token?.access_token;
      }
    } catch {
      // ignore
    }
  }
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  
  // Check Content-Type before parsing
  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  
  if (!res.ok) {
    const message = await parseErrorResponse(res);
    throw new ApiError(message, res.status);
  }
  
  if (res.status === 204 || res.headers.get("content-length") === "0") {
    return undefined as T;
  }
  
  // Only parse JSON if Content-Type indicates JSON
  if (!isJson) {
    const text = await res.text();
    // If we got HTML, likely hitting wrong URL (frontend instead of backend)
    if (contentType.includes("text/html") || text.trim().startsWith("<!")) {
      let errorMsg = `Got HTML instead of JSON. Check API URL: ${url}\n`;
      errorMsg += `Current API base: ${base}\n`;
      
      if (base === "/api") {
        errorMsg += `\n⚠️ Using '/api' proxy. This only works in development mode (npm run dev).\n`;
        errorMsg += `Solutions:\n`;
        errorMsg += `1. For local dev: Ensure backend is running on http://localhost:8000\n`;
        errorMsg += `2. For local dev: Set VITE_API_URL=http://localhost:8000 in .env.local\n`;
        errorMsg += `3. For production: Set VITE_API_URL in .env.production or build args\n`;
      } else {
        errorMsg += `\n⚠️ Backend may not be running or URL is incorrect.\n`;
        errorMsg += `Check: ${base}/health\n`;
      }
      
      throw new ApiError(errorMsg, res.status);
    }
    throw new ApiError(
      `Expected JSON but got ${contentType || "unknown"}. Response: ${text.substring(0, 200)}`,
      res.status
    );
  }
  
  return res.json() as Promise<T>;
}
