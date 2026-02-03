interface FormSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}

export function FormSlider({ label, value, min, max, onChange }: FormSliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <label className="font-medium text-slate-700">{label}</label>
        <span className="text-slate-500">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-primary-600"
      />
    </div>
  );
}
