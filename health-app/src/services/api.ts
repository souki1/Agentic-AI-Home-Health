import type {
  Patient,
  CheckIn,
  CheckInWithScores,
  AuthResponse,
  AuthState,
  ChatRequest,
  ChatResponse,
  ChatMessage,
} from "../types";
import { ApiError, request } from "./client";

const PATIENTS = "/patients";
const CHECK_INS = "/check-ins";
const CHAT = "/chat";

export async function register(user: {
  email: string;
  password: string;
  role: "patient" | "admin";
  name?: string | null;
}): Promise<void> {
  await request(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify(user),
    },
    false
  );
}

export async function login(
  email: string,
  password: string,
  role: "patient" | "admin" = "patient"
): Promise<AuthResponse> {
  return request<AuthResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password, role }),
    },
    false
  );
}

export async function getCurrentUser(): Promise<AuthState["user"]> {
  return request<AuthState["user"]>("/auth/me");
}

export async function fetchPatients(): Promise<Patient[]> {
  return request<Patient[]>(PATIENTS);
}

export async function fetchPatient(id: string): Promise<Patient | null> {
  try {
    return await request<Patient>(`${PATIENTS}/${encodeURIComponent(id)}`);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

export async function fetchCheckIns(
  patientId?: string
): Promise<CheckInWithScores[]> {
  const q = patientId ? `?patient_id=${encodeURIComponent(patientId)}` : "";
  const list = await request<CheckInWithScores[]>(`${CHECK_INS}${q}`);
  return Array.isArray(list) ? list : [];
}

export async function createCheckIn(
  body: Omit<CheckIn, "id">
): Promise<CheckInWithScores> {
  const payload = {
    patient_id: body.patient_id,
    date: body.date,
    fatigue: body.fatigue,
    breathlessness: body.breathlessness,
    cough: body.cough,
    pain: body.pain,
    nausea: body.nausea,
    dizziness: body.dizziness,
    swelling: body.swelling,
    anxiety: body.anxiety,
    headache: body.headache,
    chest_tightness: body.chest_tightness,
    joint_stiffness: body.joint_stiffness,
    skin_issues: body.skin_issues,
    constipation: body.constipation,
    bloating: body.bloating,
    sleep_hours: body.sleep_hours,
    meds_taken: body.meds_taken,
    appetite: body.appetite,
    mobility: body.mobility,
    devices: body.devices ?? undefined,
    notes: body.notes ?? undefined,
  };
  return request<CheckInWithScores>(CHECK_INS, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function syncAnalytics(): Promise<void> {
  await request(`${CHECK_INS}/sync-analytics`, {
    method: "POST",
  });
}

export async function sendChatMessage(
  message: string,
  conversationHistory?: ChatMessage[]
): Promise<ChatResponse> {
  const payload: ChatRequest = {
    message,
    conversation_history: conversationHistory,
  };
  return request<ChatResponse>(CHAT, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
