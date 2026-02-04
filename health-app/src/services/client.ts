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
  if (!res.ok) {
    const message = await parseErrorResponse(res);
    throw new ApiError(message, res.status);
  }
  if (res.status === 204 || res.headers.get("content-length") === "0") {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}
