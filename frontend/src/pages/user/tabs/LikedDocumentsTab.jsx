import { useState, useCallback, useEffect } from 'react';
import PageNavigation from '@/components/PageNavigation.jsx';
import usePagination from '@/hooks/usePagination.jsx';
import DocumentCard from '@/components/DocumentCard.jsx';

import userApi from '@/api/userApi.js';
const LikedDocumentsTab = () => {
  const [docs, setDocs] = useState(null);
  const { pagination, updatePagination, setPage } = usePagination();

  const fetchLikedDocuments = useCallback(async () => {
    try {
      const response = await userApi.getMyLikedDocuments({
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
      setDocs(response.data.data);
      console.log('response', response);
    } catch (e) {
      console.log(e);
    }
  }, [pagination.currentPage, pagination.limit, updatePagination]);

  useEffect(() => {
    console.log('docs', docs);
  }, [docs]);

  useEffect(() => {
    fetchLikedDocuments();
  }, [fetchLikedDocuments]);
  return (
    <div className="flex flex-col">
      {docs &&
        docs.length &&
        docs?.map((doc) => (
          <DocumentCard document={doc} orientation={'horizontal'} />
          // <div>{JSON.stringify(doc, null, 2)}</div>
        ))}
      <PageNavigation
        page={pagination.currentPage}
        totalPage={pagination.totalPages}
        onPageChange={setPage}
      />
    </div>
  );
};

export default LikedDocumentsTab;
