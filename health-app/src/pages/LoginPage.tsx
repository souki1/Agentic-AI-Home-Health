import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login as apiLogin, register as apiRegister } from '../services/api';
import { ApiError } from '../services/client';
import type { Role } from '../types';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<Role>('patient');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const address = email || 'user@example.com';
      try {
        const response = await apiLogin(address, password);
        login(response);
        navigate(response.user.role === 'patient' ? '/patient/checkin' : '/admin/dashboard');
        return;
      } catch (err) {
        const is401 = err instanceof ApiError && err.status === 401;
        const message = err instanceof Error ? err.message : 'Login failed';
        if (!is401 && !message.toLowerCase().includes('invalid credentials')) {
          setError(message);
          return;
        }
        // 401 = user may not exist: auto-register then retry login
        try {
          await apiRegister({ email: address, password, role });
          const response = await apiLogin(address, password);
          login(response);
          navigate(response.user.role === 'patient' ? '/patient/checkin' : '/admin/dashboard');
        } catch (registerErr) {
          setError(registerErr instanceof Error ? registerErr.message : 'Registration or login failed');
        }
        return;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
        <h1 className="text-xl font-semibold text-slate-800">Sign in</h1>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Role</label>
            <div className="mt-2 flex gap-2">
              <button
                type="button"
                onClick={() => setRole('patient')}
                className={`flex-1 rounded-lg border py-2 text-sm font-medium transition ${
                  role === 'patient'
                    ? 'border-primary-600 bg-primary-600 text-white'
                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                }`}
              >
                Patient
              </button>
              <button
                type="button"
                onClick={() => setRole('admin')}
                className={`flex-1 rounded-lg border py-2 text-sm font-medium transition ${
                  role === 'admin'
                    ? 'border-primary-600 bg-primary-600 text-white'
                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                }`}
              >
                Admin
              </button>
            </div>
          </div>
          {error && <p className="text-sm text-amber-600">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-primary-600 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
        <p className="mt-6 text-center text-xs text-slate-400">
          Sign in with any email/password. Backend required (VITE_API_URL).
        </p>
      </div>
    </div>
  );
}
