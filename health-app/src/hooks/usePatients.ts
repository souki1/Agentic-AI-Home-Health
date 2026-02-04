import { fetchPatients } from "../services/api";
import { useAsync } from "./useAsync";

export function usePatients() {
  return useAsync(fetchPatients, []);
}
