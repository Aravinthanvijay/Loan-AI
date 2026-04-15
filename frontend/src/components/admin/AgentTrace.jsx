import React, { useState } from 'react';
import { HiOutlineChevronDown, HiOutlineChevronUp, HiOutlineCheckCircle, HiOutlineXCircle } from 'react-icons/hi';

const AGENT_META = {
  agent1_intake: { name: 'Agent 1: Intake Validation', desc: 'PAN validation, blacklist check, duplicate detection' },
  agent2_document: { name: 'Agent 2: Document Verification', desc: 'OCR extraction, cross-validation of documents' },
  agent3_credit: { name: 'Agent 3: Credit Scoring', desc: 'ML-based default prediction & SHAP analysis' },
  agent4_rules: { name: 'Agent 4: Rules Engine', desc: 'Business rule evaluation (age, income, FOIR)' },
  agent5_policy: { name: 'Agent 5: Policy Compliance', desc: 'RAG-based policy clause matching' },
  agent6_decision: { name: 'Agent 6: AI Decision', desc: 'LLM-powered final decision synthesis' },
};

const AgentTrace = ({ trace }) => {
  const [expanded, setExpanded] = useState({});

  if (!trace) return <div className="empty-state"><h3>No trace data available</h3></div>;

  const toggle = (key) => setExpanded(prev => ({ ...prev, [key]: !prev[key] }));

  const agents = Object.entries(AGENT_META);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {agents.map(([key, meta]) => {
        const result = trace[key];
        const hasResult = result && Object.keys(result).length > 0;
        const passed = result?.passed !== false && result?.status !== 'fail';
        const isExpanded = expanded[key];

        return (
          <div key={key} className="glass-card" style={{ padding: 0 }}>
            <div className="expandable-header" onClick={() => toggle(key)}>
              <div className="flex gap-2" style={{ alignItems: 'center' }}>
                {hasResult ? (
                  passed ? <HiOutlineCheckCircle style={{ color: 'var(--accent-emerald)', fontSize: '1.3rem' }} /> : <HiOutlineXCircle style={{ color: 'var(--accent-red)', fontSize: '1.3rem' }} />
                ) : (
                  <div style={{ width: 20, height: 20, borderRadius: '50%', background: 'var(--text-muted)', opacity: 0.3 }}></div>
                )}
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{meta.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{meta.desc}</div>
                </div>
              </div>
              <div className="flex gap-1" style={{ alignItems: 'center' }}>
                {hasResult && <span className={`badge ${passed ? 'badge-approved' : 'badge-rejected'}`}>{passed ? 'Pass' : 'Fail'}</span>}
                {isExpanded ? <HiOutlineChevronUp /> : <HiOutlineChevronDown />}
              </div>
            </div>
            {isExpanded && hasResult && (
              <div className="expandable-body">
                <pre style={{ background: 'var(--bg-glass)', padding: '1rem', borderRadius: 8, overflow: 'auto', fontSize: '0.8rem', color: 'var(--text-secondary)', maxHeight: 300 }}>
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default AgentTrace;