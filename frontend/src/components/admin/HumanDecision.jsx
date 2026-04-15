import React, { useState } from 'react';
import adminService from '../../services/adminService';
import { HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineExclamation } from 'react-icons/hi';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

const HumanDecision = ({ application, onDecisionMade }) => {
  const [notes, setNotes] = useState('');
  const [showConfirm, setShowConfirm] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!application) return null;

  const alreadyDecided = application.admin_decision || ['approved', 'rejected'].includes(application.status);
  const aiDecision = application.final_decision || application.agent6_result?.decision;
  const aiConfidence = application.agent6_result?.confidence;
  const aiReasoning = application.agent6_result?.reasoning;

  const handleDecision = async (decision) => {
    setSubmitting(true);
    try {
      await adminService.makeDecision(application.application_id, decision, notes);
      toast.success(`Application ${decision}d successfully`);
      setShowConfirm(null);
      onDecisionMade && onDecisionMade();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Decision failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      {/* AI Recommendation Summary */}
      {aiDecision && (
        <div className="glass-card mb-3">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>AI Recommendation</h3>
          <div className="flex gap-2 mb-2" style={{ alignItems: 'center' }}>
            <span className={`badge badge-${aiDecision}`} style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}>
              {aiDecision?.toUpperCase()}
            </span>
            {aiConfidence && (
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Confidence: {(aiConfidence * 100).toFixed(0)}%
              </span>
            )}
          </div>
          {aiReasoning && <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.7 }}>{aiReasoning}</p>}
        </div>
      )}

      {alreadyDecided ? (
        <div className="glass-card">
          <div className="flex gap-2" style={{ alignItems: 'center' }}>
            <HiOutlineCheckCircle style={{ color: 'var(--accent-emerald)', fontSize: '1.5rem' }} />
            <div>
              <div style={{ fontWeight: 600 }}>Decision Made: <span className={`badge badge-${application.admin_decision || application.status}`}>{(application.admin_decision || application.status)?.toUpperCase()}</span></div>
              {application.admin_notes && <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>Notes: {application.admin_notes}</div>}
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Make Decision</h3>
          <div className="form-group">
            <label className="form-label">Admin Notes (optional)</label>
            <textarea className="form-textarea" placeholder="Add your review notes here..." value={notes} onChange={e => setNotes(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <button className="btn btn-success btn-lg" style={{ flex: 1 }} onClick={() => setShowConfirm('approve')}>
              <HiOutlineCheckCircle /> Approve
            </button>
            <button className="btn btn-danger btn-lg" style={{ flex: 1 }} onClick={() => setShowConfirm('reject')}>
              <HiOutlineXCircle /> Reject
            </button>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      <AnimatePresence>
        {showConfirm && (
          <motion.div className="modal-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <motion.div className="modal-content" initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}>
              <div className="flex-center mb-2">
                <HiOutlineExclamation style={{ fontSize: '2.5rem', color: showConfirm === 'approve' ? 'var(--accent-emerald)' : 'var(--accent-red)' }} />
              </div>
              <h2 className="text-center">Confirm {showConfirm === 'approve' ? 'Approval' : 'Rejection'}</h2>
              <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
                Are you sure you want to <strong>{showConfirm}</strong> application <strong>{application.application_id}</strong>?
              </p>
              <div className="modal-actions">
                <button className="btn btn-outline" onClick={() => setShowConfirm(null)} disabled={submitting}>Cancel</button>
                <button className={`btn ${showConfirm === 'approve' ? 'btn-success' : 'btn-danger'}`} onClick={() => handleDecision(showConfirm)} disabled={submitting}>
                  {submitting ? <span className="spinner" style={{ width: 18, height: 18 }}></span> : `Yes, ${showConfirm}`}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HumanDecision;