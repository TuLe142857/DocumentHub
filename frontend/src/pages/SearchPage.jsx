import { useSearchParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { ListFilter, X as Delete, Tag, Folder } from 'lucide-react';
import api from '@/api/api.js';

import usePagination from '@/hooks/usePagination.jsx';
import PageNavigation from '@/components/PageNavigation.jsx';
import DocumentCard from '@/components/DocumentCard.jsx';

import TagInput from '@/components/forms/TagInput.jsx';
import CategoriesFilter from '@/components/CategoriesFilter.jsx';

const FilterSideBar = ({
  categories,
  selectedCategories,
  onSelectCategory,
  onRemoveCategory,

  tags,
  onAddTag,
  onRemoveTag,
  className = '',
}) => {
  return (
    <div className={`flex flex-col ${className}`}>
      <div>Category</div>
      <CategoriesFilter
        categories={categories}
        selectedCategories={selectedCategories}
        onSelect={onSelectCategory}
        onRemove={onRemoveCategory}
      />

      <div>Tag</div>
      <TagInput tags={tags} onAdd={onAddTag} onRemove={onRemoveTag} />
    </div>
  );
};

const ActiveFilters = ({
  categories,
  selectedCategories,
  onRemoveCategory,

  tags,
  onRemoveTag,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-row items-center flex-wrap gap-x-1.5 gap-y-1 ${className}`}
    >
      <div className="text-black text-md  mr-2">Filter by:</div>
      {categories
        .filter((category) => selectedCategories.includes(category.id))
        .map((category) => (
          <div className="flex flex-row items-center gap-1 rounded-md px-2 py-1 text-sm font-semibold text-gray-600 bg-white border border-gray-300 ">
            <Folder size={12} />
            <span>{category.name}</span>
            <span
              onClick={() => onRemoveCategory(category.id)}
              className="hover:text-red-500"
            >
              <Delete size={12} />
            </span>
          </div>
        ))}

      {tags.map((tag) => (
        <div className="flex flex-row items-center gap-1 rounded-md px-2 text-sm font-semibold text-gray-600 bg-white border border-gray-300 ">
          <Tag size={12} />
          <span>{tag}</span>
          <span onClick={() => onRemoveTag(tag)} className="hover:text-red-500">
            <Delete size={12} />
          </span>
        </div>
      ))}
    </div>
  );
};

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const query = useState({
    keyword: searchParams.get('q') || '',
    category_id: searchParams.get('category_id'),
  });

  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [docs, setDocs] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tags, setTags] = useState([]);
  const [openFilerSidebar, setOpenFilerSidebar] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await api.get('/categories');
        setCategories(res.data?.data);
      } catch (err) {
        setError(err?.response?.data?.message || 'Something went wrong');
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = new URLSearchParams();
        params.set('keywords', searchParams.get('q') || '');
        if (searchParams.has('category_id')) {
          params.set('category_id', searchParams.get('category_id'));
        }
        if (searchParams.has('tags')) {
          searchParams.getAll('tags').forEach((tag) => {
            params.append('tags', tag);
          });
        }
        params.set('page', pagination.currentPage);
        params.set('limit', pagination.limit);

        const res = await api.get('/search', { params: params });

        setDocs(res.data?.data);
        const meta = res.data?.meta;
        updatePagination({
          currentPage: meta.current_page,
          limit: meta.per_page,
          totalPages: meta.total_pages,
          totalItems: meta.total_items,
          hasNextPage: meta.has_next,
          hasPreviousPage: meta.has_prev,
        });
      } catch (err) {
        setError(err?.response?.data?.message || 'Something went wrong');
      } finally {
        setLoading(false);
      }
    };

    fetchDocs();
  }, [
    searchParams,
    pagination.currentPage,
    pagination.limit,
    updatePagination,
  ]);

  return (
    <div className={`flex flex-row w-screen`}>
      <div>
        <label
          className="flex "
          onClick={() => setOpenFilerSidebar(!openFilerSidebar)}
        >
          <ListFilter className="p-2 m-2 rounded bg-sky-200" size={36} />
          {openFilerSidebar ? 'Filter' : ''}
        </label>

        {openFilerSidebar && (
          <FilterSideBar
            categories={categories}
            selectedCategories={selectedCategories}
            onSelectCategory={(id) =>
              setSelectedCategories((prev) => [...prev, id])
            }
            onRemoveCategory={(id) =>
              setSelectedCategories((prev) => prev.filter((i) => i !== id))
            }
            tags={tags}
            onAddTag={(t) => setTags((prev) => [...prev, t])}
            onRemoveTag={(t) =>
              setTags((prev) => prev.filter((tag) => tag !== t))
            }
            className="sm:w-60 lg:w-100"
          />
        )}
      </div>

      <div className={'flex flex-col flex-1 py-2 mx-3 p-3 bg-gray-50'}>
        <div className="text-2xl font-bold">Search Result</div>
        <div>
          Find {pagination.totalItems} result
          {pagination.totalItems > 0 ? 's' : ''}
        </div>

        {(selectedCategories.length > 0 || tags.length > 0) && (
          <ActiveFilters
            categories={categories}
            selectedCategories={selectedCategories}
            onSelectCategory={(id) =>
              setSelectedCategories((prev) => [...prev, id])
            }
            onRemoveCategory={(id) =>
              setSelectedCategories((prev) => prev.filter((i) => i !== id))
            }
            tags={tags}
            onAddTag={(t) => setTags((prev) => [...prev, t])}
            onRemoveTag={(t) =>
              setTags((prev) => prev.filter((tag) => tag !== t))
            }
          />
        )}

        <hr className="text-gray-400 my-2" />

        <div>
          Display {docs.length} result {docs.length ? 's' : ''}
        </div>

        <div className="flex flex-row flex-wrap justify-center gap-2">
          {docs &&
            docs.map((doc) => <DocumentCard key={doc.id} document={doc} />)}
        </div>

        <div className="mt-auto" />
        <PageNavigation
          page={pagination.currentPage}
          totalPage={pagination.totalPages}
          onPageChange={setPage}
        />
      </div>
    </div>
  );
};

export default SearchPage;
