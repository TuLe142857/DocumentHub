import api from '@/api/api.js';

const collectionApi = {
  createCollection: (name) => api.post('/collections', { name: name }),
  renameCollection: (id, newName) =>
    api.patch(`/collections/${id}`, { new_name: newName }),
  deleteCollection: (id) => api.delete(`/collections/${id}`),
  getItems: (id, query) =>
    api.get(`/collections/${id}/items`, { params: query }),
  addItem: (id, docId) => api.put(`/collections/${id}/items/${docId}`),
  removeItem: (id, docId) => api.delete(`/collections/${id}/items/${docId}`),
};

export default collectionApi;
