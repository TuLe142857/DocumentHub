import adminApi from '@/api/adminApi.js';
import { useState, useEffect, useCallback } from 'react';
import PageNavigation from '@/components/PageNavigation.jsx';
import usePagination from '@/hooks/usePagination.jsx';
import { toast } from 'react-toastify';
const AdminDocumentManagement = () => {
  const [search, setSearch] = useState('');
  const [searchDebounced, setSearchDebounced] = useState('');
  const [status, setStatus] = useState('BANNED');

  const { pagination, updatePagination, setPage } = usePagination();

  const [docs, setDocs] = useState([]);

  const fetchDocs = useCallback(async () => {
    try {
      const params = {
        q: searchDebounced,
        page: pagination.currentPage,
        limit: pagination.limit,
      };
      if (status) {
        params['status'] = status;
      }
      console.log('params', params);
      const response = await adminApi.getDocuments(params);

      const meta = response.data?.meta;
      updatePagination({
        currentPage: meta.current_page,
        limit: meta.per_page,
        totalPages: meta.total_pages,
        totalItems: meta.total_items,
        hasNextPage: meta.has_next,
        hasPreviousPage: meta.has_prev,
      });
      setDocs(response?.data?.data);
    } catch (err) {
      console.log(err);
    }
  }, [
    pagination.currentPage,
    pagination.limit,
    searchDebounced,
    status,
    updatePagination,
  ]);

  useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setSearchDebounced(search);
      setPage(1);
    }, 500);
    return () => {
      clearTimeout(timeout);
    };
  }, [search, setPage]);

  const handeUnbanDocument = async (id) => {
    if (!confirm('Confirm unban this document?')) {
      return;
    }
    const toastId = toast.loading('waiting...');
    try {
      await adminApi.unbanDocument(id);
      toast.update(toastId, {
        type: 'success',
        render: 'Success',
        isLoading: false,
        autoClose: 500,
      });
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        'Something went wrong, please try again later';
      toast.update(toastId, {
        type: 'error',
        render: msg,
        isLoading: false,
        autoClose: 500,
      });
    }
  };

  return (
    <div className="flex flex-col p-2 gap-2">
      <div className={'text-2xl text-black font-bold'}>Document management</div>

      <div
        className={
          'flex flex-row p-2 my-4 items-center gap-2 rounded-lg bg-white shadow border border-gray-300'
        }
      >
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="search document"
          className={`
          flex-1 p-2 rounded-sm border border-gray-200
          text-lg font-normal
          bg-gray-100 focus:outline-blue-500 max-w-100 `}
        />

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className={`
          p-2 rounded-sm border border-gray-200
          text-lg font-normal
          bg-gray-100 focus:outline-blue-500 `}
        >
          <option value={''}>All status</option>
          <option value={'BANNED'}>Banned</option>
        </select>
      </div>

      <table className="text-md text-gray-700 bg-white rounded-md overflow-hidden shadow border border-gray-300">
        <colgroup>
          {/*<col className="w-1/4"/>*/}
          {/*<col className="w-1/4"/>*/}
          {/*<col className="w-1/4"/>*/}
          {/*<col className="w-1/4"/>*/}
        </colgroup>

        <thead>
          <tr className={`text-left text-black font-bold bg-gray-300/50 `}>
            <th className="px-3 py-2 border-r border-gray-300">Title</th>
            <th className="px-3 py-2 border-r border-gray-300">Owner</th>
            <th className="px-3 py-2 border-r border-gray-300">Status</th>
            <th className="px-3 py-2 border-r border-gray-300">Visibility</th>
            <th className="px-3 py-2">Action</th>
          </tr>
        </thead>

        <tbody>
          {docs &&
            docs.map((doc) => (
              <tr
                key={doc.id}
                className="hover:bg-sky-50/50 border-t border-gray-200"
              >
                <td className="px-3 py-2 truncate border-r border-gray-300">
                  {doc.title}
                </td>
                <td className="px-3 py-2 truncate border-r border-gray-300">
                  {doc.owner}
                </td>
                <td className="px-3 py-2 truncate border-r border-gray-300">
                  {doc.status}
                </td>
                <td className="px-3 py-2 truncate border-r border-gray-300">
                  {doc.visibility}
                </td>
                <td className="px-3 py-2 truncate">
                  {doc.status === 'BANNED' && (
                    <button
                      className="p-2 rounded-sm bg-green-100/50 text-green-500 hover:bg-green-200/50"
                      onClick={() => handeUnbanDocument(doc.id)}
                    >
                      Unban
                    </button>
                  )}
                </td>
              </tr>
            ))}
        </tbody>
      </table>

      <PageNavigation
        page={pagination.currentPage}
        totalPage={pagination.totalPages}
        onPageChange={setPage}
      />

      <div>DEBUG DATA</div>
      <pre>{JSON.stringify(docs, null, 2)}</pre>
    </div>
  );
};

export default AdminDocumentManagement;
