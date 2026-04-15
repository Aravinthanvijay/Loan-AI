import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useAdminAuth } from '../../context/AdminAuthContext';

const ProtectedRoute = ({ children, isAdmin = false }) => {
  const { token: userToken } = useAuth();
  const { token: adminToken } = useAdminAuth();

  if (isAdmin) {
    if (!adminToken) return <Navigate to="/admin/login" replace />;
  } else {
    if (!userToken) return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;