import type { Patient, CheckIn } from '../types';
import { mockPatients, initialCheckIns } from './data';

const STORAGE_KEY_PATIENTS = 'health_analytics_patients';
const STORAGE_KEY_CHECKINS = 'health_analytics_checkins';

function loadPatients(): Patient[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_PATIENTS);
    if (raw) return JSON.parse(raw);
  } catch (_) {}
  return [...mockPatients];
}

function loadCheckIns(): CheckIn[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_CHECKINS);
    if (raw) return JSON.parse(raw);
  } catch (_) {}
  return [...initialCheckIns];
}

let patients = loadPatients();
let checkIns = loadCheckIns();

function persistCheckIns() {
  localStorage.setItem(STORAGE_KEY_CHECKINS, JSON.stringify(checkIns));
}

function persistPatients() {
  localStorage.setItem(STORAGE_KEY_PATIENTS, JSON.stringify(patients));
}

export const store = {
  getPatients(): Patient[] {
    return [...patients];
  },
  getPatient(id: string): Patient | undefined {
    return patients.find((p) => p.id === id);
  },
  getCheckIns(): CheckIn[] {
    return [...checkIns];
  },
  getCheckInsByPatient(patientId: string): CheckIn[] {
    return checkIns.filter((c) => c.patient_id === patientId).sort((a, b) => b.date.localeCompare(a.date));
  },
  addCheckIn(checkIn: Omit<CheckIn, 'id'>): CheckIn {
    const id = 'c' + Date.now();
    const newOne = { ...checkIn, id } as CheckIn;
    checkIns = [newOne, ...checkIns];
    persistCheckIns();
    return newOne;
  },
  setCheckIns(data: CheckIn[]) {
    checkIns = data;
    persistCheckIns();
  },
  setPatients(data: Patient[]) {
    patients = data;
    persistPatients();
  },
};
