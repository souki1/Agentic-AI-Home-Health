import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import {
  LoginPage,
  PatientCheckinPage,
  PatientHistoryPage,
  AdminDashboardPage,
  AdminPatientsPage,
  AdminPatientDetailPage,
  ChatPage,
} from './pages';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/patient/checkin"
            element={
              <ProtectedRoute allowedRole="patient">
                <PatientCheckinPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/patient/history"
            element={
              <ProtectedRoute allowedRole="patient">
                <PatientHistoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/patients"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminPatientsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/patients/:id"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminPatientDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <ProtectedRoute allowedRoles={['patient', 'admin']}>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
