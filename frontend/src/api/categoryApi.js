import api from '@/api/api.js';

const categoryApi = {
  getCategories: () => api.get('/categories'),
};
export default categoryApi;
