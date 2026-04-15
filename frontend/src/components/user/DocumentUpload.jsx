import React, { useRef, useState } from 'react';
import { HiOutlineCloudUpload, HiOutlineX, HiOutlinePhotograph } from 'react-icons/hi';

const DocumentUpload = ({ label, accept = 'image/*', file, onFileSelect }) => {
  const inputRef = useRef(null);
  const [dragover, setDragover] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragover(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) onFileSelect(droppedFile);
  };

  const handleChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) onFileSelect(selectedFile);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div>
      <label className="form-label">{label} *</label>
      <input ref={inputRef} type="file" accept={accept} onChange={handleChange} style={{ display: 'none' }} />

      {!file ? (
        <div
          className={`upload-zone ${dragover ? 'dragover' : ''}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
          onDragLeave={() => setDragover(false)}
          onDrop={handleDrop}
        >
          <div className="upload-icon"><HiOutlineCloudUpload /></div>
          <div className="upload-text">Click to upload or drag & drop</div>
          <div className="upload-hint">JPG, PNG or PDF up to 10MB</div>
        </div>
      ) : (
        <div className="upload-preview">
          <div style={{ width: 60, height: 60, borderRadius: 8, background: 'var(--bg-glass)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {file.type?.startsWith('image/') ? (
              <img src={URL.createObjectURL(file)} alt="preview" style={{ width: 60, height: 60, objectFit: 'cover', borderRadius: 8 }} />
            ) : (
              <HiOutlinePhotograph style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }} />
            )}
          </div>
          <div className="file-info">
            <div className="file-name">{file.name}</div>
            <div className="file-size">{formatSize(file.size)}</div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => onFileSelect(null)} style={{ color: 'var(--accent-red-light)' }}>
            <HiOutlineX />
          </button>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;