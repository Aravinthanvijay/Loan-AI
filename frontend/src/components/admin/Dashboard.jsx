import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { HiOutlineDocumentText, HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineClock, HiOutlineChartBar } from 'react-icons/hi';
import adminService from '../../services/adminService';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await adminService.getDashboardStats();
        setStats(res.data);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  if (loading) return <div className="loading-screen"><div className="spinner"></div></div>;

  const cards = [
    { label: 'Total Applications', value: stats?.total || 0, color: 'blue', icon: <HiOutlineDocumentText /> },
    { label: 'Approved', value: stats?.approved || 0, color: 'emerald', icon: <HiOutlineCheckCircle /> },
    { label: 'Rejected', value: stats?.rejected || 0, color: 'red', icon: <HiOutlineXCircle /> },
    { label: 'Pending Review', value: stats?.pending_review || 0, color: 'amber', icon: <HiOutlineClock /> },
  ];

  const total = stats?.total || 1;
  const approvalRate = stats?.total > 0 ? ((stats.approved / total) * 100).toFixed(1) : 0;

  return (
    <div>
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        {cards.map((card, i) => (
          <motion.div key={i} className={`stat-card ${card.color}`} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <div className="stat-icon">{card.icon}</div>
            <div className="stat-value">{card.value}</div>
            <div className="stat-label">{card.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Approval Rate Card */}
      <div className="glass-card" style={{ maxWidth: 400 }}>
        <div className="flex-between mb-2">
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Approval Rate</h3>
          <HiOutlineChartBar style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }} />
        </div>
        <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--accent-emerald-light)' }}>{approvalRate}%</div>
        <div className="confidence-bar" style={{ marginTop: '0.75rem' }}>
          <div className="confidence-fill high" style={{ width: `${approvalRate}%` }}></div>
        </div>
        <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          {stats?.approved || 0} approved out of {stats?.total || 0} total • {stats?.processing || 0} processing
        </div>
      </div>
    </div>
  );
};

export default Dashboard;