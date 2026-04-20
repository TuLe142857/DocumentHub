import api from '@/api/api.js';

const searchApi = {
  search: (params) => api.get('/search', { params: params }),
};
export default searchApi;
