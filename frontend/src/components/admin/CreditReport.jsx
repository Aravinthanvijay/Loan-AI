import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const CreditReport = ({ agent3 }) => {
  if (!agent3) return <div className="empty-state"><h3>Credit report not available</h3><p style={{ color: 'var(--text-muted)' }}>Agent 3 has not completed processing</p></div>;

  const score = agent3.credit_score || 0;
  const prob = agent3.default_probability || 0;
  const risk = agent3.risk_band || 'unknown';
  const factors = agent3.top_factors || [];

  const gaugeClass = score >= 750 ? 'high' : score >= 650 ? 'medium' : 'low';

  const shapData = factors.map(f => ({
    name: (f.factor || f.feature || '').replace(/_/g, ' '),
    value: Math.abs(f.shap_value || 0),
    direction: (f.shap_value || 0) > 0 ? 'risk' : 'safe',
  }));

  return (
    <div>
      <div className="grid-3 mb-3">
        {/* Credit Score Gauge */}
        <div className="glass-card">
          <div className={`credit-gauge ${gaugeClass}`}>
            <div className="gauge-value">{score}</div>
            <div className="gauge-label">Credit Score</div>
            <div style={{ marginTop: '0.75rem' }}>
              <div className="confidence-bar">
                <div className={`confidence-fill ${gaugeClass}`} style={{ width: `${((score - 300) / 600) * 100}%` }}></div>
              </div>
              <div className="flex-between mt-1" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <span>300</span><span>600</span><span>900</span>
              </div>
            </div>
          </div>
        </div>

        {/* Default Probability */}
        <div className="glass-card text-center">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Default Probability</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 900, color: prob > 0.5 ? 'var(--accent-red-light)' : prob > 0.3 ? 'var(--accent-amber-light)' : 'var(--accent-emerald-light)' }}>
            {(prob * 100).toFixed(1)}%
          </div>
          <div className="confidence-bar" style={{ marginTop: '0.75rem' }}>
            <div className={`confidence-fill ${prob > 0.5 ? 'low' : prob > 0.3 ? 'medium' : 'high'}`} style={{ width: `${prob * 100}%` }}></div>
          </div>
        </div>

        {/* Risk Band */}
        <div className="glass-card text-center">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Risk Band</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, textTransform: 'uppercase' }}>
            <span className={`badge badge-${risk === 'low' ? 'approved' : risk === 'medium' ? 'pending' : 'rejected'}`} style={{ fontSize: '1.2rem', padding: '0.5rem 1.5rem' }}>
              {risk}
            </span>
          </div>
        </div>
      </div>

      {/* SHAP Factors Chart */}
      {shapData.length > 0 && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Top Risk Factors (SHAP Analysis)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 20, left: 100, bottom: 0 }}>
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 12 }} width={100} />
              <Tooltip
                contentStyle={{ background: '#1a2035', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#f1f5f9' }}
                formatter={(value, name, props) => [`${value.toFixed(4)}`, props.payload.direction === 'risk' ? '↑ Increases Risk' : '↓ Decreases Risk']}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {shapData.map((d, i) => (
                  <Cell key={i} fill={d.direction === 'risk' ? '#ef4444' : '#10b981'} opacity={0.8} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-2 mt-1" style={{ fontSize: '0.75rem' }}>
            <span style={{ color: '#ef4444' }}>■ Increases risk</span>
            <span style={{ color: '#10b981' }}>■ Decreases risk</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreditReport;