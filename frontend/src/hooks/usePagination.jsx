import { useState, useCallback } from 'react';

/**
 *
 * @param defaultPage
 * @param defaultLimit
 * @returns {{pagination: {currentPage: number, limit: number, totalPages: number, totalItems: number, hasNextPage: boolean, hasPreviousPage: boolean}, setPagination: (value: (((prevState: {currentPage: number, limit: number, totalPages: number, totalItems: number, hasNextPage: boolean, hasPreviousPage: boolean}) => {currentPage: number, limit: number, totalPages: number, totalItems: number, hasNextPage: boolean, hasPreviousPage: boolean}) | {currentPage: number, limit: number, totalPages: number, totalItems: number, hasNextPage: boolean, hasPreviousPage: boolean})) => void, updatePagination: (function(*): void)|*, setLimit: (function(*): void)|*, setPage: (function(*): void)|*}}
 */
const usePagination = (defaultPage = 1, defaultLimit = 10) => {
  const [pagination, setPagination] = useState({
    currentPage: defaultPage,
    limit: defaultLimit,
    totalPages: 0,
    totalItems: 0,
    hasNextPage: false,
    hasPreviousPage: false,
  });

  const updatePagination = useCallback((meta) => {
    setPagination((prev) => ({ ...prev, ...meta }));
  }, []);

  const setLimit = useCallback((newLimit) => {
    setPagination((prev) => ({
      ...prev,
      limit: newLimit,
    }));
  }, []);

  const setPage = useCallback((newPage) => {
    setPagination((prev) => ({ ...prev, currentPage: newPage }));
  }, []);

  return {
    pagination,
    setPagination,
    updatePagination,
    setLimit,
    setPage,
  };
};

export default usePagination;
