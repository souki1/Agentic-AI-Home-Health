import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { Role } from '../../types';

interface TopbarProps {
  pageTitle: string;
  role: Role;
  email: string;
}

export function Topbar({ pageTitle, role, email }: TopbarProps) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6 shadow-sm">
      <h1 className="text-lg font-semibold text-slate-800">{pageTitle}</h1>
      <div className="flex items-center gap-4">
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
          {role === 'admin' ? 'Admin' : 'Patient'}
        </span>
        <span className="text-sm text-slate-500">{email}</span>
        <button
          type="button"
          onClick={handleLogout}
          className="text-sm font-medium text-slate-600 hover:text-primary-600"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
