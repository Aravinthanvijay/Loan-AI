import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('userToken'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      localStorage.setItem('userToken', token);
    } else {
      localStorage.removeItem('userToken');
      setUser(null);
    }
  }, [token]);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/auth/login', { email, password });
      const data = response.data.data;
      setToken(data.access_token);
      setUser({ user_id: data.user_id, email: data.email, full_name: data.full_name });
      return true;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Login failed';
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/auth/register', userData);
      const data = response.data.data;
      setToken(data.access_token);
      setUser({ user_id: data.user_id, email: data.email });
      return true;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Registration failed';
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, error, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};