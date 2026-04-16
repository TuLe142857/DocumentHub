import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { EllipsisVertical, Trash2 } from 'lucide-react';

import usePagination from '@/hooks/usePagination.jsx';

import api from '@/api/api.js';

import DocumentCard from '@/components/DocumentCard.jsx';
import PageNavigation from '@/components/PageNavigation.jsx';
import Loading from '@/components/Loading.jsx';
import ErrorPage from '@/pages/errors/ErrorPage.jsx';

const DocumentsTab = ({ username }) => {
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );

  const [docs, setDocs] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination(1, 4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const url =
          isAuthenticated && currentUser && currentUser?.username === username
            ? `/users/me/documents`
            : `/users/${username}/documents`;
        const query = {
          limit: pagination.limit,
          page: pagination.currentPage,
        };
        const response = await api.get(url, { params: query });
        setDocs(response.data?.data);
        const meta = response.data?.meta;
        updatePagination({
          currentPage: meta.current_page,
          limit: meta.per_page,
          totalPages: meta.total_pages,
          totalItems: meta.total_items,
          hasNextPage: meta.has_next,
          hasPreviousPage: meta.has_prev,
        });
      } catch (err) {
        setError(err.response.data?.message || 'Something went wrong');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [
    currentUser,
    isAuthenticated,
    pagination.currentPage,
    pagination.limit,
    updatePagination,
    username,
  ]);

  const handleDelete = async (doc) => {
    if (!confirm(`Are you sure you want to delete this document?`)) {
      return;
    }
    try {
      await api.delete(`/documents/${doc.id}`);
      setDocs((pre) => pre.filter((d) => d.id !== doc.id));
      alert('ok');
    } catch (err) {
      const msg =
        err.response.data?.message || 'Something went wrong, please try again.';
      alert(`Error deleting document: ${msg}`);
    }
  };

  if (loading) {
    return <Loading />;
  }
  if (error) {
    return <ErrorPage message={error} />;
  }
  return (
    <div className="flex flex-col p-2 m-2 gap-2">
      {docs &&
        docs.map((doc) => (
          <div>
            <div className="group relative flex flex-row flex-1 items-center">
              <DocumentCard
                orientation={'horizontal'}
                document={doc}
                key={doc.id}
                className="group-hover:bg-sky-100 bg-white border border-gray-200 mx-2"
              />
              {isAuthenticated &&
                currentUser &&
                currentUser.username === username && (
                  <button
                    className="absolute right-5 top-5 p-2 text-gray-400 hover:text-red-500 hover:rounded-xl hover:bg-red-200/50"
                    onClick={() => handleDelete(doc)}
                  >
                    <Trash2 size={32} />
                  </button>
                )}
            </div>
            <hr className="text-gray-400 my-2" />
          </div>
        ))}
      <PageNavigation
        page={pagination.currentPage}
        totalPage={pagination.totalPages}
        onPageChange={setPage}
      />
    </div>
  );
};

export default DocumentsTab;
