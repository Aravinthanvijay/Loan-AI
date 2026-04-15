import React from 'react';

const DocumentViewer = ({ application }) => {
  if (!application) return null;

  const panDoc = application.pan_document;
  const salaryDoc = application.salary_document;

  const getImageUrl = (doc) => {
    if (!doc?.file_path) return null;
    const path = doc.file_path.replace(/\\/g, '/');
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    const baseUrl = apiBase.replace('/api', '');
    return `${baseUrl}/uploads/${path.split('uploads/').pop() || path}`;
  };

  return (
    <div className="grid-2">
      <div className="glass-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>PAN Card</h3>
        {panDoc ? (
          <div>
            <div style={{ background: 'var(--bg-glass)', borderRadius: 8, padding: '1rem', textAlign: 'center', marginBottom: '1rem' }}>
              <img src={getImageUrl(panDoc)} alt="PAN Card" style={{ maxHeight: 200, borderRadius: 8, objectFit: 'contain' }} onError={(e) => { e.target.style.display = 'none'; }} />
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>{panDoc.filename}</div>
            </div>
          </div>
        ) : (
          <div className="empty-state" style={{ padding: '2rem' }}><p>No PAN document uploaded</p></div>
        )}
      </div>

      <div className="glass-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Salary Slip</h3>
        {salaryDoc ? (
          <div>
            <div style={{ background: 'var(--bg-glass)', borderRadius: 8, padding: '1rem', textAlign: 'center', marginBottom: '1rem' }}>
              <img src={getImageUrl(salaryDoc)} alt="Salary Slip" style={{ maxHeight: 200, borderRadius: 8, objectFit: 'contain' }} onError={(e) => { e.target.style.display = 'none'; }} />
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>{salaryDoc.filename}</div>
            </div>
          </div>
        ) : (
          <div className="empty-state" style={{ padding: '2rem' }}><p>No salary document uploaded</p></div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;