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
  console.group(`Debug API: ${res.config?.method?.toUpperCase()} ${res.config.url}`);
  console.log("Request config:", res.config);
  console.log("Response data:", res.data);
  console.groupEnd();
}

const debug_api_error = (err) => {
  console.group(`Debug API ERROR: ${err.config?.method?.toUpperCase()} ${err.config.url}`);
  console.log("Request:", err.config);
  console.log("Error response:", err.response?.data);
  console.log("Error message:", err.message);
  console.groupEnd();
}

api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV){
      debug_api_success(response);
    }
    return response;
  },
  async (error) => {
    if (import.meta.env.DEV){
      debug_api_error(error);
    }

    const originalRequest = error.config;
    const data = error.response?.data;
    const isRefreshRequest = originalRequest.url.includes('/auth/refresh');

    if (
      data?.error_code === ERROR_CODE.JWT_TOKEN_EXPIRED &&
      !originalRequest._retry &&
      !isRefreshRequest
    ) {
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
        await axios.get(`${API_BASE_URL}/auth/refresh`, {
          withCredentials: true,
        });
        processQueue(null);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
