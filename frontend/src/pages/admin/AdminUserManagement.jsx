import { useState, useEffect, useCallback } from 'react';
import adminApi from '@/api/adminApi.js';
import usePagination from '@/hooks/usePagination.jsx';
import PageNavigation from '@/components/PageNavigation.jsx';
import { toast } from 'react-toastify';
import {
  ShieldCheck as UserActiveIcon,
  ShieldAlert as UserInactiveIcon,
  Mail as MailIcon,
  User as UserIcon,
  UserCheck as UnbanUserIcon,
  UserX as BanUserIcon,
} from 'lucide-react';

const AdminUserManagement = () => {
  // search
  const [search, setSearch] = useState('');
  const [searchDebounced, setSearchDebounced] = useState('');
  const [filterActive, setFilterActive] = useState('');

  const [users, setUsers] = useState([]);
  const { pagination, updatePagination, setPage } = usePagination();

  const fetchUsers = useCallback(async () => {
    try {
      const params = {
        page: pagination.currentPage,
        limit: pagination.limit,
      };
      const q = searchDebounced.trim();
      if (q !== '') {
        if (q.includes('@')) {
          params['email'] = q.trim();
        } else {
          params['username'] = q.trim();
        }
      }
      if (filterActive !== null && filterActive !== '') {
        params['is_active'] = filterActive;
      }
      console.log(params);

      const response = await adminApi.getUser(params);
      const meta = response.data.meta;
      updatePagination({
        currentPage: meta.current_page,
        limit: meta.per_page,
        totalPages: meta.total_pages,
        totalItems: meta.total_items,
        hasNextPage: meta.has_next,
        hasPreviousPage: meta.has_prev,
      });

      setUsers(response.data.data);
    } catch (err) {
      console.log('err fetch user', err);
    }
  }, [
    searchDebounced,
    filterActive,
    pagination.currentPage,
    pagination.limit,
    updatePagination,
  ]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setSearchDebounced(search);
      setPage(1);
    }, 500);
    return () => {
      clearTimeout(timeout);
    };
  }, [search, setPage]);

  const handleToggleUserStatus = async (user) => {
    try {
      if (user.is_active) {
        const reason = prompt('Please enter reason to ban this user');
        if (!reason) {
          return;
        }
        await adminApi.banUser(user.id, reason);
      } else {
        if (!confirm('Confirm ?')) {
          return;
        }
        await adminApi.unbanUser(user.id);
      }
      // update user
      setUsers((prev) =>
        prev.map((u) =>
          u.id === user.id ? { ...u, is_active: !user.is_active } : u
        )
      );
    } catch (err) {
      toast.error(err?.response?.data?.message || 'Error fetching user');
    }
  };

  return (
    <div className="flex flex-col p-1">
      {/*Title*/}
      <div className="text-2xl m-2 font-extrabold">User Management</div>

      {/*Search Filter*/}
      <div className="sticky top-0 left-0 flex flex-row p-2 my-4 items-center gap-2 rounded-lg bg-white shadow border border-gray-300">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="search username or email"
          className={`
          flex-1 p-2 rounded-sm border border-gray-200
          text-lg font-normal
          bg-gray-100 focus:outline-blue-500 max-w-100 `}
        />

        <select
          value={filterActive}
          onChange={(e) => setFilterActive(e.target.value)}
          className={`
           p-2 rounded-sm border border-gray-200
          text-lg font-normal
          bg-gray-100 focus:outline-blue-500 max-w-100 `}
        >
          <option value={''}>All status</option>
          <option value={'true'}>Active</option>
          <option value={'false'}>Banned</option>
        </select>
      </div>

      {/*Users Table*/}
      <table className="bg-white shadow rounded-xl overflow-hidden">
        <colgroup className="w-full table-fixed">
          <col className="w-1/4" />
          <col className="w-1/3" />
          <col className="w-1/6" />
          <col className="w-1/6" />
        </colgroup>

        <thead className="bg-gray-50">
          <tr className="text-left text-sm text-gray-600">
            <th className="px-4 py-3">Username</th>
            <th className="px-4 py-3">Email</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Action</th>
          </tr>
        </thead>

        <tbody>
          {users &&
            users.map((user) => (
              <tr
                key={user.name}
                className="group text-left text-md text-black border-t border-gray-200 hover:bg-sky-100/50 transition"
              >
                <td className="px-4 py-2 truncate">
                  <div className="flex flex-row items-center gap-1">
                    <UserIcon className="font-normal text-gray-400" />
                    <span>{user.username}</span>
                  </div>
                </td>

                <td className="px-4 py-2 truncate">
                  <div className="flex flex-row items-center gap-1">
                    <MailIcon className="text-gray-400" size={16} />
                    <span>{user.email}</span>
                  </div>
                </td>

                <td className="px-4 py-2 truncate">
                  <span
                    className={`
                    p-1.5 truncate font-semibold
                    ${user.is_active ? 'text-green-500' : 'text-red-500'}
                    `}
                  >
                    {user.is_active ? 'Active' : 'Banned'}
                  </span>
                </td>

                <td className="px-4 py-2 truncate">
                  <button
                    onClick={() => handleToggleUserStatus(user)}
                    className={`
                    p-1.5 truncate font-semibold rounded-lg 
                    ${
                      !user.is_active
                        ? 'text-green-500 bg-green-100/50 hover:bg-green-100'
                        : 'text-red-500 bg-red-100/50 hover:bg-red-100'
                    }
                    `}
                  >
                    {user.is_active ? 'Ban user' : 'Unban User'}
                  </button>
                </td>
              </tr>
            ))}
        </tbody>
      </table>

      {/*Pagination*/}
      <PageNavigation
        page={pagination.currentPage}
        totalPage={pagination.totalPages}
        onPageChange={setPage}
      />
    </div>
  );
};

export default AdminUserManagement;
