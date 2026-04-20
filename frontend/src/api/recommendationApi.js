import api from '@/api/api.js';

const recommendationApi = {
  getForMe: () => api.get('/recommendation/for_me'),
  getTrending: (params) => api.get('/recommendation/trending', { params }),
  getSimilar: (id, limit = 10) =>
    api.get(`/recommendation/similar/${id}`, { params: { limit } }),
};
export default recommendationApi;
