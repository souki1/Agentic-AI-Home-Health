import type { Status } from '../types';
import { getStatusColor } from '../utils';

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${getStatusColor(status)} ${className}`}
    >
      {status}
    </span>
  );
}
