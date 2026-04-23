import { NavLink, useNavigate, useNavigation } from 'react-router-dom';
import { useState } from 'react';

import {
  Menu,
  LayoutDashboard,
  Users,
  TriangleAlert,
  Grid3x3,
  FileX,
  LogOut,
  ChevronLeft,
} from 'lucide-react';

import { useDispatch } from 'react-redux';
import { logout } from '@/store/slice/userSlice.jsx';
import authApi from '@/api/authApi.js';
import { toast } from 'react-toastify';

const SideBarItem = ({ to, icon, name, end, showFull }) => {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => `
        group relative flex items-center h-11 px-3 mx-3 rounded-lg cursor-pointer
        transition-all duration-200 ease-in-out
        ${
          isActive
            ? 'bg-blue-500/10 text-blue-400'
            : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-100'
        }
      `}
    >
      {/* Active Indicator Left Border */}
      {({ isActive }) => (
        <>
          <div
            className={`
            absolute left-0 top-1/2 -translate-y-1/2 w-1 rounded-r-md bg-blue-500
            transition-all duration-300 ease-out
            ${isActive ? 'h-3/4 opacity-100' : 'h-0 opacity-0'}
          `}
          />

          <div className="flex items-center justify-center ">{icon}</div>

          <span
            className={`
            whitespace-nowrap font-medium text-sm
            transition-all duration-300 ease-in-out overflow-hidden
            ${showFull ? 'w-auto opacity-100 ml-3' : 'w-0 opacity-0 ml-0'}
          `}
          >
            {name}
          </span>
        </>
      )}
    </NavLink>
  );
};

const AdminSidebar = () => {
  const [open, setOpen] = useState(true);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      if (confirm('Are you sure you want to logout?')) {
        await authApi.logout();
        dispatch(logout());
        navigate('/login');
      }
    } catch (err) {
      const msg =
        err?.response?.data?.message || err?.message || 'Something went wrong.';
      toast.error(`Error logging out: ${msg}`);
    }
  };
  return (
    <aside
      className={`
      relative flex flex-col h-screen bg-slate-900 border-r border-slate-800 
      mr-3
      transition-all duration-300 ease-in-out z-20 shrink-0
      ${open ? 'w-64' : 'w-20'}
    `}
    >
      <span
        className={`
          font-bold text-lg text-slate-100 whitespace-nowrap
          transition-all duration-300 overflow-hidden
          ${open ? 'w-auto opacity-100 ml-3' : 'w-0 opacity-0 ml-0'}
        `}
      >
        Admin Panel
      </span>

      <button
        onClick={() => setOpen(!open)}
        className="absolute -right-3 top-5 p-1 rounded-full bg-slate-800 border border-slate-700 text-slate-400 hover:text-slate-100 hover:bg-slate-700 transition-colors z-30"
      >
        {open ? <ChevronLeft size={16} /> : <Menu size={16} />}
      </button>

      {/* Navigation Links */}
      <nav className="flex-1 flex flex-col gap-y-1.5 overflow-y-auto overflow-x-hidden py-2">
        <div
          className={`px-4 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider transition-all duration-300 ${open ? 'opacity-100' : 'opacity-0 hidden'}`}
        >
          Menu
        </div>

        <SideBarItem
          to=""
          icon={<LayoutDashboard size={20} />}
          name="Dashboard"
          end
          showFull={open}
        />
        <SideBarItem
          to="users"
          icon={<Users size={20} />}
          name="Users"
          showFull={open}
        />
        <SideBarItem
          to="categories"
          icon={<Grid3x3 size={20} />}
          name="Categories"
          showFull={open}
        />
        <SideBarItem
          to="reports"
          icon={<TriangleAlert size={20} />}
          name="Reports"
          showFull={open}
        />
        <SideBarItem
          to="documents"
          icon={<FileX size={20} />}
          name="Documents"
          showFull={open}
        />
      </nav>

      <div className="p-3 border-t border-slate-800/50 flex flex-col gap-1">
        <button
          className={`
          group relative flex items-center h-11 px-3 mt-1 rounded-lg cursor-pointer
          text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-colors duration-200
          ${open ? 'mx-0' : 'justify-center mx-0'}
        `}
          onClick={handleLogout}
        >
          <div className="flex items-center justify-center">
            <LogOut size={24} />
          </div>
          <span
            className={`whitespace-nowrap font-medium text-sm transition-all duration-300 overflow-hidden ${open ? 'w-auto opacity-100 ml-3' : 'w-0 opacity-0 ml-0'}`}
          >
            Logout
          </span>
        </button>
      </div>
    </aside>
  );
};

export default AdminSidebar;
