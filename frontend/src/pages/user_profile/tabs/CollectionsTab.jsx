import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';

import api from '@/api/api.js';
import PageNavigation from '@/components/PageNavigation.jsx';
import usePagination from '@/hooks/usePagination.jsx';
const CollectionsTab = ({ username }) => {
  const { id: collection_id } = useParams();
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );

  const [collections, setCollections] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.get(`/collections`);
        setCollections(response.data?.data);
        const meta = response.data.meta;
        updatePagination({
          currentPage: meta.current_page,
          limit: meta.per_page,
          totalPages: meta.total_pages,
          totalItems: meta.total_items,
          hasNextPage: meta.has_next,
          hasPreviousPage: meta.has_prev,
        });
      } catch (err) {
        setError(
          err.resonse.data?.message || 'Something went wrong, please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentUser, collection_id, pagination.currentPage, pagination.limit]);

  return (
    <div className="flex flex-col">
      <button>Create Collections</button>
      <pre>{JSON.stringify(collections, null, 2)}</pre>
      <pre>{JSON.stringify(pagination, null, 2)}</pre>

      <div className="mt-auto">
        <PageNavigation
          page={pagination.currentPage}
          totalPage={pagination.totalPages}
          onPageChange={setPage}
        />
      </div>
    </div>
  );
};

export default CollectionsTab;
