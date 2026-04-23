import api from '@/api/api.js';

const adminApi = {
  getUser: (params) => api.get('/admin/users', { params: params }),
  banUser: (userId, reason) =>
    api.post(`/admin/users/${userId}/ban`, { reason: reason }),
  unbanUser: (userId) => api.post(`/admin/users/${userId}/unban`),

  createCategory: (name) => api.post(`/admin/categories`, { name: name }),
  renameCategory: (categoryId, newName) =>
    api.patch(`/admin/categories/${categoryId}`, { new_name: newName }),
  deleteCategory: (id) => api.delete(`/admin/categories/${id}`),

  getReportedDocuments: (params) =>
    api.get('/admin/reports', { params: params }),
  getReportedDocumentDetails: (documentId, params) =>
    api.get(`/admin/reports/documents/${documentId}`, { params: params }),
  handleReportedDocument: (documentId, accept, note) =>
    api.post(`/admin/reports/documents/${documentId}`, {
      note: note,
      accept: accept,
    }),

  getDocuments: (params) => api.get('/admin/documents', { params: params }),
  getDocumentDetails: (documentId) => api.get(`/admin/documents/${documentId}`),
  unbanDocument: (documentId) =>
    api.post(`/admin/documents/${documentId}/unban`),
};
export default adminApi;
