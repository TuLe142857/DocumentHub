import { useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import {
  LogOut as LogOutIcon,
  UserPen as ProfileIcon,
  User as UserIcon,
  FileText as DocumentIcon,
  Library as CollectionIcon,
  Upload as UploadIcon,
} from 'lucide-react';

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

const AvatarDropDown = ({ user, className = '' }) => {
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
    <div ref={modalRef} className={`relative ${className}`}>
      <img
        src={user?.avatar_url || avatar}
        alt="avatar"
        onClick={() => setIsOpen(!isOpen)}
        className="w-10 h-10 bg-white rounded-full object-cover border border-gray-300"
      ></img>
      {isOpen && (
        <div className="absolute right-0 mt-2 p-2 flex flex-col items-start bg-white rounded-xl shadow-2xl border border-gray-200">
          <MenuItem
            className="font-bold"
            name={user.username}
            icon={<UserIcon />}
            onClick={() => navigate(`/users/${user.username}`)}
          />
          <Separator />
          <MenuItem
            name="Profile"
            icon={<ProfileIcon />}
            onClick={() => navigate(`/users/${user.username}?tab=overview`)}
          />
          <MenuItem
            name="My Collections"
            icon={<CollectionIcon />}
            onClick={() => navigate(`/users/${user.username}?tab=collections`)}
          />
          <MenuItem
            name="My Documents"
            icon={<DocumentIcon />}
            onClick={() => navigate(`/users/${user.username}?tab=documents`)}
          />
          <MenuItem
            name="Upload"
            icon={<UploadIcon />}
            onClick={() => navigate(`/upload`)}
          />
          <Separator />
          <MenuItem
            className="text-red-500"
            name="Logout"
            icon={<LogOutIcon />}
            onClick={handleLogout}
          />
        </div>
      )}
    </div>
  );
};

export default AvatarDropDown;
