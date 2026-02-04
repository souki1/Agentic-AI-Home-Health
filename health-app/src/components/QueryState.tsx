import type { ReactNode } from "react";

interface QueryStateProps {
  loading: boolean;
  error: string | null;
  children: ReactNode;
  loadingMessage?: string;
}

export function QueryState({
  loading,
  error,
  children,
  loadingMessage = "Loading…",
}: QueryStateProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-slate-500">
        {loadingMessage}
      </div>
    );
  }
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
        {error}
      </div>
    );
  }
  return <>{children}</>;
}
