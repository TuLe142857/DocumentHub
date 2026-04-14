import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Search, Upload } from 'lucide-react';
import logo from '@/assets/react.svg';
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
  if (isLoading) {
    return <>Loading</>;
  }

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchKeyWord.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchKeyWord)}`);
    }
  };

  return (
    <div className="flex flex-row px-10 h-20 justify-between items-center w-screen gap-1 bg-sky-300 ">
      {/*
          LOGO
      */}
      <div className="flex flex-row items-center gap-2 hover:cursor-pointer">
        <img
          src={logo}
          alt="Logo"
          className="w-10 h-10 bg-white rounded-full"
          onClick={() => navigate('/')}
        ></img>
        <div className="text-xl text-center text-white font-bold ">
          DocumentHub
        </div>
      </div>

      {/*
            SEARCH BAR
      */}
      <form
        onSubmit={handleSearch}
        className="flex flex-row rounded bg-white w-1/2 justify-center"
      >
        <input
          type="text"
          value={searchKeyWord}
          onChange={(e) => setSearchKeyWord(e.target.value)}
          placeholder="Search..."
          className="flex flex-1 m-2 p-2 rounded-sm bg-white"
        />
        <button
          type="submit"
          className="p-2 px-4 m-2 rounded-xl bg-sky-300 hover:bg-sky-500"
        >
          <Search className="text-white" />
        </button>
      </form>

      {/*
           USER MENU
      */}
      {isAuthenticated && (
        <div className="flex flex-row items-center gap-2">
          <button
            className="flex flex-row bg-white p-2 px-4 m-2 rounded-xl shadow-sm hover:bg-sky-500 hover:text-white"
            onClick={() => navigate('/upload')}
          >
            <Upload />
            <div>Upload</div>
          </button>
          <AvatarDropDown user={user} />
        </div>
      )}
      {!isAuthenticated && (
        <div className="flex flex-row">
          <button
            onClick={() => navigate('/login')}
            className="bg-white p-2 m-2 rounded-xl shadow-sm hover:bg-sky-500 hover:text-white"
          >
            Login
          </button>
          <button
            className="bg-white p-2 m-2 rounded-xl shadow-sm hover:bg-sky-500 hover:text-white"
            onClick={() => navigate('/register')}
          >
            Register
          </button>
        </div>
      )}
    </div>
  );
};

export default Header;
