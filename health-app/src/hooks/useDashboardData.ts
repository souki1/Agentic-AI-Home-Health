import type { Patient, CheckInWithScores } from "../types";
import { fetchCheckIns, fetchPatients } from "../services/api";
import { useAsync } from "./useAsync";

interface DashboardData {
  patients: Patient[];
  checkIns: CheckInWithScores[];
}

function fetchDashboard(): Promise<DashboardData> {
  return Promise.all([fetchPatients(), fetchCheckIns()]).then(
    ([patients, checkIns]) => ({ patients, checkIns })
  );
}

export function useDashboardData() {
  return useAsync(fetchDashboard, []);
}
