import { useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { LogOut, UserPen, User, Upload, Bookmark } from 'lucide-react';

import avatar from '@/assets/avatar.jpg';
import { useDispatch } from 'react-redux';
import { logout } from '@/store/slice/userSlice.jsx';
import api from '@/api/api.js';

const MenuItem = ({ name, icon, onClick, className }) => {
  return (
    <button
      onClick={onClick}
      className={`flex flex-row w-full m-1 p-2 gap-x-2 rounded-sm hover:bg-sky-100 whitespace-nowrap ${className}`}
    >
      {icon}
      <div>{name}</div>
    </button>
  );
};

const Separator = () => {
  return <hr className="border-gray-300 my-2 w-full" />;
};

const AvatarDropDown = ({ user }) => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const dispatch = useDispatch();
  const modalRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    try {
      if (confirm('Are you sure you want to logout?')) {
        await api.post('/auth/logout');
        dispatch(logout());
        navigate('/login');
      }
    } catch {
      alert('Error logging out');
    }
  };

  return (
    <div ref={modalRef} className="relative">
      <img
        src={user?.avatar_url || avatar}
        alt="avatar"
        onClick={() => setIsOpen(!isOpen)}
        className="w-10 h-10 bg-white rounded-full"
      ></img>
      {isOpen && (
        <div className="absolute right-0 mt-2 p-2 flex flex-col items-start bg-white rounded-xl shadow-2xl">
          <MenuItem
            className="font-bold"
            name={user.username}
            icon={<User />}
            onClick={() => navigate(`/users/${user.username}`)}
          />
          <Separator />
          <MenuItem
            name="Profile"
            icon={<UserPen />}
            onClick={() => navigate(`/users/${user.username}?tab=overview`)}
          />
          <MenuItem
            name="My Collections"
            icon={<Bookmark />}
            onClick={() => navigate(`/users/${user.username}?tab=collections`)}
          />
          <MenuItem
            name="My Documents"
            icon={<Upload />}
            onClick={() => navigate(`/users/${user.username}?tab=documents`)}
          />
          <Separator />
          <MenuItem
            className="text-red-500"
            name="Logout"
            icon={<LogOut />}
            onClick={handleLogout}
          />
        </div>
      )}
    </div>
  );
};

export default AvatarDropDown;
