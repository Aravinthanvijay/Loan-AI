import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { AdminAuthProvider } from './context/AdminAuthContext';
import ProtectedRoute from './components/shared/ProtectedRoute';

// Pages
import Login from './components/shared/Login';
import AdminLogin from './components/shared/AdminLogin';
import UserHome from './pages/user/UserHome';
import Apply from './pages/user/Apply';
import MyApplications from './pages/user/MyApplications';
import AdminHome from './pages/admin/AdminHome';
import ReviewApplication from './pages/admin/ReviewApplication';
import AdminSettings from './pages/admin/AdminSettings';

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <AdminAuthProvider>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#1a2035',
                color: '#f1f5f9',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                fontSize: '0.9rem',
              },
              success: { iconTheme: { primary: '#10b981', secondary: '#fff' } },
              error: { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
            }}
          />
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/admin/login" element={<AdminLogin />} />

            {/* User Protected Routes */}
            <Route path="/user/home" element={<ProtectedRoute><UserHome /></ProtectedRoute>} />
            <Route path="/user/apply" element={<ProtectedRoute><Apply /></ProtectedRoute>} />
            <Route path="/user/applications" element={<ProtectedRoute><MyApplications /></ProtectedRoute>} />

            {/* Admin Protected Routes */}
            <Route path="/admin/home" element={<ProtectedRoute isAdmin><AdminHome /></ProtectedRoute>} />
            <Route path="/admin/review" element={<ProtectedRoute isAdmin><ReviewApplication /></ProtectedRoute>} />
            <Route path="/admin/settings" element={<ProtectedRoute isAdmin><AdminSettings /></ProtectedRoute>} />

            {/* Default Route */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </AdminAuthProvider>
      </AuthProvider>
    </Router>
  );
};

export default App;