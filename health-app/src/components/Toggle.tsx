interface ToggleProps {
  label: string;
  value: boolean;
  onChange: (value: boolean) => void;
  onLabel?: string;
  offLabel?: string;
}

export function Toggle({ label, value, onChange, onLabel = 'Yes', offLabel = 'No' }: ToggleProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      <label className="text-sm font-medium text-slate-700">{label}</label>
      <div className="flex items-center gap-2">
        <span className="text-sm text-slate-500">{value ? onLabel : offLabel}</span>
        <button
          type="button"
          role="switch"
          aria-checked={value}
          onClick={() => onChange(!value)}
          className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
            value ? 'bg-primary-600' : 'bg-slate-200'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition ${
              value ? 'translate-x-5' : 'translate-x-1'
            }`}
          />
        </button>
      </div>
    </div>
  );
}
