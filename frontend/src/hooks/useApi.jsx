import api from '@/api/api.js';
import { useEffect, useState, useCallback } from 'react';

/**
 * @typedef {Object} AxiosConfig
 * @property {"GET" | "POST" | "PUT" | "DELETE" | "PATCH"} method
 * @property {Object.<String, Any>} params
 * @property {any} data
 * @property {Object.<string, string>} headers
 * @property {number} timeout
 */

/**
 *
 * @param {String} url
 * @param {AxiosConfig} options
 * @returns {{data: unknown, pagination: unknown, loading: boolean, error: unknown, refetch: (function(): Promise<void>)|*}}
 */
export default function useApi(url, options) {
  const [data, setData] = useState(null);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api({ url: url, ...options });
      setData(response.data?.data || null);
      setPagination(response.data?.meta || null);
    } catch (e) {
      setError(e?.response?.data?.error_code || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);
  return { data, pagination, loading, error, refetch: fetchData };
}
