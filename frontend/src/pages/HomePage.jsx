import api from '@/api/api.js';
import DocumentCard from '@/components/DocumentCard.jsx';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp } from 'lucide-react';

const CategoryBar = ({ categories }) => {
  const navigate = useNavigate();
  return (
    <div className="flex flex-row gap-2 items-center overflow-x-auto w-screen p-2 bg-sky-100">
      {categories &&
        categories.map((category) => (
          <div
            key={category.id}
            className="font-bold bg-white text-blue-700 rounded-full p-2 hover:cursor-pointer hover:bg-sky-200"
            onClick={() =>
              navigate(`/search?category_ids=${encodeURIComponent(category.id)}`)
            }
          >
            {category?.name || 'something went wrong'}
          </div>
        ))}
    </div>
  );
};

/**
 * @param {Array<import('@/types/document.jsx').Document>} documents
 * @returns {React.JSX.Element}
 * @constructor
 */
const DocumentList = ({ documents }) => {
  return (
    <div className="flex flex-row w-screen overflow-x-auto gap-2">
      {documents &&
        documents.map((document) => (
          <DocumentCard
            document={document}
            key={document.id}
            className="border border-gray-200 hover:bg-gray-100/50"
          />
        ))}
    </div>
  );
};

const HomePage = () => {
  const [categories, setCategories] = useState([]);
  const [trending, setTrending] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await api.get('/categories');
        const data = response.data?.data;
        console.log(JSON.stringify(data, null, 2));
        if (!data) {
          console.log('Can not fetch Categories');
        }
        setCategories(data);
      } catch {
        console.log('Can not fetch Categories');
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchTrending = async () => {
      setTrending([]);
      try {
        for (const category of categories) {
          const params = {
            category_ids: category.id,
            sort: '-view,-like,-download,-created_at',
            limit: 5
          };

          const response = await api.get(`search`, { params: params });
          const documents = response.data?.data;
          const data = {
            category: category.name,
            documents: documents,
          };
          setTrending((prev) => [...prev, data]);
        }
      } catch (err) {
        console.log(err);
      }
    };
    fetchTrending();
  }, [categories]);

  useEffect(() => {
    console.log('trending', trending);
  }, [trending]);

  return (
    <div className="flex flex-col w-screen bg-white">
      <CategoryBar categories={categories} />

      {trending &&
        trending.map((t) => (
          <div key={t.id}>
            <div className="flex flex-row gap-x-2 m-2 items-center text-2xl font-extrabold text-black">
              <TrendingUp
                size={48}
                className="rounded-sm p-2 text-white bg-linear-to-tr  from-blue-700 to-cyan-200"
              />
              <span className="text-center">Trending in </span>
              <span className="text-center rounded text-transparent bg-clip-text bg-linear-to-r from-blue-500 to-cyan-500">
                {t.category}
              </span>
            </div>
            <DocumentList documents={t.documents} key={t.id} />
          </div>
        ))}
    </div>
  );
};

export default HomePage;
