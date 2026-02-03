import type { ReactNode } from 'react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
}

export function KpiCard({ title, value, subtitle, icon }: KpiCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
          {subtitle && <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>}
        </div>
        {icon && <div className="text-slate-300">{icon}</div>}
      </div>
    </div>
  );
}
