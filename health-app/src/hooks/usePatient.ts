import { fetchPatient } from "../services/api";
import { useAsync } from "./useAsync";

export function usePatient(id: string | undefined) {
  return useAsync(
    () => (id ? fetchPatient(id) : Promise.resolve(null)),
    [id ?? ""]
    );
}
