import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Navbar from '../../components/shared/Navbar';
import { motion } from 'framer-motion';
import { HiOutlineDocumentAdd, HiOutlineCollection, HiOutlineShieldCheck, HiOutlineLightningBolt, HiOutlineClock, HiOutlineChip } from 'react-icons/hi';

const UserHome = () => {
  const { user } = useAuth();

  const features = [
    { icon: <HiOutlineLightningBolt />, title: 'Instant Processing', desc: '6 AI agents analyze your application in real-time' },
    { icon: <HiOutlineShieldCheck />, title: 'Secure & Private', desc: 'Bank-grade encryption for all your documents' },
    { icon: <HiOutlineClock />, title: 'Quick Decision', desc: 'Get AI-powered decision within minutes' },
    { icon: <HiOutlineChip />, title: 'Smart Analysis', desc: 'ML-powered credit scoring with explainable AI' },
  ];

  return (
    <>
      <Navbar />
      <div className="page-container">
        {/* Hero */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ textAlign: 'center', padding: '3rem 0 2rem' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '1rem', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            AI-Powered Loan Underwriting
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', maxWidth: 600, margin: '0 auto 2rem' }}>
            {user?.full_name ? `Welcome back, ${user.full_name}!` : 'Welcome!'} Apply for a loan and get an instant AI-driven decision with full transparency.
          </p>
          <div className="flex-center gap-2">
            <Link to="/user/apply" className="btn btn-primary btn-lg">
              <HiOutlineDocumentAdd /> Apply for Loan
            </Link>
            <Link to="/user/applications" className="btn btn-outline btn-lg">
              <HiOutlineCollection /> My Applications
            </Link>
          </div>
        </motion.div>

        {/* Feature Cards */}
        <div className="grid-4" style={{ marginTop: '3rem' }}>
          {features.map((f, i) => (
            <motion.div key={i} className="glass-card text-center" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 + i * 0.1 }}>
              <div style={{ fontSize: '2rem', color: 'var(--accent-blue-light)', marginBottom: '0.75rem' }}>{f.icon}</div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>{f.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </>
  );
};

export default UserHome;