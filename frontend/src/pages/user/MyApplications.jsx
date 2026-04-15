import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Navbar from '../../components/shared/Navbar';
import ApplicationStatus from '../../components/user/ApplicationStatus';
import userService from '../../services/userService';
import { HiOutlineDocumentText, HiOutlineEye, HiOutlineArrowLeft } from 'react-icons/hi';

const MyApplications = () => {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await userService.getMyApplications();
        setApps(res.data || []);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '-';
  const formatAmount = (a) => a ? `₹${Number(a).toLocaleString('en-IN')}` : '-';

  return (
    <>
      <Navbar />
      <div className="page-container">
        {selectedId ? (
          <div>
            <button className="btn btn-ghost mb-2" onClick={() => setSelectedId(null)}>
              <HiOutlineArrowLeft /> Back to list
            </button>
            <ApplicationStatus applicationId={selectedId} />
          </div>
        ) : (
          <>
            <div className="page-header">
              <h1>My Applications</h1>
              <p>Track and monitor all your loan applications</p>
            </div>

            {loading ? (
              <div className="loading-screen"><div className="spinner"></div></div>
            ) : apps.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📋</div>
                <h3>No applications yet</h3>
                <p style={{ marginBottom: '1rem' }}>Submit your first loan application to get started</p>
                <a href="/user/apply" className="btn btn-primary">Apply Now</a>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {apps.map((app, i) => (
                  <motion.div key={app.application_id} className="glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                    style={{ cursor: 'pointer' }} onClick={() => setSelectedId(app.application_id)}>
                    <div className="flex-between">
                      <div>
                        <div className="flex gap-1" style={{ alignItems: 'center', marginBottom: '0.5rem' }}>
                          <HiOutlineDocumentText style={{ color: 'var(--accent-blue-light)' }} />
                          <span style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--accent-blue-light)' }}>{app.application_id}</span>
                          <span className={`badge badge-${app.status}`}>{app.status?.replace('_', ' ')}</span>
                        </div>
                        <div className="flex gap-2" style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                          <span>{formatAmount(app.loan_amount)}</span>
                          <span>•</span>
                          <span style={{ textTransform: 'capitalize' }}>{app.loan_purpose}</span>
                          <span>•</span>
                          <span>{formatDate(app.created_at)}</span>
                        </div>
                      </div>
                      <button className="btn btn-outline btn-sm"><HiOutlineEye /> View</button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
};

export default MyApplications;