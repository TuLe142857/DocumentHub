import api from '@/api/api.js';
import { toast } from 'react-toastify';
import { X as ExitButtonIcon, PenLine as EditIcon } from 'lucide-react';
import { useState, useEffect } from 'react';

import TagInput from '@/components/forms/TagInput.jsx';

const FormHeader = ({ onExit }) => (
  <>
    <button
      className="absolute top-1 right-1 p-2 text-gray-500 rounded-full  hover:bg-gray-400/50"
      onClick={() => onExit()}
    >
      <ExitButtonIcon />
    </button>
    <div className="flex gap-2 text-xl font-semibold ">
      <EditIcon color={'blue'} />
      <div>Edit Document</div>
    </div>
    <hr className="text-gray-200 my-1" />
  </>
);

const FormFooter = ({ onSubmit, onCancel }) => (
  <div className="self-end mr-5 flex flex-row gap-2 text-lg font-semibold">
    <button
      onClick={() => onCancel()}
      className="rounded-md p-2 0 text-gray-600 hover:bg-gray-200"
    >
      Cancel
    </button>

    <button
      onClick={onSubmit}
      className="rounded-md p-2 bg-green-500 text-white"
    >
      Save
    </button>
  </div>
);

/**
 * @import {Document} from '@/types/document.jsx'
 * @param {Document} doc
 * @param onCancel
 * @param onUpdate
 * @param className
 * @returns {React.JSX.Element}
 * @constructor
 */
const DocumentEditForm = ({ doc, onCancel, onUpdate, className }) => {
  const [formData, setformData] = useState({
    desc: doc.desc || null,
    title: doc.title || null,
    category_id: doc?.category_id,
    visibility: doc.visibility,
    tags: doc.tags || null,
  });

  // available categories in system
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await api.get('/categories');
        setCategories(res.data.data);
      } catch (error) {
        toast.error(
          error?.response?.data?.message ||
            'Something went wrong, please try again later.'
        );
      }
    };
    fetchCategories();
  }, []);

  const handleFormChange = (e) => {
    e.preventDefault();
    setformData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };
  const handleSubmit = async () => {
    // check diff .....

    const toast_id = toast.loading('Updating...');
    try {
      await api.patch(`/documents/${doc.id}`, formData);
      console.log('form', formData);
      // update ...

      const { category_id, ...updateData } = formData;
      if (formData?.category_id) {
        updateData.category = categories.find(
          (c) => String(c.id) === formData.category_id
        ).name;
      }
      onUpdate((prev) => ({
        ...prev,
        ...updateData,
      }));
      console.log('updated', updateData);
      toast.update(toast_id, {
        type: 'success',
        render: 'Update Success',
        isLoading: false,
        autoClose: 3000,
      });
    } catch (err) {
      toast.update(toast_id, {
        type: 'error',
        render:
          err?.response?.data?.message ||
          'Something went wrong, please try again.',
        isLoading: false,
        autoClose: 3000,
      });
      console.error('Exception', err);
    }
  };

  return (
    <div
      className={`relative flex flex-col gap-2 p-2 bg-white rounded-xl min-w-100 min-h-100 ${className}`}
    >
      <FormHeader onExit={onCancel} />

      <div className="flex flex-col flex-1 gap-2 overflow-y-auto">
        <div className="text-black font-bold">Title</div>
        <input
          name="title"
          value={formData.title}
          onChange={handleFormChange}
          className="rounded-sm p-2 border border-gray-300 focus:outline-sky-500"
        />

        <div className="text-black font-bold">Tags</div>
        <TagInput
          tags={formData.tags}
          onAdd={(t) =>
            setformData((prev) => ({ ...prev, tags: [...prev.tags, t] }))
          }
          onRemove={(t) =>
            setformData((prev) => ({
              ...prev,
              tags: prev.tags.filter((item) => item !== t),
            }))
          }
        />

        <div className="flex flex-row gap-2">
          <div className="w-1/2 flex flex-col">
            <div className="text-black font-bold">Category</div>
            <select
              name="category_id"
              onChange={handleFormChange}
              value={formData.category_id}
              className="rounded-sm p-2 border border-gray-300 focus:outline-sky-500"
            >
              {/*<option>{formData?.category_id ? doc?.category : undefined}</option>*/}
              {formData?.category_id || <option>{doc.category}</option>}
              {categories &&
                categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
            </select>
          </div>

          <div className="w-1/2 flex flex-col">
            <div className="text-black font-bold">Visibility</div>
            <select
              name="visibility"
              value={formData.visibility}
              onChange={handleFormChange}
              className="rounded-sm p-2 border border-gray-300 focus:outline-sky-500"
            >
              <option value="PUBLIC">Public</option>
              <option value="PRIVATE">Private</option>
            </select>
          </div>
        </div>

        <div className="text-black font-bold">Descriptions</div>
        <textarea
          name="desc"
          value={formData.desc}
          onChange={handleFormChange}
          rows={4}
          className="rounded-sm min-h-25 p-2 border border-gray-300 focus:outline-sky-500 "
        />
      </div>

      <FormFooter onCancel={onCancel} onSubmit={handleSubmit} />
    </div>
  );
};

export default DocumentEditForm;
