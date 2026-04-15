import React, { useState } from 'react';
import Navbar from '../../components/shared/Navbar';
import { useAdminAuth } from '../../context/AdminAuthContext';
import adminService from '../../services/adminService';
import toast from 'react-hot-toast';
import { HiOutlineBan, HiOutlineShieldCheck } from 'react-icons/hi';

const AdminSettings = () => {
  const { admin } = useAdminAuth();
  const [pan, setPan] = useState('');
  const [reason, setReason] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAddBlacklist = async (e) => {
    e.preventDefault();
    if (!pan || !reason) return;
    setLoading(true);
    try {
      await adminService.addToBlacklist(pan, reason, name);
      toast.success(`PAN ${pan} added to blacklist`);
      setPan(''); setReason(''); setName('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add to blacklist');
    } finally { setLoading(false); }
  };

  return (
    <>
      <Navbar isAdmin />
      <div className="page-container">
        <div className="page-header">
          <h1>Admin Settings</h1>
          <p>Manage system configuration and blacklist</p>
        </div>

        <div className="grid-2">
          {/* Admin Profile */}
          <div className="glass-card">
            <h3 className="flex gap-1 mb-2" style={{ fontSize: '1rem', fontWeight: 600 }}>
              <HiOutlineShieldCheck /> Admin Profile
            </h3>
            <div style={{ display: 'grid', gap: '0.75rem', fontSize: '0.9rem' }}>
              <div className="flex-between">
                <span style={{ color: 'var(--text-muted)' }}>Name</span>
                <span style={{ fontWeight: 500 }}>{admin?.full_name || 'Admin'}</span>
              </div>
              <div className="flex-between">
                <span style={{ color: 'var(--text-muted)' }}>Email</span>
                <span style={{ fontWeight: 500 }}>{admin?.email || '-'}</span>
              </div>
              <div className="flex-between">
                <span style={{ color: 'var(--text-muted)' }}>Role</span>
                <span className="badge badge-processing">{admin?.role || 'admin'}</span>
              </div>
            </div>
          </div>

          {/* Add to Blacklist */}
          <div className="glass-card">
            <h3 className="flex gap-1 mb-2" style={{ fontSize: '1rem', fontWeight: 600 }}>
              <HiOutlineBan /> Add to Blacklist
            </h3>
            <form onSubmit={handleAddBlacklist}>
              <div className="form-group">
                <label className="form-label">PAN Number *</label>
                <input className="form-input" placeholder="ABCDE1234F" value={pan} onChange={e => setPan(e.target.value.toUpperCase())} maxLength={10} required />
              </div>
              <div className="form-group">
                <label className="form-label">Name</label>
                <input className="form-input" placeholder="Person name (optional)" value={name} onChange={e => setName(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Reason *</label>
                <textarea className="form-textarea" placeholder="Reason for blacklisting..." value={reason} onChange={e => setReason(e.target.value)} required />
              </div>
              <button className="btn btn-danger btn-full" type="submit" disabled={loading}>
                {loading ? <span className="spinner" style={{ width: 18, height: 18 }}></span> : <><HiOutlineBan /> Add to Blacklist</>}
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default AdminSettings;