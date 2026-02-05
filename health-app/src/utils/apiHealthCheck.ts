import { config } from "../config";

/**
 * Check if the backend API is accessible
 * Useful for debugging connection issues
 */
export async function checkApiHealth(): Promise<{ ok: boolean; message: string }> {
  try {
    const healthUrl = `${config.apiBaseUrl}/health`;
    const res = await fetch(healthUrl, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    
    if (res.ok) {
      const data = await res.json();
      return { ok: true, message: `Backend is running: ${JSON.stringify(data)}` };
    } else {
      return { ok: false, message: `Backend returned ${res.status}: ${res.statusText}` };
    }
  } catch (error) {
    const err = error as Error;
    return {
      ok: false,
      message: `Cannot reach backend at ${config.apiBaseUrl}: ${err.message}`,
    };
  }
}
