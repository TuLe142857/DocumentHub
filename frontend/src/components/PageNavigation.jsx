import { ArrowRight, ArrowLeft } from 'lucide-react';

/**
 * @callback onPageChangeCallback
 * @param {number} page
 */

/**
 * @param {Object} props
 * @param {number} props.page
 * @param {number} props.totalPage
 * @param {onPageChangeCallback} props.onPageChange
 * @returns {React.JSX.Element}
 * @constructor
 */
const PageNavigation = ({ page, totalPage, onPageChange }) => {
  return (
    <div className="flex flex-row item-center justify-center gap-x-5 text-center bg-red-500">
      <button
        className="flex m-2 p-2 rounded-xl bg-sky-200 disabled:bg-gray-400 hover:bg-sky-400"
        disabled={page <= 1}
        onClick={() => onPageChange && onPageChange(page - 1)}
      >
        <ArrowLeft />
      </button>

      <div className="flex items-center justify-center">
        {page}/{totalPage}
      </div>

      <button
        className="flex m-2 p-2 rounded-xl bg-sky-200 disabled:bg-gray-400 hover:bg-sky-400"
        disabled={page >= totalPage}
        onClick={() => onPageChange && onPageChange(page + 1)}
      >
        <ArrowRight />
      </button>
    </div>
  );
};

export default PageNavigation;
