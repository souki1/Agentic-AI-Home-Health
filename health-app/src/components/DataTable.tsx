import type { ReactNode } from 'react';

interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField: keyof T | ((row: T) => string);
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
}

export function DataTable<T>({ columns, data, keyField, onRowClick, emptyMessage = 'No data' }: DataTableProps<T>) {
  const getKey = (row: T) =>
    typeof keyField === 'function' ? keyField(row) : String((row as Record<string, unknown>)[keyField as string]);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-600"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white">
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-sm text-slate-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row) => (
                <tr
                  key={getKey(row)}
                  onClick={() => onRowClick?.(row)}
                  className={
                    onRowClick
                      ? 'cursor-pointer transition-colors hover:bg-slate-50'
                      : ''
                  }
                >
                  {columns.map((col) => (
                    <td key={col.key} className="whitespace-nowrap px-4 py-3 text-sm text-slate-700">
                      {col.render(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
