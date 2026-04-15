import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AdminAuthContext = createContext();

export const AdminAuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('adminToken'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      localStorage.setItem('adminToken', token);
    } else {
      localStorage.removeItem('adminToken');
      setAdmin(null);
    }
  }, [token]);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/auth/admin/login', { email, password });
      const data = response.data.data;
      setToken(data.access_token);
      setAdmin({ admin_id: data.admin_id, email: data.email, full_name: data.full_name, role: data.role });
      return true;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Admin login failed';
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setAdmin(null);
    setToken(null);
  };

  return (
    <AdminAuthContext.Provider value={{ admin, token, loading, error, login, logout, isAuthenticated: !!token }}>
      {children}
    </AdminAuthContext.Provider>
  );
};

export const useAdminAuth = () => {
  const context = useContext(AdminAuthContext);
  if (!context) throw new Error('useAdminAuth must be used within AdminAuthProvider');
  return context;
};