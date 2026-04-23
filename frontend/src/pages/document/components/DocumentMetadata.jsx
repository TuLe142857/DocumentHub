import { useState } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

const DocumentMetadata = ({ doc, className = '' }) => {
  const [open, setOpen] = useState(false);
  return (
    <div
      className={`flex flex-col text-black font-semibold text-md ${className}`}
    >
      <div
        className="flex flex-row justify-between gap-1 rounded-md p-1  hover:bg-gray-200/50"
        onClick={() => {
          setOpen(!open);
        }}
      >
        <div>Details</div>
        <div className="flex flex-row gap-1">
          {open ? 'Hide' : 'Show'}
          {open ? <ChevronDown /> : <ChevronUp />}
        </div>
      </div>

      {open && (
        <>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex flex-col rounded-xl shadow-sm p-2 items-center ">
              <div>Category</div>
              <div className="text-blue-500">{doc.category}</div>
            </div>
            <div className="flex flex-col rounded-xl shadow-sm p-2 items-center ">
              <div>Format</div>
              <div className="text-blue-500">{doc.available_formats}</div>
            </div>

            <div className="flex flex-col rounded-xl shadow-sm p-2 items-center ">
              <div>Page count</div>
              <div className="text-blue-500">{doc.page_count}</div>
            </div>
            <div className="flex flex-col rounded-xl shadow-sm p-2 items-center ">
              <div>View count</div>
              <div className="text-blue-500">{doc.view_count}</div>
            </div>
          </div>

          <hr className="text-gray-200 my-2" />

          <div>Checksum(original file)</div>
          <div className="flex flex-col pl-2 border-l-2 border-sky-500">
            <div>
              <div className="text-sm">SHA265</div>
              <div className="break-all text-sm text-gray-500 font-normal bg-gray-100/50 p-1 rounded-sm border border-gray-100">
                {doc.sha256sum}
              </div>
            </div>
            <div>
              <div className="text-sm">MD5</div>
              <div className="break-all text-sm text-gray-500 font-normal bg-gray-100/50 p-1 rounded-sm border border-gray-100">
                {doc.md5sum}
              </div>
            </div>
          </div>

          <div>Description</div>
          <pre className="text-sm text-gray-500 font-normal p-1 rounded-sm bg-gray-100/50 border border-gray-100 ">
            {doc.desc}
          </pre>

          <div>Tags</div>
          <div className="flex flex-row flex-wrap gap-1">
            {doc?.tags?.map((tag) => (
              <div className="text-blue-500 bg-blue-200/50 p-1 rounded-md">
                # {tag}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default DocumentMetadata;
