import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { store } from '../mock/store';
import { toISODate } from '../utils';
import type { CheckIn, Appetite, Mobility } from '../types';
import { AppLayout } from '../components/layout';
import { FormSlider, Toggle, Toast } from '../components';

const MOCK_PATIENT_ID = 'p1';

export function PatientCheckinPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [toastVisible, setToastVisible] = useState(false);
  const [form, setForm] = useState<Omit<CheckIn, 'id' | 'patient_id'>>({
    date: toISODate(new Date()),
    fatigue: 0,
    breathlessness: 0,
    cough: 0,
    pain: 0,
    nausea: 0,
    dizziness: 0,
    swelling: 0,
    anxiety: 0,
    sleep_hours: 7,
    meds_taken: true,
    appetite: 'Normal',
    mobility: 'Normal',
    notes: '',
  });

  const handleSave = () => {
    store.addCheckIn({ ...form, patient_id: MOCK_PATIENT_ID });
    setToastVisible(true);
    setTimeout(() => navigate('/patient/history'), 800);
  };

  const handleReset = () => {
    setForm({
      date: toISODate(new Date()),
      fatigue: 0,
      breathlessness: 0,
      cough: 0,
      pain: 0,
      nausea: 0,
      dizziness: 0,
      swelling: 0,
      anxiety: 0,
      sleep_hours: 7,
      meds_taken: true,
      appetite: 'Normal',
      mobility: 'Normal',
      notes: '',
    });
  };

  return (
    <AppLayout role="patient" email={user?.email ?? ''} pageTitle="Daily Check-in">
      <div className="mx-auto max-w-5xl">
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-800">Date</h2>
              <input
                type="date"
                value={form.date}
                onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))}
                className="mt-2 rounded-lg border border-slate-200 px-3 py-2 text-sm"
              />
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-slate-800">Symptoms (0–10)</h2>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-4">
                  <FormSlider label="Fatigue" value={form.fatigue} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, fatigue: v }))} />
                  <FormSlider label="Breathlessness" value={form.breathlessness} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, breathlessness: v }))} />
                  <FormSlider label="Cough" value={form.cough} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, cough: v }))} />
                  <FormSlider label="Pain" value={form.pain} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, pain: v }))} />
                </div>
                <div className="space-y-4">
                  <FormSlider label="Nausea" value={form.nausea} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, nausea: v }))} />
                  <FormSlider label="Dizziness" value={form.dizziness} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, dizziness: v }))} />
                  <FormSlider label="Swelling" value={form.swelling} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, swelling: v }))} />
                  <FormSlider label="Anxiety" value={form.anxiety} min={0} max={10} onChange={(v) => setForm((f) => ({ ...f, anxiety: v }))} />
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-slate-800">Daily factors</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">Sleep (hours)</label>
                  <input
                    type="number"
                    min={0}
                    max={12}
                    value={form.sleep_hours}
                    onChange={(e) => setForm((f) => ({ ...f, sleep_hours: Number(e.target.value) || 0 }))}
                    className="mt-1 w-24 rounded-lg border border-slate-200 px-3 py-2 text-sm"
                  />
                </div>
                <Toggle label="Medication taken" value={form.meds_taken} onChange={(v) => setForm((f) => ({ ...f, meds_taken: v }))} />
                <div>
                  <label className="block text-sm font-medium text-slate-700">Appetite</label>
                  <select
                    value={form.appetite}
                    onChange={(e) => setForm((f) => ({ ...f, appetite: e.target.value as Appetite }))}
                    className="mt-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
                  >
                    <option value="Normal">Normal</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Mobility</label>
                  <select
                    value={form.mobility}
                    onChange={(e) => setForm((f) => ({ ...f, mobility: e.target.value as Mobility }))}
                    className="mt-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
                  >
                    <option value="Normal">Normal</option>
                    <option value="Reduced">Reduced</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <label className="block text-sm font-medium text-slate-700">Notes (optional)</label>
              <textarea
                value={form.notes ?? ''}
                onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
                rows={3}
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                placeholder="Any additional notes..."
              />
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleSave}
                className="rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700"
              >
                Save Check-in
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Reset
              </button>
            </div>
          </div>
          <div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-800">How it works</h3>
              <p className="mt-2 text-sm text-slate-600">
                Submit one check-in per day. Sliders are 0 (none) to 10 (severe). Your symptom and risk scores are computed automatically. Care teams may follow up if scores suggest support is needed.
              </p>
              <h3 className="mt-4 font-semibold text-slate-800">Tips</h3>
              <ul className="mt-2 list-inside list-disc text-sm text-slate-600">
                <li>Be consistent with the time of day</li>
                <li>Include notes if something changed</li>
                <li>Mark meds and sleep honestly for better insights</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <Toast message="Check-in saved" visible={toastVisible} onDismiss={() => setToastVisible(false)} />
    </AppLayout>
  );
}
