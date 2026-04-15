import api from './api';

const adminService = {
  async getAllApplications(page = 1, status = null) {
    const params = { page, per_page: 20 };
    if (status) params.status = status;
    const response = await api.get('/admin/applications', { params });
    return response.data;
  },

  async getApplicationDetail(applicationId) {
    const response = await api.get(`/admin/applications/${applicationId}`);
    return response.data;
  },

  async getAgentTrace(applicationId) {
    const response = await api.get(`/admin/trace/${applicationId}`);
    return response.data;
  },

  async makeDecision(applicationId, decision, notes = '') {
    const response = await api.post(`/admin/applications/${applicationId}/decide`, {
      decision,
      notes,
    });
    return response.data;
  },

  async getDashboardStats() {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  async addToBlacklist(panNumber, reason, name = '') {
    const response = await api.post('/admin/blacklist', {
      pan_number: panNumber,
      reason,
      name,
    });
    return response.data;
  },
};

export default adminService;