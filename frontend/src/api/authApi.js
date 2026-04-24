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
  forgotPassword: (identity) =>
    api.post('/auth/forgot_password', { identity: identity }),
  resetPassword: (identity, otp_code, new_password) =>
    api.post('/auth/reset_password', {
      identity: identity,
      otp_code: otp_code,
      new_password: new_password,
    }),
};

export default authApi;
