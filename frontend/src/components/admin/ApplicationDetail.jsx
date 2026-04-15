import React, { useState, useEffect } from 'react';
import adminService from '../../services/adminService';
import AgentTrace from './AgentTrace';
import CreditReport from './CreditReport';
import HumanDecision from './HumanDecision';
import { HiOutlineArrowLeft, HiOutlineUser, HiOutlineBriefcase, HiOutlineCurrencyRupee } from 'react-icons/hi';
import { motion } from 'framer-motion';

const ApplicationDetail = ({ applicationId, onBack }) => {
  const [app, setApp] = useState(null);
  const [trace, setTrace] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [appRes, traceRes] = await Promise.all([
          adminService.getApplicationDetail(applicationId),
          adminService.getAgentTrace(applicationId),
        ]);
        setApp(appRes.data);
        setTrace(traceRes.data);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    fetchData();
  }, [applicationId]);

  if (loading) return <div className="loading-screen"><div className="spinner"></div></div>;
  if (!app) return <div className="empty-state"><h3>Application not found</h3></div>;

  const formatAmount = (a) => a ? `₹${Number(a).toLocaleString('en-IN')}` : '-';
  const tabs = ['overview', 'agents', 'credit', 'decision'];

  return (
    <div>
      <button className="btn btn-ghost mb-2" onClick={onBack}><HiOutlineArrowLeft /> Back to List</button>

      <div className="flex-between mb-3">
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>{app.full_name}</h2>
          <div className="flex gap-1 mt-1">
            <span className={`badge badge-${app.status}`}>{app.status?.replace('_', ' ')}</span>
            <span className="tag">{app.application_id}</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-3">
        {tabs.map(t => (
          <button key={t} className={`btn ${tab === t ? 'btn-primary' : 'btn-outline'} btn-sm`} onClick={() => setTab(t)} style={{ textTransform: 'capitalize' }}>
            {t}
          </button>
        ))}
      </div>

      <motion.div key={tab} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
        {tab === 'overview' && (
          <div className="grid-2">
            <div className="glass-card">
              <h3 className="flex gap-1 mb-2" style={{ fontSize: '1rem', fontWeight: 600 }}><HiOutlineUser /> Personal Info</h3>
              <div style={{ display: 'grid', gap: '0.5rem', fontSize: '0.9rem' }}>
                {[
                  ['Name', app.full_name],
                  ['Age', app.age],
                  ['PAN', app.pan_number],
                  ['Phone', app.phone],
                  ['Email', app.email],
                ].map(([k, v]) => (
                  <div key={k} className="flex-between">
                    <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                    <span style={{ fontWeight: 500 }}>{v || '-'}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card">
              <h3 className="flex gap-1 mb-2" style={{ fontSize: '1rem', fontWeight: 600 }}><HiOutlineBriefcase /> Employment</h3>
              <div style={{ display: 'grid', gap: '0.5rem', fontSize: '0.9rem' }}>
                {[
                  ['Type', app.employment_type],
                  ['Employer', app.employer_name || '-'],
                  ['Years', app.years_employed || '-'],
                  ['Monthly Income', formatAmount(app.monthly_income)],
                ].map(([k, v]) => (
                  <div key={k} className="flex-between">
                    <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                    <span style={{ fontWeight: 500 }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card" style={{ gridColumn: 'span 2' }}>
              <h3 className="flex gap-1 mb-2" style={{ fontSize: '1rem', fontWeight: 600 }}><HiOutlineCurrencyRupee /> Loan Details</h3>
              <div className="grid-3" style={{ fontSize: '0.9rem' }}>
                {[
                  ['Loan Amount', formatAmount(app.loan_amount)],
                  ['Purpose', app.loan_purpose],
                  ['Existing Loans', app.existing_loans],
                  ['Existing EMI', formatAmount(app.existing_emi)],
                  ['Decision', app.final_decision || 'Pending'],
                ].map(([k, v]) => (
                  <div key={k}>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 2 }}>{k}</div>
                    <div style={{ fontWeight: 600 }}>{v}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === 'agents' && <AgentTrace trace={trace} />}

        {tab === 'credit' && <CreditReport agent3={trace?.agent3_credit} />}

        {tab === 'decision' && (
          <HumanDecision application={app} onDecisionMade={() => {
            setLoading(true);
            adminService.getApplicationDetail(applicationId).then(res => {
              setApp(res.data);
              setLoading(false);
            });
          }} />
        )}
      </motion.div>
    </div>
  );
};

export default ApplicationDetail;