import { useEffect } from 'react';

interface ToastProps {
  message: string;
  visible: boolean;
  onDismiss: () => void;
  duration?: number;
}

export function Toast({ message, visible, onDismiss, duration = 3000 }: ToastProps) {
  useEffect(() => {
    if (!visible) return;
    const t = setTimeout(onDismiss, duration);
    return () => clearTimeout(t);
  }, [visible, onDismiss, duration]);

  if (!visible) return null;
  return (
    <div className="fixed bottom-6 right-6 z-50 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800 shadow-lg">
      {message}
    </div>
  );
}
