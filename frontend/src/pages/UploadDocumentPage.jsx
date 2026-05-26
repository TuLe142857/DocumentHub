import { useState, useEffect } from 'react';
import api from '@/api/api.js';

const UploadDocumentPage = () => {
  const [formData, setFormData] = useState({
    title: '',
    desc: '',
    file: null,
    category_id: null,
    tags: [],
    visibility: 'Public',
  });
  const [tagInput, setTagInput] = useState('');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categories, setCategories] = useState([]);
  const [supportedTypes, setSupportedTypes] = useState([
    '.docx',
    '.doc',
    '.ppt',
    '.pptx',
    '.pdf',
  ]);
  const [maxFileSize, setMaxFileSize] = useState(1024 * 1024 * 5);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [categoriesRes, typeRes, sizeRes] = await Promise.all([
          api.get('/categories'),
          api.get('/documents/supported_types'),
          api.get('/documents/max_size'),
        ]);
        setCategories(categoriesRes.data?.data);
        setSupportedTypes(typeRes.data?.data);
        setMaxFileSize(sizeRes.data?.data);
      } catch (err) {
        setError(
          err?.response?.data?.message ||
            'Something went wrong, please try again'
        );
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleFormChange = (e) => {
    e.preventDefault();
    const { name, type, files, value } = e.target;

    if (type === 'file' && name === 'file') {
      const file = files[0];
      if (!file) return;
      setFormData((prev) => ({ ...prev, file: file }));
      alert(file);
    } else if (name === 'tags') {
      if (value.endsWith(' ') || value.endsWith(',')) {
        const newTag = value.replace(' ', '').replace(',', '');
        if (newTag !== '' && !formData.tags.includes(newTag)) {
          setFormData((prev) => ({ ...prev, tags: [...prev.tags, newTag] }));
          setTagInput('');
        }
      } else {
        setTagInput(value);
      }
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      setError(null);
      // await api.post('/documents', formData, {
      //   headers: { 'Content-Type': 'multipart/form-data' },
      // });
      const data = new FormData();

      data.append('title', formData.title);
      data.append('desc', formData.desc);
      data.append('file', formData.file);
      data.append('visibility', formData.visibility);
      data.append('category_id', formData.category_id);

      formData.tags.forEach((tag) => {
        data.append('tags', tag);
      });
      await api.post('/documents', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      alert('ok');
    } catch (err) {
      setError(
        err?.response?.data?.message || 'Something went wrong, please try again'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 p-5 items-center justify-center bg-sky-100">
      <form
        className="flex flex-col w-full md:w-3/5 lg:w-1/2 p-5 gap-2 rounded-xl bg-white"
        onSubmit={handleFormSubmit}
      >
        <div className="font-bold text-3xl text-black">Upload Document</div>
        {error && <div className="text-red-500 text-xl">Error: {error}</div>}
        <div className="text-black font-bold">Title *</div>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleFormChange}
          placeholder="Title"
          className="bg-white rounded m-2 p-2  border border-gray-500 hover:outline-sky-500"
        />

        <div className="text-black font-bold">Description</div>
        <textarea
          name="desc"
          value={formData.desc}
          onChange={handleFormChange}
          className="bg-white rounded m-2 p-2  border border-gray-500 hover:outline-sky-500"
        />

        <div className="text-black font-bold">File</div>
        <div className="flex flex-row items-center gap-x-2">
          <label
            htmlFor="fileSelect"
            className="text-lg p-2  rounded-xl bg-sky-300 hover:bg-sky-500"
          >
            Select file *
          </label>
          <input
            id="fileSelect"
            type="file"
            name="file"
            onChange={handleFormChange}
            hidden={true}
          />
          {formData.file ? (
            <div>{formData.file.name}</div>
          ) : (
            <div>No file choosen</div>
          )}
        </div>

        <div className="text-black font-bold">Visibility</div>
        <select
          name="visibility"
          value={formData.visibility}
          onChange={handleFormChange}
          className="bg-white rounded m-2 p-2  border border-gray-500 hover:outline-sky-500"
        >
          <option value={''}>--select--</option>
          <option value={'PUBLIC'}>Public</option>
          <option value={'PRIVATE'}>Private</option>
        </select>

        <div className="text-black font-bold">Category</div>
        <select
          name="category_id"
          value={formData.category_id}
          onChange={handleFormChange}
          className="bg-white rounded m-2 p-2  border border-gray-500 hover:outline-sky-500"
        >
          <option value={''}>--select--</option>
          {categories &&
            categories.map((category) => (
              <option value={category.id}>{category.name}</option>
            ))}
        </select>

        <div className="text-black font-bold">Tags</div>
        <div className="flex flex-row gap-1 gap-x-3 flex-wrap">
          {formData.tags.map((tag) => (
            <div className="flex flex-row rounded-xl p-2 px-3  gap-x-2 bg-sky-200/50 text-sm text-blue-500">
              <div className="font-bold">{tag}</div>
              <div
                className="hover:text-red-500 hover:cursor-pointer"
                onClick={() => {
                  setFormData((prev) => ({
                    ...prev,
                    tags: prev.tags.filter((t) => t !== tag),
                  }));
                }}
              >
                x
              </div>
            </div>
          ))}
        </div>
        <input
          name="tags"
          value={tagInput}
          onChange={handleFormChange}
          className="bg-white rounded m-2 p-2  border border-gray-500 hover:outline-sky-500"
          placeholder="Add tags separate by ' ' or ','"
        />

        <button
          type="submit"
          className="p-2 rounded-xl text-lg font-bold text-white bg-sky-300 hover:bg-sky-500"
        >
          Upload
        </button>
      </form>
    </div>
  );
};

export default UploadDocumentPage;
