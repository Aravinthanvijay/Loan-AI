import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import userService from '../../services/userService';
import DecisionResult from './DecisionResult';
import { HiOutlineRefresh } from 'react-icons/hi';

const AGENTS = [
  { key: 'agent1', name: 'Intake Validation', desc: 'PAN check, blacklist, duplicates' },
  { key: 'agent2', name: 'Document Verification', desc: 'OCR extraction, cross-validation' },
  { key: 'agent3', name: 'Credit Scoring', desc: 'ML model, default probability' },
  { key: 'agent4', name: 'Rules Engine', desc: 'Business rule evaluation' },
  { key: 'agent5', name: 'Policy Compliance', desc: 'RAG policy check' },
  { key: 'agent6', name: 'AI Decision', desc: 'LLM-powered final decision' },
];

const ApplicationStatus = ({ applicationId }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await userService.getApplicationStatus(applicationId);
      setStatus(res.data);
      // Stop polling if done
      if (['approved', 'rejected', 'pending_admin', 'failed'].includes(res.data?.status)) {
        setPolling(false);
      }
    } catch (err) {
      console.error('Failed to fetch status', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    setPolling(true);
  }, [applicationId]);

  useEffect(() => {
    if (!polling) return;
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [polling]);

  if (loading) return <div className="loading-screen"><div className="spinner"></div><p style={{ color: 'var(--text-muted)' }}>Loading status...</p></div>;
  if (!status) return <div className="empty-state"><h3>Application not found</h3></div>;

  const progress = status.agent_progress || {};
  const statusValue = status.status;

  return (
    <div>
      <div className="flex-between mb-3">
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Application {status.application_id}</h2>
          <span className={`badge badge-${statusValue}`}>{statusValue?.replace('_', ' ')}</span>
        </div>
        <button className="btn btn-outline btn-sm" onClick={fetchStatus}><HiOutlineRefresh /> Refresh</button>
      </div>

      {/* Agent Pipeline */}
      <div className="glass-card mb-3">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Processing Pipeline</h3>
        <div className="agent-timeline">
          {AGENTS.map((agent, i) => {
            const done = progress[agent.key];
            const isLast = i === AGENTS.length - 1;
            const prevDone = i === 0 ? true : progress[AGENTS[i-1].key];
            const isRunning = !done && prevDone && statusValue === 'processing';

            return (
              <div key={agent.key} className={`agent-step ${done ? 'completed' : ''} ${isRunning ? 'running' : ''}`}>
                <div className="agent-dot"></div>
                <div className="agent-name">{agent.name}</div>
                <div className="agent-desc">{done ? '✓ Complete' : isRunning ? '⟳ Processing...' : agent.desc}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Decision Result */}
      {(statusValue === 'approved' || statusValue === 'rejected' || statusValue === 'pending_admin') && (
        <DecisionResult status={status} />
      )}
    </div>
  );
};

export default ApplicationStatus;