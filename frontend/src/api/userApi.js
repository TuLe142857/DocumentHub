import api from '@/api/api.js';

const userApi = {
  getMyProfile: () => api.get('/users/me/profile'),
  updateMyProfile: (payload) => api.patch('/users/me/profile', payload),
  updateMyAvatar: (formData) =>
    api.put('/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getMyDocuments: (params) =>
    api.get('/users/me/documents', { params: params }),
  getMyLikedDocuments: (params) =>
    api.get('/users/me/liked_documents', { params: params }),
  getMyCollections: (params) =>
    api.get('/users/me/collections', { params: params }),

  // Other users
  getUserProfile: (username) => api.get(`/users/${username}/profile`),
  getUserDocuments: (username, params) =>
    api.get(`/users/${username}/documents`, { params }),
};

export default userApi;
