import { useSelector } from 'react-redux';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Search, Upload, LogIn, UserPlus, BookOpen } from 'lucide-react';
import AppLogo from '@/components/AppLogo.jsx';
import AvatarDropDown from '@/components/AvatarDropDown.jsx';

/**
 * Include: app logo, search bar, avatar dropdown(if login, else login/register button)
 * @returns {React.JSX.Element}
 * @constructor
 */
const Header = () => {
  const [searchKeyWord, setSearchKeyWord] = useState('');

  const { isLoading, isAuthenticated, user } = useSelector(
    (state) => state.user
  );
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    setSearchKeyWord(searchParams.get('q') || '');
  }, [searchParams, location.pathname]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchKeyWord.trim()) {
      if (location.pathname === '/search') {
        const params = new URLSearchParams(searchParams);
        params.set('q', searchKeyWord);
        setSearchParams(params);
      } else {
        const params = new URLSearchParams(location.search);
        params.set('q', searchKeyWord);
        navigate(`/search?${params.toString()}`);
      }
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    setSearchKeyWord(e.target.value);
  };

  if (isLoading) {
    return <>Loading</>;
  }

  return (
    <div className="sticky top-0 z-9999 shadow-sm flex flex-row w-screen  px-2 sm:px-10 h-20 justify-between items-center  gap-2 bg-white ">
      {/*
          LOGO
      */}

      <AppLogo alwaysFull={false} />

      {/*
            SEARCH BAR
      */}
      <form
        onSubmit={handleSearch}
        className="group flex flex-row flex-1 gap-x-2 items-center px-2 rounded-full bg-gray-100 border border-gray-300 justify-center focus-within:outline focus-within:outline-blue-500"
      >
        <Search className="text-gray-500 group-focus-within:text-blue-500" />
        <input
          type="text"
          value={searchKeyWord}
          onChange={handleChange}
          placeholder="Search..."
          className="flex-1 text-lg my-1 p-1  focus:outline-none"
        />
      </form>

      {/*
           USER MENU
      */}
      {isAuthenticated && (
        <div className="flex flex-row items-center gap-2">
          <button
            className="hidden sm:flex sm:flex-row py-2 px-4 m-2  rounded-full text-white bg-blue-500 border hover:bg-blue-700"
            onClick={() => navigate('/upload')}
          >
            <Upload />
            <div className="hidden md:block">Upload</div>
          </button>
          <AvatarDropDown user={user} className="min-w-10 min-h-10 " />
        </div>
      )}
      {!isAuthenticated && (
        <div className="flex flex-row">
          <button
            onClick={() => navigate('/login')}
            className="flex gap-x-1 p-2 m-2 rounded-lg text-blue-500 bg-sky-100/50 border border-blue-300/50 hover:bg-sky-200/50"
          >
            <div className="hidden md:block">Login</div>
            <LogIn />
          </button>
          <button
            className="flex gap-x-1 p-2 m-2 rounded-xl text-white bg-blue-500 hover:bg-blue-600"
            onClick={() => navigate('/register')}
          >
            <div className="hidden md:block">Register</div>
            <UserPlus />
          </button>
        </div>
      )}
    </div>
  );
};

export default Header;
