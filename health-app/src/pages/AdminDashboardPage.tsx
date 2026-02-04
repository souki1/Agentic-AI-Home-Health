import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useDashboardData } from "../hooks";
import { addDays, toISODate, formatDate } from "../utils";
import { AppLayout } from "../components/layout";
import { KpiCard, LineChartCard, DataTable, StatusBadge, QueryState } from "../components";

export function AdminDashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { data, loading, error } = useDashboardData();
  const patients = data?.patients ?? [];
  const checkIns = data?.checkIns ?? [];
  const today = toISODate(new Date());

  const last7 = useMemo(() => {
    const start = addDays(today, -7);
    return checkIns.filter((c) => c.date >= start && c.date <= today);
  }, [checkIns, today]);
  const last30 = useMemo(() => {
    const start = addDays(today, -30);
    return checkIns.filter((c) => c.date >= start && c.date <= today);
  }, [checkIns, today]);

  const checkInsToday = checkIns.filter((c) => c.date === today).length;
  const expectedPerDay = patients.length;
  const missingRate7d =
    expectedPerDay * 7 > 0
      ? ((1 - last7.length / (expectedPerDay * 7)) * 100).toFixed(1) + "%"
      : "0%";
  const flagged7d = last7.filter((c) => c.status !== "Normal").length;
  const avgSymptom7d =
    last7.length > 0
      ? (last7.reduce((s, c) => s + c.symptom_score, 0) / last7.length).toFixed(1)
      : "—";

  const byDay = useMemo(() => {
    const map = new Map<string, number>();
    for (let i = 29; i >= 0; i--) map.set(addDays(today, -i), 0);
    last30.forEach((c) => map.set(c.date, (map.get(c.date) ?? 0) + 1));
    return Array.from(map.entries()).map(([date, value]) => ({
      date: date.slice(5),
      value,
    }));
  }, [last30, today]);

  const riskByDay = useMemo(() => {
    const map = new Map<string, { sum: number; count: number }>();
    for (let i = 29; i >= 0; i--) map.set(addDays(today, -i), { sum: 0, count: 0 });
    last30.forEach((c) => {
      const v = map.get(c.date)!;
      v.sum += c.risk_score;
      v.count += 1;
    });
    return Array.from(map.entries()).map(([date, v]) => ({
      date: date.slice(5),
      value: v.count ? Math.round((v.sum / v.count) * 10) / 10 : 0,
    }));
  }, [last30, today]);

  // One row per patient: their latest check-in. Sort so Needs Follow-up / Escalated first, then by risk desc.
  const needsFollowUp = useMemo(() => {
    const byPatient = new Map<string, (typeof checkIns)[0]>();
    checkIns.forEach((c) => {
      const cur = byPatient.get(c.patient_id);
      if (!cur || c.date > cur.date) byPatient.set(c.patient_id, c);
    });
    const list = Array.from(byPatient.values());
    const statusOrder = (s: string) => (s === "Escalated" ? 0 : s === "Needs Follow-up" ? 1 : 2);
    return list.sort((a, b) => {
      const orderA = statusOrder(a.status);
      const orderB = statusOrder(b.status);
      if (orderA !== orderB) return orderA - orderB;
      return b.risk_score - a.risk_score;
    });
  }, [checkIns]);

  // If no check-ins yet, show one row per patient with placeholder so table isn’t empty
  const tableRows = useMemo(() => {
    if (needsFollowUp.length > 0) return needsFollowUp;
    return patients.map((p) => ({
      id: p.id,
      patient_id: p.id,
      date: "",
      risk_score: 0,
      status: "Normal" as const,
      symptom_score: 0,
    })) as (typeof checkIns)[0][];
  }, [needsFollowUp, patients]);

  const getPatientName = (id: string) => patients.find((p) => p.id === id)?.name ?? id;
  const getPatientCondition = (id: string) =>
    patients.find((p) => p.id === id)?.condition ?? "—";

  return (
    <AppLayout role="admin" email={user?.email ?? ""} pageTitle="Dashboard">
      <QueryState loading={loading} error={error}>
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard title="Check-ins Today" value={checkInsToday} />
            <KpiCard
              title="Missing Check-ins Rate (7d)"
              value={missingRate7d}
              subtitle="Last 7 days"
            />
            <KpiCard
              title="Flagged Check-ins (7d)"
              value={flagged7d}
              subtitle="Needs follow-up or escalated"
            />
            <KpiCard title="Avg Symptom Score (7d)" value={avgSymptom7d} />
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <LineChartCard
              title="Check-ins per day (30 days)"
              data={byDay}
              valueLabel="Check-ins"
            />
            <LineChartCard
              title="Avg risk score trend (30 days)"
              data={riskByDay}
              valueLabel="Risk score"
              color="#dc2626"
            />
          </div>
          <div>
            <h2 className="mb-1 text-lg font-semibold text-slate-800">
              Needs Follow-up
            </h2>
            <p className="mb-3 text-sm text-slate-500">
              Patients needing follow-up appear first. All patients with a check-in are listed.
            </p>
            <DataTable
              keyField="id"
              data={tableRows}
              columns={[
                {
                  key: "patient",
                  header: "Patient",
                  render: (r) => getPatientName(r.patient_id),
                },
                {
                  key: "condition",
                  header: "Condition",
                  render: (r) => getPatientCondition(r.patient_id),
                },
                {
                  key: "date",
                  header: "Last Check-in",
                  render: (r) => (r.date ? formatDate(r.date) : "—"),
                },
                {
                  key: "risk_score",
                  header: "Risk Score",
                  render: (r) =>
                    r.risk_score != null ? r.risk_score.toFixed(1) : "—",
                },
                {
                  key: "status",
                  header: "Status",
                  render: (r) => <StatusBadge status={r.status} />,
                },
                {
                  key: "view",
                  header: "",
                  render: (r) => (
                    <button
                      type="button"
                      onClick={() => navigate(`/admin/patients/${r.patient_id}`)}
                      className="text-primary-600 hover:underline text-sm font-medium"
                    >
                      View
                    </button>
                  ),
                },
              ]}
              emptyMessage="No patients yet. When patients sign up and submit check-ins, they will appear here."
            />
          </div>
        </div>
      </QueryState>
    </AppLayout>
  );
}
