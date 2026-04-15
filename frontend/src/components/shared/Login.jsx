import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { motion } from 'framer-motion';
import { HiOutlineShieldCheck, HiOutlineMail, HiOutlineLockClosed } from 'react-icons/hi';
import toast from 'react-hot-toast';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [panNumber, setPanNumber] = useState('');
  const { login, register, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    let success;
    if (isRegister) {
      success = await register({ email, password, full_name: fullName, phone, pan_number: panNumber });
    } else {
      success = await login(email, password);
    }
    if (success) {
      toast.success(isRegister ? 'Account created!' : 'Welcome back!');
      navigate('/user/home');
    } else {
      toast.error(error || 'Authentication failed');
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
          <div className="auth-icon">
            <HiOutlineShieldCheck />
          </div>
          <h1>{isRegister ? 'Create Account' : 'Welcome Back'}</h1>
          <p>{isRegister ? 'Start your loan application journey' : 'Sign in to your account'}</p>
        </div>

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="form-input" type="text" placeholder="Rahul Kumar Sharma" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <input className="form-input" type="tel" placeholder="9876543210" value={phone} onChange={(e) => setPhone(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">PAN Number</label>
                <input className="form-input" type="text" placeholder="ABCDE1234F" value={panNumber} onChange={(e) => setPanNumber(e.target.value.toUpperCase())} required maxLength={10} />
              </div>
            </>
          )}

          <div className="form-group">
            <label className="form-label">Email</label>
            <input id="login-email" className="form-input" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input id="login-password" className="form-input" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
          </div>

          {error && <div className="form-error" style={{ marginBottom: '1rem' }}>{error}</div>}

          <button id="login-submit" type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading}>
            {loading ? <span className="spinner" style={{ width: 20, height: 20 }}></span> : (isRegister ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); setIsRegister(!isRegister); setEmail(''); setPassword(''); }}>
              {isRegister ? 'Sign In' : 'Register'}
            </a>
          </p>
          <p style={{ marginTop: '0.5rem' }}>
            <Link to="/admin/login">Admin Login →</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;