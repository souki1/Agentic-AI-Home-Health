import { fetchCheckIns } from "../services/api";
import { useAsync } from "./useAsync";

export function useCheckIns(patientId?: string) {
  return useAsync(() => fetchCheckIns(patientId), [patientId ?? ""]);
}
