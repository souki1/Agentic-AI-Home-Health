import type { Patient, CheckIn, Appetite, Mobility } from '../types';
import { computeSymptomScore, computeRiskScore, computeStatus } from '../utils/scores';
import { addDays, toISODate } from '../utils';

const today = toISODate(new Date());

export const mockPatients: Patient[] = [
  { id: 'p1', name: 'Alice Johnson', age: 72, condition: 'COPD', created_at: '2024-01-15' },
  { id: 'p2', name: 'Robert Chen', age: 68, condition: 'Heart Failure', created_at: '2024-02-01' },
  { id: 'p3', name: 'Maria Garcia', age: 75, condition: 'Diabetes', created_at: '2024-01-20' },
  { id: 'p4', name: 'James Wilson', age: 80, condition: 'COPD', created_at: '2024-02-10' },
  { id: 'p5', name: 'Patricia Brown', age: 65, condition: 'Heart Failure', created_at: '2024-01-25' },
];

function genCheckIns(): CheckIn[] {
  const row = (
    id: string, patient_id: string, date: string,
    fatigue: number, breathlessness: number, cough: number, pain: number,
    nausea: number, dizziness: number, swelling: number, anxiety: number,
    sleep_hours: number, meds_taken: boolean, appetite: Appetite, mobility: Mobility,
    notes?: string
  ): CheckIn => ({
    id, patient_id, date, fatigue, breathlessness, cough, pain, nausea, dizziness, swelling, anxiety,
    sleep_hours, meds_taken, appetite, mobility, ...(notes && { notes }),
  });
  const base: CheckIn[] = [
    row('c1', 'p1', today, 3, 4, 2, 2, 0, 1, 0, 2, 7, true, 'Normal', 'Normal', 'Feeling okay'),
    row('c2', 'p1', addDays(today, -1), 5, 5, 4, 3, 1, 2, 1, 3, 6, true, 'Normal', 'Reduced'),
    row('c3', 'p1', addDays(today, -2), 2, 3, 2, 1, 0, 0, 0, 1, 8, true, 'Normal', 'Normal'),
    row('c4', 'p2', today, 6, 7, 3, 5, 2, 3, 2, 4, 4, false, 'Low', 'Reduced', 'Short of breath'),
    row('c5', 'p2', addDays(today, -1), 5, 6, 2, 4, 1, 2, 1, 3, 5, true, 'Normal', 'Reduced'),
    row('c6', 'p3', today, 2, 1, 1, 2, 0, 0, 0, 0, 7, true, 'Normal', 'Normal'),
    row('c7', 'p3', addDays(today, -3), 4, 2, 2, 3, 1, 0, 0, 2, 6, true, 'Low', 'Normal'),
    row('c8', 'p4', addDays(today, -1), 8, 8, 6, 7, 4, 5, 4, 6, 3, false, 'Low', 'Reduced'),
    row('c9', 'p5', today, 4, 4, 3, 4, 0, 1, 0, 2, 6, true, 'Normal', 'Normal'),
    row('c10', 'p5', addDays(today, -2), 5, 5, 4, 5, 1, 1, 1, 2, 5, true, 'Low', 'Reduced'),
  ];
  return base;
}

export const initialCheckIns = genCheckIns();

export function withScores(checkIns: CheckIn[]) {
  return checkIns.map((c) => {
    const symptom_score = computeSymptomScore(c);
    const risk_score = computeRiskScore(c);
    const status = computeStatus(risk_score);
    return { ...c, symptom_score, risk_score, status };
  });
}
