import api from './api';

const userService = {
  async submitApplication(formData) {
    const response = await api.post('/user/apply', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async getMyApplications() {
    const response = await api.get('/user/applications');
    return response.data;
  },

  async getApplicationStatus(applicationId) {
    const response = await api.get(`/user/status/${applicationId}`);
    return response.data;
  },
};

export default userService;