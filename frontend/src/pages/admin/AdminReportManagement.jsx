import { useState, useEffect, useCallback } from 'react';
import adminApi from '@/api/adminApi.js';

import usePagination from '@/hooks/usePagination.jsx';
import PageNavigation from '@/components/PageNavigation.jsx';
import ReportDetails from '@/pages/admin/modals/ReportDetails.jsx';
import useModal from '@/modal/useModal.jsx';

const AdminReportManagement = () => {
  const [docs, setDocs] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination();
  const { openModal, closeModal } = useModal();

  const fetchReportedDocuments = useCallback(async () => {
    try {
      const response = await adminApi.getReportedDocuments({
        page: pagination.currentPage,
        limit: pagination.limit,
      });

      const meta = response.data.meta;
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
  }, [pagination.currentPage, pagination.limit, updatePagination]);

  useEffect(() => {
    fetchReportedDocuments();
  }, [fetchReportedDocuments]);

  const handleReport = (docId) => {
    openModal(
      <ReportDetails
        docId={docId}
        onExit={closeModal}
        classname="h-[80vh] w-[75vw] bg-white rounded-xl overflow-hidden"
      />
    );
  };

  return (
    <div className="flex flex-col p-2 gap-2">
      <div className="text-black text-2xl font-bold">Report Management</div>

      <div className="text-black text-lg font-bold">
        List of pending report documents
      </div>

      <table className="text-md text-gray-700 bg-white rounded-md overflow-hidden shadow-sm border border-gray-200">
        <colgroup>
          <col className="w-1/4" />
          <col className="w-1/4" />
          <col className="w-1/4" />
          <col className="w-1/4" />
        </colgroup>

        <thead>
          <tr className="text-left text-black font-bold bg-gray-200">
            <th className="py-2 px-3">Title</th>
            <th className="py-2 px-3">Owner</th>
            <th className="py-2 px-3">Report count</th>
            <th className="py-2 px-3">Action</th>
          </tr>
        </thead>

        <tbody>
          {docs &&
            docs.map((doc) => (
              <tr className="text-left border-t border-gray-200">
                <td className="py-2 px-3 truncate">{doc.title}</td>
                <td className="py-2 px-3 truncate">{doc.owner}</td>
                <td className="py-2 px-3 truncate">{doc.report_count}</td>
                <td className="py-2 px-3 truncate">
                  <button
                    className="bg-green-100/50 text-green-500 p-2 py-1 rounded-md hover:bg-green-200/50"
                    onClick={() => handleReport(doc.id)}
                  >
                    view details
                  </button>
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

    </div>
  );
};

export default AdminReportManagement;
