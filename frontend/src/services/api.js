import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — attach JWT token
api.interceptors.request.use((config) => {
  // Check admin token first, then user token
  const adminToken = localStorage.getItem('adminToken');
  const userToken = localStorage.getItem('userToken');

  if (config.url?.startsWith('/admin') && adminToken) {
    config.headers.Authorization = `Bearer ${adminToken}`;
  } else if (userToken) {
    config.headers.Authorization = `Bearer ${userToken}`;
  }

  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const isAdminRoute = error.config?.url?.startsWith('/admin');
      if (isAdminRoute) {
        localStorage.removeItem('adminToken');
        if (window.location.pathname.startsWith('/admin')) {
          window.location.href = '/admin/login';
        }
      } else {
        localStorage.removeItem('userToken');
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;