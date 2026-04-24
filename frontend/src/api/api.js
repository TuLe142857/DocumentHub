import axios from 'axios';
import { ERROR_CODE } from '../constants/errorCode.jsx';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

const debug_api_success = (res) => {
  console.group(
    `Debug API: ${res.config?.method?.toUpperCase()} ${res.config.url}`
  );
  console.log('Request config:', res.config);
  console.log('Response data:', res.data);
  console.groupEnd();
};

const debug_api_error = (err) => {
  console.group(
    `Debug API ERROR: ${err.config?.method?.toUpperCase()} ${err.config.url}`
  );
  console.log('Request:', err.config);
  console.log('Error response:', err.response?.data);
  console.log('Error message:', err.message);
  console.groupEnd();
};

api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      debug_api_success(response);
    }
    return response;
  },
  async (error) => {
    if (import.meta.env.DEV) {
      debug_api_error(error);
    }

    const originalRequest = error.config;
    const errorCode = error?.response?.data?.error_code;
    const isRefreshRequest = originalRequest.url.includes('/auth/refresh');

    const needRefresh =
      (errorCode === ERROR_CODE.JWT_TOKEN_EXPIRED ||
        errorCode === ERROR_CODE.UNAUTHORIZED) &&
      !isRefreshRequest &&
      !originalRequest._retry;
    if (needRefresh) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err));
      }
      originalRequest._retry = true;
      isRefreshing = true;
      try {
        console.log('Try refreshing token');
        await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          {},
          {
            withCredentials: true,
          }
        );
        processQueue(null);
        console.log('Refresh token ok');
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        console.log('refreshError:', refreshError?.response?.data);

        if (
          window.location.pathname !== '/login' &&
          !originalRequest.url.includes('/auth/whoami')
        ) {
          alert('please login and try again');
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
