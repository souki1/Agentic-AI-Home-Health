import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { Role } from '../types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRole?: Role;
  /** If set, allow any role in this list (takes precedence over allowedRole) */
  allowedRoles?: Role[];
}

export function ProtectedRoute({ children, allowedRole, allowedRoles }: ProtectedRouteProps) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  const allowed = allowedRoles ?? (allowedRole != null ? [allowedRole] : []);
  if (allowed.length > 0 && !allowed.includes(user.role)) {
    const redirect = user.role === 'patient' ? '/patient/checkin' : '/admin/dashboard';
    return <Navigate to={redirect} replace />;
  }
  return <>{children}</>;
}
