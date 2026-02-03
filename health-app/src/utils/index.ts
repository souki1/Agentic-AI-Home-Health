export {
  computeSymptomScore,
  computeRiskScore,
  computeStatus,
  getStatusColor,
} from './scores';

export function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatDateTime(d: string): string {
  return new Date(d).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function toISODate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function addDays(date: string, days: number): string {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return toISODate(d);
}
