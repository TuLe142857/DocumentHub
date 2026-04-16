import { useState } from 'react';
import api from '@/api/api.js';
import { Folder as CollectionIcon, X as ExitIcon } from 'lucide-react';

const CollectionCreateForm = ({ onExit, onSuccess }) => {
  const [collectionName, setCollectionName] = useState('');
  const handleCreate = async (e) => {
    e.preventDefault();
    if (!collectionName) {
      alert('Please enter a collection name');
    }

    try {
      await api.post('/collections', { name: collectionName });
      setCollectionName('');
      alert('Created successfully.');
      onSuccess();
      onExit();
    } catch (err) {
      alert(
        err?.response?.data?.message || 'Something went wrong, please try again'
      );
    }
  };
  return (
    <form
      onSubmit={handleCreate}
      className="relative flex flex-col gap-y-3 text-lg font-semibold items-center w-100 h-fit rounded-xl shadow-xl bg-white px-10 py-5"
    >
      <button
        type="button"
        className="absolute top-1 right-1 rounded-full p-2 text-gray-500 hover:bg-gray-200"
        onClick={() => onExit()}
      >
        <ExitIcon />
      </button>

      <div className="rounded-full bg-sky-100 p-2 text-sky-500">
        <CollectionIcon size={32} />
      </div>
      <div className="text-black font-bold text-xl">Create Collection</div>
      <input
        type="text"
        value={collectionName}
        onChange={(e) => setCollectionName(e.target.value)}
        className="w-full p-2 font-normal rounded-sm border border-gray-300 focus:outline-sky-500"
        placeholder="Collection name"
      />
      <button
        type="submit"
        className="p-2 px-5 rounded-sm bg-blue-500 text-white hover:bg-blue-700"
      >
        Create
      </button>
    </form>
  );
};

export default CollectionCreateForm;
