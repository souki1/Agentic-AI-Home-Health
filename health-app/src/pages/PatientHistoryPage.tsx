import { useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useCheckIns } from "../hooks";
import { addDays, toISODate, formatDate } from "../utils";
import type { CheckInWithScores } from "../types";
import { AppLayout } from "../components/layout";
import {
  DataTable,
  Drawer,
  DateRangeFilter,
  StatusBadge,
  QueryState,
} from "../components";

type Range = "7" | "30" | "custom";

export function PatientHistoryPage() {
  const { user } = useAuth();
  const [range, setRange] = useState<Range>("30");
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");
  const [selected, setSelected] = useState<CheckInWithScores | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { data, loading, error } = useCheckIns(user?.id ?? "p1");
  const allCheckIns = data ?? [];

  const filtered = useMemo(() => {
    const today = toISODate(new Date());
    let start: string;
    let end: string = today;
    if (range === "7") start = addDays(today, -7);
    else if (range === "30") start = addDays(today, -30);
    else {
      start = customStart || addDays(today, -30);
      end = customEnd || today;
    }
    return allCheckIns.filter((c) => c.date >= start && c.date <= end);
  }, [allCheckIns, range, customStart, customEnd]);

  const openDrawer = (row: CheckInWithScores) => {
    setSelected(row);
    setDrawerOpen(true);
  };

  return (
    <AppLayout
      role="patient"
      email={user?.email ?? ""}
      pageTitle="Check-in History"
    >
      <QueryState loading={loading} error={error}>
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <DateRangeFilter
              value={range}
              onRangeChange={setRange}
              customStart={customStart}
              customEnd={customEnd}
              onCustomStartChange={setCustomStart}
              onCustomEndChange={setCustomEnd}
            />
          </div>
          <DataTable<CheckInWithScores>
            keyField="id"
            data={filtered}
            onRowClick={openDrawer}
            columns={[
              {
                key: "date",
                header: "Date",
                render: (r) => formatDate(r.date),
              },
              {
                key: "symptom_score",
                header: "Symptom Score",
                render: (r) => r.symptom_score.toFixed(1),
              },
              {
                key: "risk_score",
                header: "Risk Score",
                render: (r) => r.risk_score.toFixed(1),
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
                    onClick={(e) => {
                      e.stopPropagation();
                      openDrawer(r);
                    }}
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

      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Check-in Details"
      >
        {selected && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs text-slate-500">Symptom Score</p>
                <p className="text-lg font-semibold text-slate-800">
                  {selected.symptom_score.toFixed(1)}
                </p>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs text-slate-500">Risk Score</p>
                <p className="text-lg font-semibold text-slate-800">
                  {selected.risk_score.toFixed(1)}
                </p>
              </div>
              <div className="col-span-2">
                <StatusBadge status={selected.status} />
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-700">Fields</p>
              <ul className="mt-2 space-y-1 text-sm text-slate-600">
                <li>Date: {formatDate(selected.date)}</li>
                <li>
                  Fatigue: {selected.fatigue} · Breathlessness:{" "}
                  {selected.breathlessness} · Cough: {selected.cough} · Pain:{" "}
                  {selected.pain}
                </li>
                <li>
                  Nausea: {selected.nausea} · Dizziness: {selected.dizziness} ·
                  Swelling: {selected.swelling} · Anxiety: {selected.anxiety}
                </li>
                <li>
                  Headache: {selected.headache ?? 0} · Chest tightness:{" "}
                  {selected.chest_tightness ?? 0} · Joint stiffness:{" "}
                  {selected.joint_stiffness ?? 0} · Skin:{" "}
                  {selected.skin_issues ?? 0} · Constipation:{" "}
                  {selected.constipation ?? 0} · Bloating:{" "}
                  {selected.bloating ?? 0}
                </li>
                <li>
                  Sleep: {selected.sleep_hours}h · Meds:{" "}
                  {selected.meds_taken ? "Yes" : "No"} · Appetite:{" "}
                  {selected.appetite} · Mobility: {selected.mobility}
                </li>
                {selected.devices &&
                  (selected.devices.spo2 != null ||
                    selected.devices.bp_systolic != null ||
                    selected.devices.weight_kg != null ||
                    selected.devices.glucose_mgdl != null) && (
                    <li>
                      Devices:{" "}
                      {selected.devices.spo2 != null &&
                        `SpO2 ${selected.devices.spo2}%`}
                      {selected.devices.bp_systolic != null &&
                        selected.devices.bp_diastolic != null &&
                        ` · BP ${selected.devices.bp_systolic}/${selected.devices.bp_diastolic}`}
                      {selected.devices.weight_kg != null &&
                        ` · ${selected.devices.weight_kg} kg`}
                      {selected.devices.glucose_mgdl != null &&
                        ` · Glucose ${selected.devices.glucose_mgdl} mg/dL`}
                    </li>
                  )}
                {selected.notes && (
                  <li>Notes: {selected.notes}</li>
                )}
              </ul>
            </div>
            <details className="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <summary className="cursor-pointer text-sm font-medium text-slate-700">
                Raw JSON
              </summary>
              <pre className="mt-2 overflow-auto text-xs text-slate-600">
                {JSON.stringify(selected, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </Drawer>
    </AppLayout>
  );
}
