import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface DataPoint {
  date: string;
  value: number;
  label?: string;
}

interface LineChartCardProps {
  title: string;
  data: DataPoint[];
  dataKey?: string;
  valueLabel?: string;
  color?: string;
}

export function LineChartCard({
  title,
  data,
  dataKey = 'value',
  valueLabel = 'Value',
  color = '#2563eb',
}: LineChartCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-slate-700">{title}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#64748b" />
            <YAxis tick={{ fontSize: 11 }} stroke="#64748b" />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
              formatter={(value) => [value ?? 0, valueLabel]}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
