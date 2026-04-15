import React from 'react';
import { motion } from 'framer-motion';
import { HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineClock } from 'react-icons/hi';

const DecisionResult = ({ status }) => {
  const decision = status?.final_decision || status?.status;
  const isApproved = decision === 'approve' || decision === 'approved';
  const isRejected = decision === 'reject' || decision === 'rejected';
  const isPending = decision === 'pending_admin' || decision === 'manual_review';

  const bannerClass = isApproved ? 'approved' : isRejected ? 'rejected' : 'pending';
  const icon = isApproved ? <HiOutlineCheckCircle /> : isRejected ? <HiOutlineXCircle /> : <HiOutlineClock />;
  const text = isApproved ? 'Application Approved' : isRejected ? 'Application Rejected' : 'Pending Admin Review';

  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}>
      <div className={`decision-banner ${bannerClass}`}>
        <div className="decision-icon">{icon}</div>
        <div className="decision-text">{text}</div>
        {status?.confidence && (
          <div style={{ marginTop: '0.5rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              AI Confidence: {(status.confidence * 100).toFixed(0)}%
            </span>
            <div className="confidence-bar" style={{ maxWidth: 300, margin: '0.5rem auto 0' }}>
              <div
                className={`confidence-fill ${status.confidence > 0.75 ? 'high' : status.confidence > 0.5 ? 'medium' : 'low'}`}
                style={{ width: `${status.confidence * 100}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {status?.reasoning && (
        <div className="glass-card mb-2">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>AI Reasoning</h3>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>{status.reasoning}</p>
        </div>
      )}

      {status?.key_factors?.length > 0 && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Key Factors</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {status.key_factors.map((f, i) => <span key={i} className="tag">{f}</span>)}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default DecisionResult;