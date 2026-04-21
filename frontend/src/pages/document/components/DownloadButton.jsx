import { useEffect, useRef, useState } from 'react';
import api from '@/api/api.js';
import { Download } from 'lucide-react';

const DownloadButton = ({ doc }) => {
  const [open, setOpen] = useState(false);
  const modalRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleDownload = async (format = '.pdf') => {
    try {
      const response = await api.get(
        `/documents/${doc.id}/download?format=${encodeURIComponent(format)}`
      );
      const downloadUrl = response.data?.data;
      if (downloadUrl) {
        console.log('Download download', downloadUrl);
        window.open(downloadUrl, '_blank');
      }
    } catch (err) {
      const msg = err.response.data?.message || 'Something went wrong';
      alert(`Can not download document: ${msg}`);
    } finally {
      setOpen(false);
    }
  };
  return (
    <div ref={modalRef} className="relative flex flex-col">
      <button
        className={`flex flex-row p-2  rounded-xl ${open ? 'bg-sky-200' : 'bg-white'} hover:bg-sky-200`}
        onClick={() => setOpen(!open)}
      >
        <Download />
        <div>{doc.download_count}</div>
      </button>
      {open && (
        <div className="absolute left-0 mt-12 flex flex-col rounded-xl bg-white">
          <div className="text-black font-bold p-2 whitespace-nowrap">
            Available format for download
          </div>
          {doc?.available_formats?.map((format) => (
            <div
              className="m-2 p-2 text-black text-lg rounded-xl hover:bg-sky-200"
              key={format}
              onClick={() => handleDownload(format)}
            >
              {format}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DownloadButton;
