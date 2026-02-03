import type { CheckIn, Status } from '../types';

/** symptom_score = average of all symptom fields (0–10) */
const SYMPTOM_KEYS = ['fatigue', 'breathlessness', 'cough', 'pain', 'nausea', 'dizziness', 'swelling', 'anxiety'] as const;

export function computeSymptomScore(c: CheckIn): number {
  const count = SYMPTOM_KEYS.length;
  const sum = SYMPTOM_KEYS.reduce((acc, k) => acc + (c[k] ?? 0), 0);
  return Math.round((sum / count) * 10) / 10;
}

/**
 * risk_score = weighted formula:
 * - symptom_score base
 * - meds_taken penalty (if false, add)
 * - low_sleep penalty
 */
export function computeRiskScore(c: CheckIn): number {
  const symptom = computeSymptomScore(c);
  const medsPenalty = c.meds_taken ? 0 : 1.5;
  const sleepPenalty = c.sleep_hours < 5 ? 1 : c.sleep_hours < 7 ? 0.5 : 0;
  const score = symptom + medsPenalty + sleepPenalty;
  return Math.min(10, Math.round(score * 10) / 10);
}

/** risk_score < 4 → Normal; 4–7 → Needs Follow-up; > 7 → Escalated */
export function computeStatus(riskScore: number): Status {
  if (riskScore < 4) return 'Normal';
  if (riskScore <= 7) return 'Needs Follow-up';
  return 'Escalated';
}

export function getStatusColor(status: Status): string {
  switch (status) {
    case 'Normal': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    case 'Needs Follow-up': return 'bg-amber-100 text-amber-800 border-amber-200';
    case 'Escalated': return 'bg-red-100 text-red-800 border-red-200';
    default: return 'bg-slate-100 text-slate-800 border-slate-200';
  }
}
