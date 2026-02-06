export type Role = 'patient' | 'admin';

export interface Patient {
  id: string;
  name: string;
  age: number;
  condition: string;
  created_at: string;
}

export type Appetite = 'Normal' | 'Low';
export type Mobility = 'Normal' | 'Reduced';

/** Optional device readings (home health monitors) */
export interface DeviceReadings {
  spo2?: number | null;        // SpO2 %
  bp_systolic?: number | null;
  bp_diastolic?: number | null;
  weight_kg?: number | null;
  glucose_mgdl?: number | null; // blood glucose mg/dL
}

export interface CheckIn {
  id: string;
  patient_id: string;
  date: string;
  fatigue: number;
  breathlessness: number;
  cough: number;
  pain: number;
  nausea: number;
  dizziness: number;
  swelling: number;
  anxiety: number;
  headache: number;
  chest_tightness: number;
  joint_stiffness: number;
  skin_issues: number;
  constipation: number;
  bloating: number;
  sleep_hours: number;
  meds_taken: boolean;
  appetite: Appetite;
  mobility: Mobility;
  /** Optional device readings */
  devices?: DeviceReadings | null;
  notes?: string;
}

export type Status = 'Normal' | 'Needs Follow-up' | 'Escalated';

export interface CheckInWithScores extends CheckIn {
  symptom_score: number;
  risk_score: number;
  status: Status;
}

export interface AuthUser {
  id: string;
  email: string;
  role: Role;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface AuthResponse {
  token: AuthToken;
  user: AuthUser;
}

export interface AuthState {
  user: AuthUser;
  token: AuthToken;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  provider: 'ollama' | 'vertex';
}
