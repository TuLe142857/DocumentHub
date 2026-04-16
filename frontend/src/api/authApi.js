import api from '@/api/api.js';

const authApi = {

  /**
   * @typedef LoginPayload
   * @property {string} identity
   * @property {string} password
   */
  /**
   *
   * @param {LoginPayload} payload
   * @return {Promise<axios.AxiosResponse<any>>}
   */
  login: (payload) => api.post('/auth/login', payload),

  logout: () => api.post('/auth/logout'),

  whoami: () => api.get('/auth/whoami'),

  // Register flow
  requestRegister: (payload) => api.post('/auth/register/request', payload),
  verifyRegister: (payload) => api.post('/auth/register/verify', payload),
  completeRegister: (payload) => api.post('/auth/register/complete', payload),

  // Password flow
  forgotPassword: (payload) => api.post('/auth/forgot_password', payload),
  resetPassword: (payload) => api.post('/auth/reset_password', payload),
};

export default authApi;

