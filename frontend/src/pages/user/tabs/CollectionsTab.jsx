import { useState, useEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import {
  Pen,
  Trash2,
  FolderPlus as AddCollectionIcon,
  ArrowLeft as GoBackIcon,
  Folder as CollectionIcon,
  PencilIcon,
} from 'lucide-react';

import api from '@/api/api.js';
import collectionApi from '@/api/collectionApi.js';
import PageNavigation from '@/components/PageNavigation.jsx';
import usePagination from '@/hooks/usePagination.jsx';
import CollectionCard from '@/components/CollectionCard.jsx';

import Modal from '@/modal/Modal.jsx';
import CollectionCreateForm from '@/components/forms/CollectionCreateForm.jsx';
import DocumentCard from '@/components/DocumentCard.jsx';

const CollectionListTab = ({
  collections,
  onDeleteCollection,
  onSelectCollection,
}) => {
  return (
    <div>
      {collections && (
        <div className="flex flex-row flex-wrap justify-start p-2 gap-2">
          {collections.map((collection) => (
            <div
              className="relative group flex flex-row items-center w-60 rounded-xl bg-white p-2 shadown border border-slate-200 hover:border-sky-500"
              onClick={() => onSelectCollection(collection)}
            >
              <CollectionCard collection={collection} className="w-50 h-15" />
              <button
                className="absolute top-1 right-1 hidden group-hover:block rounded-sm p-1 m-2 text-gray-400 hover:text-red-500 hover:bg-red-200/50"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteCollection(collection);
                }}
              >
                <Trash2 />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const CollectionDetails = ({ collection }) => {
  const [docs, setDocs] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination();
  const fetchDocument = useCallback(async () => {
    try {
      const query = {
        page: pagination.currentPage,
        limit: pagination.limit,
      };
      const response = await collectionApi.getItems(collection.id, query);
      console.log('res', response.data);
      const data = response.data.data;
      const meta = response.data.meta;
      updatePagination({
        currentPage: meta.current_page,
        limit: meta.per_page,
        totalPages: meta.total_pages,
        totalItems: meta.total_items,
        hasNextPage: meta.has_next,
        hasPreviousPage: meta.has_prev,
      });
      setDocs(data);
      console.log(data);
    } catch (err) {
      console.log(err);
    }
  }, [
    collection.id,
    pagination.currentPage,
    pagination.limit,
    updatePagination,
  ]);

  useEffect(() => {
    fetchDocument();
  }, [fetchDocument]);

  const handleDelete = async (id) => {
    if (!confirm('are you sure?')) return;
    await collectionApi.removeItem(collection.id, id);
    setDocs((prev) => prev.filter((d) => d.id !== id));
  };

  return (
    <div className="flex flex-col">
      {docs &&
        docs.map((doc) => (
          <div className="relative">
            <DocumentCard document={doc} orientation={'horizontal'} />
            <button
              className="absolute top-2 right-2 p-2 rounded-sm text-gray-400 hover:text-red-500 hover:bg-red-200/50"
              onClick={() => handleDelete(doc.id)}
            >
              <Trash2 />
            </button>
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

const CollectionsTab = () => {
  const { id: collection_id } = useParams();
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );

  const [collections, setCollections] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination();
  const [selectedCollection, setSelectedCollection] = useState(null);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`users/me/collections`, {
        params: { page: pagination.currentPage, limit: pagination.limit },
      });
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

  useEffect(() => {
    fetchData();
  }, [
    collection_id,
    pagination.currentPage,
    pagination.limit,
    updatePagination,
  ]);

  const handleDeleteCollection = async (collection) => {
    if (!confirm(`Are you sure you want to delete this collection?`)) {
      return;
    }
    try {
      await api.delete(`collections/${collection.id}`);
      setCollections((prev) => prev.filter((c) => c.id !== collection.id));
    } catch (err) {
      alert(
        `Error: ${err.response?.data?.message || 'Something went wrong, please try again.'}`
      );
    }
  };

  if (selectedCollection)
    return (
      <div className="flex flex-col">
        <div className="flex flex-row items-center gap-2">
          <button
            onClick={() => setSelectedCollection(null)}
            className="rounded-md p-2 text-gray-700 hover:bg-gray-200/50 "
          >
            <GoBackIcon />
          </button>

          <CollectionIcon color={'blue'} fill={'blue'} size={48} />
          <div className="flex ">
            <div>
              <div className="items-center flex flex-row gap-x-2 text-xl text-black font-bold">
                {selectedCollection.name}
                <button
                  className="hover:text-blue-500 hover:cursor-pointer"
                  onClick={() => alert('Rename collection feature coming soon')}
                >
                  <Pen size={16} />
                </button>
              </div>
              <div>
                {selectedCollection?.total_items || 0} item
                {selectedCollection?.total_items ? 's' : ''}
              </div>
            </div>
          </div>
        </div>

        <hr className="text-gray-300 my-1" />

        <CollectionDetails collection={selectedCollection} />
      </div>
    );
  else
    return (
      <div className="flex flex-col flex-1">
        <Modal
          isOpen={createDialogOpen}
          onClose={() => setCreateDialogOpen(false)}
          background={'backdrop-blur-xs'}
        >
          <CollectionCreateForm
            onExit={() => setCreateDialogOpen(false)}
            onSuccess={() => fetchData()}
          />
        </Modal>

        <div className="flex flex-row items-center gap-2 px-10">
          <div className="text-black font-bold text-xl">Your Collections</div>
          <button
            className="flex flex-row p-2 m-2 gap-1 items-center rounded-xl text-gray-500 text-sm font-semibold border border-gray-300 hover:text-sky-500 hover:border-sky-500"
            onClick={() => {
              setCreateDialogOpen(true);
            }}
          >
            <AddCollectionIcon size={32} />
          </button>
        </div>

        <hr className="text-gray-300 my-2" />

        <CollectionListTab
          collections={collections}
          onDeleteCollection={handleDeleteCollection}
          onSelectCollection={(c) => setSelectedCollection(c)}
        />
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
