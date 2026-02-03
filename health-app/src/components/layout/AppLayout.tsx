import type { ReactNode } from 'react';
import type { Role } from '../../types';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

interface AppLayoutProps {
  role: Role;
  email: string;
  pageTitle: string;
  children: ReactNode;
}

export function AppLayout({ role, email, pageTitle, children }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar role={role} />
      <div className="pl-56">
        <Topbar pageTitle={pageTitle} role={role} email={email} />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
