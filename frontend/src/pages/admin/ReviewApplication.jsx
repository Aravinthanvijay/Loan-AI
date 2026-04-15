import React, { useState } from 'react';
import Navbar from '../../components/shared/Navbar';
import ApplicationList from '../../components/admin/ApplicationList';
import ApplicationDetail from '../../components/admin/ApplicationDetail';

const ReviewApplication = () => {
  const [selectedId, setSelectedId] = useState(null);

  return (
    <>
      <Navbar isAdmin />
      <div className="page-container">
        {selectedId ? (
          <ApplicationDetail applicationId={selectedId} onBack={() => setSelectedId(null)} />
        ) : (
          <>
            <div className="page-header">
              <h1>Review Applications</h1>
              <p>Browse, review, and make decisions on loan applications</p>
            </div>
            <ApplicationList onSelect={setSelectedId} />
          </>
        )}
      </div>
    </>
  );
};

export default ReviewApplication;