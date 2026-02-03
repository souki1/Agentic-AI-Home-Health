import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { Role } from '../../types';

interface SidebarProps {
  role: Role;
}

const patientNav = [
  { to: '/patient/checkin', label: 'Daily Check-in' },
  { to: '/patient/history', label: 'History' },
  { to: '/chat', label: 'AI Chat' },
];

const adminNav = [
  { to: '/admin/dashboard', label: 'Dashboard' },
  { to: '/admin/patients', label: 'Patients' },
  { to: '/chat', label: 'AI Chat' },
];

export function Sidebar({ role }: SidebarProps) {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const nav = role === 'admin' ? adminNav : patientNav;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="fixed left-0 top-0 z-30 flex h-full w-56 flex-col border-r border-slate-200 bg-white shadow-sm">
      <div className="flex h-14 items-center border-b border-slate-200 px-4">
        <span className="text-lg font-semibold text-slate-800">Home Health Analytics</span>
      </div>
      <nav className="flex-1 space-y-0.5 p-3">
        {nav.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                isActive ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-slate-200 p-3">
        <button
          type="button"
          onClick={handleLogout}
          className="block w-full rounded-lg px-3 py-2.5 text-left text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}
