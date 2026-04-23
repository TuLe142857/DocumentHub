import { useEffect, useRef, useState } from 'react';
import { useSelector } from 'react-redux';

import { BadgeAlert, Bookmark, Download, Pencil, ThumbsUp } from 'lucide-react';

import api from '@/api/api.js';
import useModal from '@/modal/useModal.jsx';
import DocumentEditForm from '@/components/forms/DocumentEditForm.jsx';
import Modal from '@/modal/Modal.jsx';
import DocumentReportForm from '@/components/forms/DocumentReportForm.jsx';

import AddDocumentToCollectionForm from '@/components/forms/AddDocumentToCollectionForm.jsx';

const DownloadButton = ({ doc, className = '' }) => {
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
        className={`flex flex-row ${className}`}
        onClick={() => setOpen(!open)}
      >
        <Download />
        <div>{doc.download_count}</div>
      </button>
      {open && (
        <div className="absolute z-100 left-0 mt-12 flex flex-col border border-gray-100 shadow-sm rounded-xl bg-white">
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

const EditButton = ({ doc, onChange, className = '' }) => {
  const { openModal, closeModal } = useModal();
  return (
    <button
      className={`flex flex-row ${className}`}
      onClick={() =>
        openModal(
          <DocumentEditForm
            doc={doc}
            onUpdate={onChange}
            onCancel={() => closeModal()}
          />
        )
      }
    >
      <Pencil />
    </button>
  );
};

const LikeButton = ({ doc, onUpdate, className = '' }) => {
  const handleLike = async () => {
    try {
      if (doc.liked) {
        await api.delete(`/documents/${doc.id}/like`);
      } else {
        await api.put(`/documents/${doc.id}/like`);
      }
      onUpdate((prevState) => ({
        ...prevState,
        liked: !doc.liked,
        like_count: prevState.like_count + (doc.liked ? -1 : 1),
      }));
    } catch (err) {
      const msg = err.response.data?.message || 'Something went wrong';
      alert(`Can not ${doc.liked ? 'unlike ' : ''}like document: ${msg}`);
    }
  };
  return (
    <button className={`flex flex-row ${className}`} onClick={handleLike}>
      <ThumbsUp fill={doc?.liked ? 'black' : 'white'} />
      <div>{doc?.like_count}</div>
    </button>
  );
};

const ReportButton = ({ doc, className = '' }) => {
  const { openModal, closeModal } = useModal();
  return (
    <button
      className={`flex flex-row ${className}`}
      onClick={() =>
        openModal(
          <DocumentReportForm
            doc={doc}
            onCancel={() => closeModal()}
            className="min-w-100 min-h-100"
          />
        )
      }
    >
      <BadgeAlert />
    </button>
  );
};

const AddToCollectionButton = ({ doc, className = '' }) => {
  const { openModal, closeModal } = useModal();
  return (
    <button
      className={`flex flex-row ${className}`}
      onClick={() =>
        openModal(
          <AddDocumentToCollectionForm doc={doc} onExit={() => closeModal()} />
        )
      }
    >
      <Bookmark />
    </button>
  );
};

const DocumentAction = ({ doc, onChange, className = '' }) => {
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );

  const buttonClassName =
    'p-2.5 rounded-xl border border-blue-100 bg-sky-100/50 hover:bg-sky-200';
  return (
    <div className={`flex flex-row ${className}`}>
      <DownloadButton doc={doc} className={buttonClassName} />
      <LikeButton doc={doc} onUpdate={onChange} className={buttonClassName} />
      {isAuthenticated && (
        <>
          <AddToCollectionButton doc={doc} className={buttonClassName} />
          <ReportButton doc={doc} className={buttonClassName} />
          {doc.owner === currentUser.username && (
            <EditButton
              doc={doc}
              onChange={onChange}
              className={buttonClassName}
            />
          )}
        </>
      )}
    </div>
  );
};

export default DocumentAction;
