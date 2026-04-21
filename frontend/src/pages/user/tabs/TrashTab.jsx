import api from '@/api/api.js';
import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { ArchiveRestore } from 'lucide-react';
import usePagination from '@/hooks/usePagination.jsx';
import PageNavigation from '@/components/PageNavigation.jsx';
import DocumentCard from '@/components/DocumentCard.jsx';
import Loading from '@/components/Loading.jsx';
import ErrorPage from '@/pages/errors/ErrorPage.jsx';
const TrashTab = () => {
  const { user: currentUser } = useSelector((state) => state.user);
  const [docs, setDocs] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination(1, 5);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await api.get(`users/me/documents`, {
          params: { statuses: 'DELETED' },
        });
        const meta = res.data?.meta;
        updatePagination({
          currentPage: meta.current_page,
          limit: meta.per_page,
          totalPages: meta.total_pages,
          totalItems: meta.total_items,
          hasNextPage: meta.has_next,
          hasPreviousPage: meta.has_prev,
        });
        setDocs(res.data?.data);
      } catch (err) {
        const msg = err?.response?.data?.message || 'Something went wrong.';
        setError(msg);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [pagination.currentPage, pagination.limit, currentUser, updatePagination]);

  const handleRestore = async (doc) => {
    if (!confirm('Are you sure?')) {
      return;
    }
    try {
      await api.post(`/documents/${doc.id}/restore`);
      setDocs((prev) => prev.filter((d) => d.id !== doc.id));
      alert('Restored');
    } catch (err) {
      alert(err.response.data.message);
    }
  };
  if (loading) return <Loading />;
  if (error) return <ErrorPage msg={error} />;
  return (
    <div className="flex flex-col p-2 gap-2">
      <div>Items in trash will be deleted after 30 days</div>
      {docs &&
        docs?.map((doc) => (
          <div>
            <div
              key={doc.id}
              className="group relative flex flex-row flex-1 items-center"
            >
              <DocumentCard
                document={doc}
                orientation="horizontal"
                className="group-hover:bg-sky-100"
              />
              <button
                className="absolute right-5 top-5 p-2 text-gray-400 hover:text-green-500 hover:rounded-xl hover:bg-green-200/50"
                onClick={() => handleRestore(doc)}
              >
                <ArchiveRestore />
              </button>
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

export default TrashTab;
