import { useState, useEffect, useCallback } from 'react';
import categoryApi from '@/api/categoryApi.js';
import adminApi from '@/api/adminApi.js';

import {
  FolderPlus as AddCategoryIcon,
  Trash2 as DeleteIcon,
  Pen as EditIcon,
} from 'lucide-react';
import { audioWorklet } from 'globals';
import { toast } from 'react-toastify';

const AdminCategoryManagement = () => {
  const [categories, setCategories] = useState([]);

  const fetchCategories = useCallback(async () => {
    try {
      const response = await categoryApi.getCategories();
      setCategories(response.data?.data);
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const handleCreateCategory = async () => {
    const name = prompt('Enter name');
    if (!name) {
      return;
    }

    const toastId = toast.loading('Loading');
    try {
      await adminApi.createCategory(name);
      toast.update(toastId, {
        type: 'success',
        render: 'Create category successfully',
        isLoading: false,
        autoClose: 500,
      });
      fetchCategories();
    } catch (err) {
      toast.update(toastId, {
        type: 'error',
        render: err?.response?.data?.message || 'Something went wrong',
        isLoading: false,
        autoClose: 500,
      });
    }
  };

  const handleRenameCategory = async (id) => {
    const name = prompt('Enter new name');

    if (!name) {
      return;
    }

    const toastId = toast.loading('Loading');
    try {
      await adminApi.renameCategory(id, name);
      toast.update(toastId, {
        type: 'success',
        render: 'Rename category successfully',
        isLoading: false,
        autoClose: 500,
      });
      setCategories((prev) =>
        prev.map((cat) => (cat.id === id ? { ...cat, name: name } : cat))
      );
    } catch (err) {
      toast.update(toastId, {
        type: 'error',
        render: err?.response?.data?.message || 'Something went wrong',
        isLoading: false,
        autoClose: 500,
      });
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!confirm('Are you sure you want to delete this category?')) {
      return;
    }
    const toastId = toast.loading('Loading');
    try {
      await adminApi.deleteCategory(id);
      toast.update(toastId, {
        type: 'success',
        render: 'Delete category successfully',
        isLoading: false,
        autoClose: 500,
      });
      setCategories((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      toast.update(toastId, {
        type: 'error',
        render: err?.response?.data?.message || 'Something went wrong',
        isLoading: false,
        autoClose: 500,
      });
    }
  };

  return (
    <div className="flex flex-col">
      <div className="text-2xl m-2 font-extrabold">Category</div>

      <button
        className="flex flex-row items-center w-fit p-2 gap-2 rounded-sm text-white bg-blue-500  hover:bg-blue-600"
        onClick={handleCreateCategory}
      >
        <span className="text-md">Add Category</span>
        <AddCategoryIcon size={24} />
      </button>

      <table className="w-full md:w-2/3 md:self-center bg-white shadow rounded-xl overflow-hidden">
        <colgroup>
          <col className="w-full" />
          <col className="w-fit " />
        </colgroup>

        <thead>
          <tr className="text-center bg-gray-200">
            <th className="py-2 px-3 border-r border-gray-300 truncate">
              Name
            </th>
            <th className="py-2 px-3 truncate">Action</th>
          </tr>
        </thead>

        {categories &&
          categories.map((category) => (
            <tr className="text-center bg-white border-t border-gray-300 hover:bg-sky-100/50">
              <td className="py-2 px-3 border-r border-gray-300 truncate">
                {category.name}
              </td>
              <td className="py-2 px-3  truncate">
                <div className="flex flex-row gap-2 justify-center">
                  <button
                    className="rounded-md p-2 py-1.5 text-green-500  hover:bg-green-200/50"
                    onClick={() => handleRenameCategory(category.id)}
                  >
                    <EditIcon size={20} />
                  </button>

                  <button
                    className="rounded-md p-2 py-1.5 text-red-500  hover:bg-red-200/50"
                    onClick={() => handleDeleteCategory(category.id)}
                  >
                    <DeleteIcon size={20} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
      </table>
    </div>
  );
};
export default AdminCategoryManagement;
