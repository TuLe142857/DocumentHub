import { useSearchParams } from 'react-router-dom';
import { useState } from 'react';
import { Funnel } from 'lucide-react';

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const query = useState({
    keyword: searchParams.get('q') || '',
    category_id: searchParams.get('category_id'),
  });
  return (
    <div>
      <Funnel />
      Search page. Coming Soon
      <div>Search params:{JSON.stringify(query, null, 2)}</div>
    </div>
  );
};

export default SearchPage;
