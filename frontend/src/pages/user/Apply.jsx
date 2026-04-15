import React from 'react';
import Navbar from '../../components/shared/Navbar';
import ApplicationForm from '../../components/user/ApplicationForm';

const Apply = () => {
  return (
    <>
      <Navbar />
      <div className="page-container">
        <div className="page-header">
          <h1>Apply for a Loan</h1>
          <p>Complete the form below to submit your loan application</p>
        </div>
        <ApplicationForm />
      </div>
    </>
  );
};

export default Apply;