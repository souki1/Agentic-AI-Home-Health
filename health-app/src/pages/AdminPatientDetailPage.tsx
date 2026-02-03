import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { store } from '../mock/store';
import { withScores } from '../mock/data';
import { formatDate } from '../utils';
import { AppLayout } from '../components/layout';
import { LineChartCard, DataTable, StatusBadge, Modal } from '../components';

export function AdminPatientDetailPage() {
  const { user } = useAuth();
  const { id } = useParams<{ id: string }>();
  const [followUpOpen, setFollowUpOpen] = useState(false);
  const patient = id ? store.getPatient(id) : undefined;
  const checkInsRaw = id ? store.getCheckInsByPatient(id) : [];
  const checkIns = useMemo(() => withScores(checkInsRaw), [checkInsRaw.length, id]);
  const latest = checkIns[0];

  const trendData = useMemo(
    () =>
      [...checkIns].reverse().map((c) => ({
        date: c.date.slice(5),
        value: c.symptom_score,
      })),
    [checkIns]
  );

  const missingFields = useMemo(() => {
    let n = 0;
    checkIns.forEach((c) => {
      if (c.notes === undefined || c.notes === '') n++;
    });
    return n;
  }, [checkIns]);
  const duplicatesDetected = 0;
  const lateSubmissions = 1;

  if (!patient) {
    return (
      <AppLayout role="admin" email={user?.email ?? ''} pageTitle="Patient">
        <p className="text-slate-600">Patient not found.</p>
      </AppLayout>
    );
  }

  return (
    <AppLayout role="admin" email={user?.email ?? ''} pageTitle={patient.name}>
      <div className="space-y-6">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-800">Profile</h2>
          <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm sm:grid-cols-3">
            <dt className="text-slate-500">Name</dt>
            <dd className="font-medium text-slate-800">{patient.name}</dd>
            <dt className="text-slate-500">Age</dt>
            <dd className="font-medium text-slate-800">{patient.age}</dd>
            <dt className="text-slate-500">Condition</dt>
            <dd className="font-medium text-slate-800">{patient.condition}</dd>
            <dt className="text-slate-500">Created</dt>
            <dd className="font-medium text-slate-800">{formatDate(patient.created_at)}</dd>
          </dl>
          {latest && (
            <div className="mt-4 flex items-center gap-3">
              <span className="text-sm text-slate-600">Current status:</span>
              <StatusBadge status={latest.status} />
              <span className="text-sm text-slate-600">Risk score: {latest.risk_score.toFixed(1)}</span>
            </div>
          )}
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-slate-800">Symptom score over time</h2>
          <LineChartCard title="" data={trendData} valueLabel="Symptom score" />
        </div>

        <div>
          <h2 className="mb-3 text-lg font-semibold text-slate-800">Check-ins</h2>
          <DataTable
            keyField="id"
            data={checkIns}
            columns={[
              { key: 'date', header: 'Date', render: (r) => formatDate(r.date) },
              { key: 'fatigue', header: 'Fatigue', render: (r) => r.fatigue },
              { key: 'breathlessness', header: 'Breathlessness', render: (r) => r.breathlessness },
              { key: 'cough', header: 'Cough', render: (r) => r.cough },
              { key: 'pain', header: 'Pain', render: (r) => r.pain },
              { key: 'nausea', header: 'Nausea', render: (r) => r.nausea ?? 0 },
              { key: 'dizziness', header: 'Dizziness', render: (r) => r.dizziness ?? 0 },
              { key: 'swelling', header: 'Swelling', render: (r) => r.swelling ?? 0 },
              { key: 'anxiety', header: 'Anxiety', render: (r) => r.anxiety ?? 0 },
              { key: 'sleep', header: 'Sleep', render: (r) => r.sleep_hours },
              { key: 'meds', header: 'Meds', render: (r) => (r.meds_taken ? 'Yes' : 'No') },
              { key: 'appetite', header: 'Appetite', render: (r) => r.appetite },
              { key: 'mobility', header: 'Mobility', render: (r) => r.mobility },
              { key: 'symptom', header: 'Symptom', render: (r) => r.symptom_score.toFixed(1) },
              { key: 'risk', header: 'Risk', render: (r) => r.risk_score.toFixed(1) },
              { key: 'status', header: 'Status', render: (r) => <StatusBadge status={r.status} /> },
            ]}
          />
        </div>

        <div className="flex flex-wrap gap-4">
          <button
            type="button"
            onClick={() => setFollowUpOpen(true)}
            className="rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700"
          >
            Create Follow-up Action
          </button>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700">Data Quality</h3>
          <ul className="mt-2 space-y-1 text-sm text-slate-600">
            <li>Missing fields (notes): {missingFields}</li>
            <li>Duplicates detected: {duplicatesDetected}</li>
            <li>Late submissions: {lateSubmissions}</li>
          </ul>
        </div>
      </div>

      <Modal open={followUpOpen} onClose={() => setFollowUpOpen(false)} title="Create Follow-up Action">
        <p className="text-sm text-slate-600">Mock: Follow-up action would be created here. No backend.</p>
        <div className="mt-4 flex justify-end">
          <button
            type="button"
            onClick={() => setFollowUpOpen(false)}
            className="rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700"
          >
            Close
          </button>
        </div>
      </Modal>
    </AppLayout>
  );
}
