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
  sleep_hours: number;
  meds_taken: boolean;
  appetite: Appetite;
  mobility: Mobility;
  notes?: string;
}

export type Status = 'Normal' | 'Needs Follow-up' | 'Escalated';

export interface CheckInWithScores extends CheckIn {
  symptom_score: number;
  risk_score: number;
  status: Status;
}

export interface AuthUser {
  email: string;
  role: Role;
}
