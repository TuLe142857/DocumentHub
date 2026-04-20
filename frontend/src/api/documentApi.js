import api from '@/api/api.js';

const documentApi = {
  getSupportedTypes: () => api.get('/documents/supported_types'),
  getMaxSize: () => api.get('/documents/max_size'),

  upload: (formData) =>
    api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getDetails: (id) => api.get(`/documents/${id}`),
  update: (id, payload) => api.patch(`/documents/${id}`, payload),
  delete: (id) => api.delete(`/documents/${id}`),
  restore: (id) => api.post(`/documents/${id}/restore`),

  like: (id) => api.put(`/documents/${id}/like`),
  unlike: (id) => api.delete(`/documents/${id}/like`),

  addTag: (id, payload) => api.put(`/documents/${id}/tags`, payload),
  removeTag: (id, payload) =>
    api.delete(`/documents/${id}/tags`, { data: payload }),

  download: (id, format = '.pdf') =>
    api.get(`/documents/${id}/download`, { params: { format: format } }),

  /**
   *
   * @param {Number} id - Document id
   * @param {Array<Number>} collection_ids - List of collection id
   * @return {Promise<axios.AxiosResponse<any>>}
   */
  addToCollections: (id, collection_ids) =>
    api.put(`/documents/${id}/collections`, { collection_ids: collection_ids }),
};

export default documentApi;
