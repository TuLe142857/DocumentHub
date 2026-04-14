import { Link } from 'react-router-dom';
import {
  ThumbsUp,
  Download,
  Eye,
  Layers,
  GlobeOff,
  Globe,
  Dot,
} from 'lucide-react';

/**
 * @import {Document, DocumentDetail} from "@/types/document.jsx"
 */

const STATUS_CONFIG = {
  DELETED: 'bg-red-200/50 text-red-500',
  BANNED: 'bg-red-200/50 text-red-500',
  PROCESSING: 'bg-blue-200/50 text-blue-500',
};

/**
 *
 * @param {Document} doc
 * @returns {React.JSX.Element}
 * @constructor
 */

const DocumentThumbnail = ({ doc }) => {
  return (
    <Link
      to={`/documents/${doc.id}`}
      className="relative w-full h-full overflow-hidden rounded-xl"
    >
      <img
        src={doc.file_thumbnail_url}
        alt={doc.title}
        className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
      />
      {doc.status && doc.status !== 'READY' && STATUS_CONFIG[doc.status] && (
        <div
          className={`absolute right-2 top-2 px-3 py-1 rounded-sm text-xs font-bold uppercase ${STATUS_CONFIG[doc.status]}`}
        >
          {doc.status}
        </div>
      )}
    </Link>
  );
};

const DocumentInfo = ({ doc }) => {
  const formatNumber = (num) =>
    num >= 1000 ? (num / 1000).toFixed(1) + 'k' : num || 0;

  return (
    <div className="flex flex-col flex-1 p-2 gap-y-1 overflow-hidden">
      <h3
        className="text-lg text-black font-bold line-clamp-2"
        title={doc.title}
      >
        {doc.title}
      </h3>

      <div className="flex flex-row items-center text-sm text-gray-600">
        <Link
          to={`/users/${doc.owner}`}
          className="font-medium hover:underline truncate max-w-30"
        >
          {doc.owner}
        </Link>
        <Dot className="shrink-0" />
        <div className="flex flex-row gap-x-1.5 items-center text-gray-500">
          {doc.visibility === 'PUBLIC' ? (
            <Globe size={16} />
          ) : (
            <GlobeOff size={16} />
          )}
          <span className="capitalize">{doc.visibility?.toLowerCase()}</span>
        </div>
      </div>

      <div className="mt-1 w-fit px-2 py-0.5 rounded-md text-xs text-blue-600 border border-blue-200 font-semibold bg-blue-50">
        {doc.category}
      </div>

      <hr className="text-gray-200 my-3 mt-auto" />

      <div className="flex flex-row items-center justify-between text-xs text-gray-500 font-medium">
        <div className="flex gap-x-3">
          <span className="flex items-center gap-x-1">
            <Eye size={16} />
            {formatNumber(doc.view_count)}
          </span>
          <span className="flex items-center gap-x-1">
            <Download size={16} />
            {formatNumber(doc.download_count)}
          </span>
          <span className="flex items-center gap-x-1">
            <ThumbsUp size={16} />
            {formatNumber(doc.like_count)}
          </span>
        </div>
        <div className="flex items-center gap-x-1">
          <Layers size={16} />
          <span>{doc.page_count || 0} pages</span>
        </div>
      </div>
    </div>
  );
};

/**
 * @param {string} className
 * @param {'horizontal' | 'vertical'} orientation
 * @param {import('@/types/document').Document} document
 */
const DocumentCard = ({
  document,
  orientation = 'vertical',
  className = 'bg-white border border-gray-200 hover:bg-gray-100',
}) => {
  return (
    <div
      className={`
      flex group transition-all duration-200 overflow-hidden rounded-xl p-2.5
      ${orientation === 'vertical' ? 'flex-col w-64' : 'flex-row h-48 w-full'}
      ${className}
    `}
    >
      <div
        className={`overflow-hidden rounded-xl bg-sky-100 ${orientation === 'vertical' ? 'w-full h-48' : 'h-full w-40'}`}
      >
        <DocumentThumbnail doc={document} />
      </div>
      <DocumentInfo doc={document} />
    </div>
  );
};

export default DocumentCard;
