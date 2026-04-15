import React, { useState, useEffect } from 'react';
import adminService from '../../services/adminService';
import { HiOutlineSearch, HiOutlineFilter, HiOutlineChevronRight } from 'react-icons/hi';

const ApplicationList = ({ onSelect }) => {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');

  const fetchApps = async () => {
    setLoading(true);
    try {
      const res = await adminService.getAllApplications(page, statusFilter || null);
      setApps(res.data || []);
      setTotalPages(res.pagination?.pages || 1);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchApps(); }, [page, statusFilter]);

  const filtered = search
    ? apps.filter(a =>
        (a.full_name || '').toLowerCase().includes(search.toLowerCase()) ||
        (a.application_id || '').toLowerCase().includes(search.toLowerCase()) ||
        (a.pan_number || '').toLowerCase().includes(search.toLowerCase())
      )
    : apps;

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '-';
  const formatAmount = (a) => a ? `₹${Number(a).toLocaleString('en-IN')}` : '-';

  return (
    <div>
      {/* Filters */}
      <div className="flex gap-2 mb-3" style={{ flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
          <HiOutlineSearch style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input className="form-input" style={{ paddingLeft: '2.5rem' }} placeholder="Search by name, ID, PAN..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="form-select" style={{ width: 180 }} value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="submitted">Submitted</option>
          <option value="processing">Processing</option>
          <option value="pending_admin">Pending Review</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Table */}
      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div className="loading-screen" style={{ minHeight: 200 }}><div className="spinner"></div></div>
        ) : filtered.length === 0 ? (
          <div className="empty-state"><div className="empty-icon">📋</div><h3>No applications found</h3></div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Application ID</th>
                <th>Applicant</th>
                <th>Amount</th>
                <th>Purpose</th>
                <th>Status</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(app => (
                <tr key={app.application_id} className="clickable" onClick={() => onSelect && onSelect(app.application_id)}>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--accent-blue-light)' }}>{app.application_id}</td>
                  <td>
                    <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{app.full_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{app.pan_number}</div>
                  </td>
                  <td style={{ fontWeight: 600 }}>{formatAmount(app.loan_amount)}</td>
                  <td><span className="tag">{app.loan_purpose}</span></td>
                  <td><span className={`badge badge-${app.status}`}>{app.status?.replace('_', ' ')}</span></td>
                  <td style={{ fontSize: '0.85rem' }}>{formatDate(app.created_at)}</td>
                  <td><HiOutlineChevronRight style={{ color: 'var(--text-muted)' }} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => setPage(p => p - 1)} disabled={page <= 1}>‹</button>
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
            <button key={p} onClick={() => setPage(p)} className={page === p ? 'active' : ''}>{p}</button>
          ))}
          <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages}>›</button>
        </div>
      )}
    </div>
  );
};

export default ApplicationList;