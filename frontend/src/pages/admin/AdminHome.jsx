import React from 'react';
import Navbar from '../../components/shared/Navbar';
import Dashboard from '../../components/admin/Dashboard';

const AdminHome = () => {
  return (
    <>
      <Navbar isAdmin />
      <div className="page-container">
        <div className="page-header">
          <h1>Admin Dashboard</h1>
          <p>Overview of loan application processing</p>
        </div>
        <Dashboard />
      </div>
    </>
  );
};

export default AdminHome;