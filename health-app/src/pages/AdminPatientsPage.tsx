import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { usePatients, useCheckIns } from "../hooks";
import { formatDate } from "../utils";
import { AppLayout } from "../components/layout";
import { DataTable, StatusBadge, QueryState } from "../components";

export function AdminPatientsPage() {
  const { user } = useAuth();
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const patientsState = usePatients();
  const checkInsState = useCheckIns();
  const patients = patientsState.data ?? [];
  const checkIns = checkInsState.data ?? [];
  const loading = patientsState.loading || checkInsState.loading;
  const error = patientsState.error ?? checkInsState.error ?? null;

  const lastByPatient = useMemo(() => {
    const map = new Map<string, (typeof checkIns)[0]>();
    checkIns.forEach((c) => {
      const cur = map.get(c.patient_id);
      if (!cur || c.date > cur.date) map.set(c.patient_id, c);
    });
    return map;
  }, [checkIns]);

  const rows = useMemo(() => {
    const list = patients.map((p) => {
      const last = lastByPatient.get(p.id);
      return {
        patient: p,
        lastCheckIn: last ? last.date : null,
        riskScore: last?.risk_score ?? null,
        status: last?.status ?? null,
      };
    });
    if (!search.trim()) return list;
    const q = search.toLowerCase();
    return list.filter(
      (r) =>
        r.patient.name.toLowerCase().includes(q) ||
        r.patient.condition.toLowerCase().includes(q)
    );
  }, [patients, lastByPatient, search]);

  return (
    <AppLayout role="admin" email={user?.email ?? ""} pageTitle="Patients">
      <QueryState loading={loading} error={error}>
        <div className="space-y-4">
          <div className="max-w-xs">
            <input
              type="search"
              placeholder="Search patients..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <DataTable
            keyField={(r) => r.patient.id}
            data={rows}
            columns={[
              {
                key: "name",
                header: "Patient Name",
                render: (r) => r.patient.name || "—",
              },
              {
                key: "condition",
                header: "Condition",
                render: (r) => r.patient.condition || "—",
              },
              {
                key: "last",
                header: "Last Check-in",
                render: (r) =>
                  r.lastCheckIn ? formatDate(r.lastCheckIn) : "—",
              },
              {
                key: "risk",
                header: "Risk Score",
                render: (r) =>
                  r.riskScore != null ? r.riskScore.toFixed(1) : "—",
              },
              {
                key: "status",
                header: "Status",
                render: (r) =>
                  r.status ? <StatusBadge status={r.status} /> : "—",
              },
              {
                key: "view",
                header: "",
                render: (r) => (
                  <button
                    type="button"
                    onClick={() => navigate(`/admin/patients/${r.patient.id}`)}
                    className="text-primary-600 hover:underline text-sm font-medium"
                  >
                    View
                  </button>
                ),
              },
            ]}
          />
        </div>
      </QueryState>
    </AppLayout>
  );
}
