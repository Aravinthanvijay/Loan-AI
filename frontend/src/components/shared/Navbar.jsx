import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useAdminAuth } from '../../context/AdminAuthContext';
import { HiOutlineShieldCheck, HiOutlineLogout } from 'react-icons/hi';

const Navbar = ({ isAdmin = false }) => {
  const location = useLocation();
  const { logout: userLogout } = useAuth();
  const { admin, logout: adminLogout } = useAdminAuth();

  const isActive = (path) => location.pathname === path ? 'active' : '';

  if (isAdmin) {
    return (
      <nav className="navbar">
        <div className="navbar-inner">
          <Link to="/admin/home" className="navbar-brand">
            <div className="brand-icon" style={{ background: 'linear-gradient(135deg, #8b5cf6, #6366f1)' }}>⚙</div>
            <span>LoanAI <span style={{ color: 'var(--accent-purple)', fontSize: '0.75rem' }}>ADMIN</span></span>
          </Link>
          <div className="navbar-links">
            <Link to="/admin/home" className={isActive('/admin/home')}>Dashboard</Link>
            <Link to="/admin/review" className={isActive('/admin/review')}>Applications</Link>
            <Link to="/admin/settings" className={isActive('/admin/settings')}>Settings</Link>
            <button className="nav-logout" onClick={adminLogout}>
              <HiOutlineLogout style={{ marginRight: 4 }} /> Logout
            </button>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/user/home" className="navbar-brand">
          <div className="brand-icon">🏦</div>
          <span>LoanAI</span>
        </Link>
        <div className="navbar-links">
          <Link to="/user/home" className={isActive('/user/home')}>Home</Link>
          <Link to="/user/apply" className={isActive('/user/apply')}>Apply</Link>
          <Link to="/user/applications" className={isActive('/user/applications')}>My Applications</Link>
          <button className="nav-logout" onClick={userLogout}>
            <HiOutlineLogout style={{ marginRight: 4 }} /> Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;