interface DateRangeFilterProps {
  value: '7' | '30' | 'custom';
  customStart?: string;
  customEnd?: string;
  onRangeChange: (range: '7' | '30' | 'custom') => void;
  onCustomStartChange?: (date: string) => void;
  onCustomEndChange?: (date: string) => void;
}

export function DateRangeFilter({
  value,
  customStart,
  customEnd,
  onRangeChange,
  onCustomStartChange,
  onCustomEndChange,
}: DateRangeFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <span className="text-sm font-medium text-slate-600">Period:</span>
      <div className="flex rounded-lg border border-slate-200 bg-white p-0.5 shadow-sm">
        <button
          type="button"
          onClick={() => onRangeChange('7')}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
            value === '7' ? 'bg-primary-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Last 7 days
        </button>
        <button
          type="button"
          onClick={() => onRangeChange('30')}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
            value === '30' ? 'bg-primary-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Last 30 days
        </button>
        <button
          type="button"
          onClick={() => onRangeChange('custom')}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
            value === 'custom' ? 'bg-primary-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Custom
        </button>
      </div>
      {value === 'custom' && onCustomStartChange && onCustomEndChange && (
        <div className="flex items-center gap-2">
          <input
            type="date"
            value={customStart ?? ''}
            onChange={(e) => onCustomStartChange(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm"
          />
          <span className="text-slate-400">to</span>
          <input
            type="date"
            value={customEnd ?? ''}
            onChange={(e) => onCustomEndChange(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm"
          />
        </div>
      )}
    </div>
  );
}
