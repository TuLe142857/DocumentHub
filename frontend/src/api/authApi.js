import api from '@/api/api.js';

const authApi = {
  login: (payload) => api.post('/auth/login', payload),

  logout: () => api.post('/auth/logout'),

  whoami: () => api.get('/auth/whoami'),

  // Register flow
  requestRegister: (payload) => api.post('/auth/register/request', payload),
  verifyRegister: (payload) => api.post('/auth/register/verify', payload),
  completeRegister: (payload) => api.post('/auth/register/complete', payload),

  // ForgotPassword flow
  forgotPassword: (payload) => api.post('/auth/forgot_password', payload),
  resetPassword: (payload) => api.post('/auth/reset_password', payload),
};

export default authApi;
