import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAdminAuth } from '../../context/AdminAuthContext';
import { motion } from 'framer-motion';
import { HiOutlineCog, HiOutlineMail, HiOutlineLockClosed } from 'react-icons/hi';
import toast from 'react-hot-toast';

const AdminLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error } = useAdminAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(email, password);
    if (success) {
      toast.success('Welcome, Admin!');
      navigate('/admin/home');
    } else {
      toast.error(error || 'Invalid admin credentials');
    }
  };

  return (
    <div className="auth-page">
      <motion.div
        className="auth-card"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="auth-header">
          <div className="auth-icon" style={{ background: 'linear-gradient(135deg, #8b5cf6, #6366f1)' }}>
            <HiOutlineCog />
          </div>
          <h1>Admin Portal</h1>
          <p>Loan underwriting management console</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Admin Email</label>
            <input id="admin-email" className="form-input" type="email" placeholder="admin@loanai.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input id="admin-password" className="form-input" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>

          {error && <div className="form-error" style={{ marginBottom: '1rem' }}>{error}</div>}

          <button id="admin-login-submit" type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading} style={{ background: 'linear-gradient(135deg, #8b5cf6, #6366f1)' }}>
            {loading ? <span className="spinner" style={{ width: 20, height: 20 }}></span> : 'Sign In as Admin'}
          </button>
        </form>

        <div className="auth-footer">
          <Link to="/login">← Back to User Login</Link>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminLogin;