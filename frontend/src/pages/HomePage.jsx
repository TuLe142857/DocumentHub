import api from '@/api/api.js';
import DocumentCard from '@/components/DocumentCard.jsx';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const CategoryBar = ({ categories }) => {
  const navigate = useNavigate();
  return (
    <div className="flex flex-row gap-2 items-center overflow-x-auto w-screen p-2 bg-sky-100">
      {categories &&
        categories.map((category) => (
          <div
            key={category.id}
            className="font-bold bg-white text-sky-700 rounded-xl p-2 hover:cursor-pointer hover:bg-sky-500 hover:text-white"
            onClick={() =>
              navigate(`/search?category_id=${encodeURIComponent(category.id)}`)
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
          <DocumentCard document={document} key={document.id} />
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
      } catch {}
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchTrending = async () => {
      setTrending([]);
      try {
        for (const category of categories) {
          const response = await api.get(
            `recommendation/trending?category_id=${encodeURIComponent(category.id)}`
          );
          const documents = response.data?.data;
          const data = {
            category: category.name,
            documents: documents,
          };
          setTrending((prev) => [...prev, data]);
        }
      } catch (err) {
        console.log(err);
      } finally {
      }
    };
    fetchTrending();
  }, [categories]);

  useEffect(() => {
    console.log('trending', trending);
  }, [trending]);

  return (
    <div className="flex flex-col w-screen bg-sky-50">
      <CategoryBar categories={categories} />

      {trending &&
        trending.map((t) => (
          <div key={t.id}>
            <div className="text-2xl font-bold text-black p-2">
              <span>Trending in </span>
              <span>{t.category}</span>
            </div>
            <DocumentList documents={t.documents} key={t.id} />
          </div>
        ))}
    </div>
  );
};

export default HomePage;
