import {
  X as ExitIcon,
  Bookmark as CollectionIcon,
  Loader2,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

import userApi from '@/api/userApi.js';
import documentApi from '@/api/documentApi.js';

/**
 * @import {Document} from '@/type/document.jsx'
 */

/**
 * @param {Object} props
 * @param {Document} props.doc
 */
const AddDocumentToCollectionForm = ({
  doc,
  onExit,
  onSuccess,
  className = 'w-full max-w-md rounded-xl bg-white border border-gray-200 shadow-xl p-4',
}) => {

  const [collections, setCollections] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);


  const [checkedCollectionIds, setCheckedCollectionIds] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  const [isInitializing, setIsInitializing] = useState(true);
  const [isLoadingList, setIsLoadingList] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 500);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  useEffect(() => {
    setPage(1);
  }, [debouncedQuery]);


  useEffect(() => {
    const fetchInitialChecked = async () => {
      try {
        const res = await userApi.getMyCollections({
          document_id: doc.id,
          limit: 100, // trick lỏ here :)
        });

        const initialCheckedIds = res.data.data.map(
          (collection) => collection.id
        );
        setCheckedCollectionIds(initialCheckedIds);
      } catch (err) {
        toast.error(err?.response?.data.message || err?.message || "Something went wrong!");
      } finally {
        setIsInitializing(false);
      }
    };

    if (doc?.id) {
      fetchInitialChecked();
    }
  }, [doc?.id]);


  useEffect(() => {
    if (isInitializing) return;

    const fetchCollections = async () => {
      setIsLoadingList(true);
      try {
        const res = await userApi.getMyCollections({
          page: page,
          limit: 10,
          q: debouncedQuery,
        });

        const { data, meta } = res.data;

        setCollections((prev) => (page === 1 ? data : [...prev, ...data]));
        setHasNext(meta.has_next);
      } catch (err) {
        const msg = err?.response?.data?.message || 'Something went wrong!';
        toast.error(msg);
      } finally {
        setIsLoadingList(false);
      }
    };

    fetchCollections();
  }, [page, debouncedQuery, isInitializing]);


  const handleToggleCheck = (collectionId) => {
    setCheckedCollectionIds(
      (prev) =>
        prev.includes(collectionId)
          ? prev.filter((id) => id !== collectionId)
          : [...prev, collectionId]
    );
  };


  const handleSave = async () => {
    setIsSaving(true);
    try {
      await documentApi.addToCollections(doc.id, checkedCollectionIds);

      toast.success('Success !');
      onSuccess && onSuccess();
      onExit && onExit();
    } catch (error) {
      toast.error(
        error?.response?.data?.message ||
          error.message ||
          'Something went wrong!'
      );
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className={`relative flex flex-col ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-200">
        <div className="flex items-center gap-2 font-semibold text-gray-800">
          <CollectionIcon className="w-5 h-5 text-blue-600" />
          <span>Add to Collection</span>
        </div>
        <button
          className="rounded-full p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          onClick={onExit}
          disabled={isSaving}
        >
          <ExitIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Search Input */}
      <div className="mt-4 mb-2">
        <input
          type="text"
          placeholder="Tìm kiếm bộ sưu tập..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/*  Collections (Checkboxes) */}
      <div className="flex-1 overflow-y-auto max-h-64 my-2 px-1">
        {isInitializing ? (
          <div className="flex justify-center py-4">
            <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          </div>
        ) : collections.length === 0 ? (
          <p className="text-center text-sm text-gray-500 py-4">
            No Collection found.
          </p>
        ) : (
          <div className="flex flex-col gap-2">
            {collections.map((collection) => (
              <label
                key={collection.id}
                className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                  checked={checkedCollectionIds.includes(collection.id)}
                  onChange={() => handleToggleCheck(collection.id)}
                />
                <span className="text-sm font-medium text-gray-700 truncate select-none">
                  {collection.name}
                </span>
              </label>
            ))}
          </div>
        )}

        {/* Load More Button */}
        {hasNext && (
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={isLoadingList}
            className="w-full mt-2 py-2 text-sm text-blue-600 font-medium hover:text-blue-800 disabled:opacity-50"
          >
            {isLoadingList ? 'Đang tải...' : 'Xem thêm'}
          </button>
        )}
      </div>

      {/* Footer Actions */}
      <div className="pt-3 border-t border-gray-200 flex justify-end gap-2 mt-auto">
        <button
          onClick={onExit}
          disabled={isSaving}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          disabled={isSaving || isInitializing}
          className="flex items-center justify-center min-w-[100px] px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-70"
        >
          {isSaving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            'Lưu thay đổi'
          )}
        </button>
      </div>
    </div>
  );
};

export default AddDocumentToCollectionForm;
