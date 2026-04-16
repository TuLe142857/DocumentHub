import {
  Folder as CollectionIcon,
  Layers as ItemCountIcon,
} from 'lucide-react';

const CollectionCard = ({ collection, className = '' }) => {
  return (
    <div className={`flex flex-row items-center gap-2 ${className}`}>
      <div className="p-1.5 rounded bg-sky-100/50">
        <CollectionIcon size={32} fill="white" color="rgb(48, 193, 255)" />
      </div>
      <div className="min-w-0 flex flex-col">
        <div className="text-black text-md font-bold line-clamp-1">
          {collection.name}
        </div>
        <div className="flex flex-row items-center font-semibold text-gray-500 text-xs gap-2">
          <ItemCountIcon size={16} />
          {`${collection.total_items} item${collection?.total_items ? 's' : ''}`}
        </div>
      </div>
    </div>
  );
};
export default CollectionCard;
