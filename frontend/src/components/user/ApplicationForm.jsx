import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HiOutlineUser, HiOutlineBriefcase, HiOutlineCurrencyRupee, HiOutlineDocumentText, HiOutlineCheckCircle, HiOutlineArrowRight, HiOutlineArrowLeft } from 'react-icons/hi';
import DocumentUpload from './DocumentUpload';
import userService from '../../services/userService';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const STEPS = [
  { label: 'Personal', icon: <HiOutlineUser /> },
  { label: 'Employment', icon: <HiOutlineBriefcase /> },
  { label: 'Loan Details', icon: <HiOutlineCurrencyRupee /> },
  { label: 'Documents', icon: <HiOutlineDocumentText /> },
];

const ApplicationForm = () => {
  const [step, setStep] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: '', age: '', pan_number: '', phone: '', email: '',
    monthly_income: '', employment_type: 'salaried', employer_name: '', years_employed: '',
    loan_amount: '', loan_purpose: 'personal', existing_loans: '0', existing_emi: '0',
  });

  const [panFile, setPanFile] = useState(null);
  const [salaryFile, setSalaryFile] = useState(null);

  const update = (field, value) => setForm(prev => ({ ...prev, [field]: value }));

  const canNext = () => {
    if (step === 0) return form.full_name && form.age && form.pan_number && form.phone && form.email;
    if (step === 1) return form.monthly_income && form.employment_type;
    if (step === 2) return form.loan_amount && form.loan_purpose;
    if (step === 3) return panFile && salaryFile;
    return false;
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      fd.append('pan_document', panFile);
      fd.append('salary_document', salaryFile);

      const result = await userService.submitApplication(fd);
      toast.success('Application submitted successfully!');
      navigate('/user/applications');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      {/* Progress Steps */}
      <div className="progress-steps">
        {STEPS.map((s, i) => (
          <div key={i} className={`progress-step ${i < step ? 'completed' : ''} ${i === step ? 'active' : ''}`}>
            <div className="step-circle">
              {i < step ? <HiOutlineCheckCircle /> : s.icon}
            </div>
            <div className="step-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="glass-card" style={{ marginTop: '1.5rem' }}>
        <AnimatePresence mode="wait">
          <motion.div key={step} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.25 }}>

            {step === 0 && (
              <div>
                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', fontWeight: 700 }}>Personal Information</h2>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Full Name *</label>
                    <input className="form-input" placeholder="Rahul Kumar Sharma" value={form.full_name} onChange={e => update('full_name', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Age *</label>
                    <input className="form-input" type="number" min="21" max="65" placeholder="30" value={form.age} onChange={e => update('age', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">PAN Number *</label>
                    <input className="form-input" placeholder="ABCDE1234F" maxLength={10} value={form.pan_number} onChange={e => update('pan_number', e.target.value.toUpperCase())} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Phone *</label>
                    <input className="form-input" type="tel" placeholder="9876543210" maxLength={10} value={form.phone} onChange={e => update('phone', e.target.value)} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Email *</label>
                  <input className="form-input" type="email" placeholder="rahul@example.com" value={form.email} onChange={e => update('email', e.target.value)} />
                </div>
              </div>
            )}

            {step === 1 && (
              <div>
                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', fontWeight: 700 }}>Employment Details</h2>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Employment Type *</label>
                    <select className="form-select" value={form.employment_type} onChange={e => update('employment_type', e.target.value)}>
                      <option value="salaried">Salaried</option>
                      <option value="self_employed">Self Employed</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Monthly Income (₹) *</label>
                    <input className="form-input" type="number" placeholder="75000" value={form.monthly_income} onChange={e => update('monthly_income', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Employer Name</label>
                    <input className="form-input" placeholder="Tata Consultancy Services" value={form.employer_name} onChange={e => update('employer_name', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Years Employed</label>
                    <input className="form-input" type="number" step="0.5" placeholder="5" value={form.years_employed} onChange={e => update('years_employed', e.target.value)} />
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div>
                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', fontWeight: 700 }}>Loan Details</h2>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Loan Amount (₹) *</label>
                    <input className="form-input" type="number" placeholder="500000" value={form.loan_amount} onChange={e => update('loan_amount', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Loan Purpose *</label>
                    <select className="form-select" value={form.loan_purpose} onChange={e => update('loan_purpose', e.target.value)}>
                      <option value="home">Home Loan</option>
                      <option value="personal">Personal Loan</option>
                      <option value="business">Business Loan</option>
                      <option value="education">Education Loan</option>
                      <option value="vehicle">Vehicle Loan</option>
                      <option value="medical">Medical Loan</option>
                      <option value="marriage">Marriage Loan</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Existing Loans</label>
                    <input className="form-input" type="number" min="0" value={form.existing_loans} onChange={e => update('existing_loans', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Existing Monthly EMI (₹)</label>
                    <input className="form-input" type="number" min="0" placeholder="0" value={form.existing_emi} onChange={e => update('existing_emi', e.target.value)} />
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div>
                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', fontWeight: 700 }}>Upload Documents</h2>
                <div className="grid-2">
                  <DocumentUpload label="PAN Card Image" accept="image/*" file={panFile} onFileSelect={setPanFile} />
                  <DocumentUpload label="Salary Slip Image" accept="image/*" file={salaryFile} onFileSelect={setSalaryFile} />
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex-between" style={{ marginTop: '2rem' }}>
          <button className="btn btn-outline" onClick={() => setStep(s => s - 1)} disabled={step === 0}>
            <HiOutlineArrowLeft /> Back
          </button>

          {step < 3 ? (
            <button className="btn btn-primary" onClick={() => setStep(s => s + 1)} disabled={!canNext()}>
              Next <HiOutlineArrowRight />
            </button>
          ) : (
            <button className="btn btn-success btn-lg" onClick={handleSubmit} disabled={!canNext() || submitting}>
              {submitting ? <span className="spinner" style={{ width: 20, height: 20 }}></span> : <><HiOutlineCheckCircle /> Submit Application</>}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApplicationForm;