/**
 * @deprecated Use services/api and hooks instead.
 * Re-exports for backwards compatibility.
 */
export {
  fetchPatients as getPatients,
  fetchPatient as getPatient,
  fetchCheckIns as getCheckIns,
  createCheckIn as addCheckIn,
} from "./api";
