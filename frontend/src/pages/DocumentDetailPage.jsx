import { useParams } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import {
  ThumbsUp,
  BadgeAlert,
  Download,
  Bookmark,
  Trash2,
  Pencil,
  Tag,
} from 'lucide-react';

import api from '@/api/api.js';
import Loading from '@/components/Loading';

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

const LikeButton = ({ doc, onUpdate }) => {
  const handleLike = async () => {
    try {
      const api_url = `/documents/${doc.id}/like`;
      if (doc.liked) {
        await api.delete(api_url);
      } else {
        await api.post(api_url);
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
    <div>
      <button
        className="flex flex-row p-2  rounded-xl bg-white hover:bg-sky-200"
        onClick={handleLike}
      >
        <ThumbsUp fill={doc?.liked ? '#27CFF5' : 'white'} />
        <div>{doc?.like_count}</div>
      </button>
    </div>
  );
};

const AddToCollectionButton = ({ doc }) => {
  const handleClick = () => {
    alert('Coming soon....');
  };
  return (
    <div>
      <button
        className="flex flex-row p-2  rounded-xl bg-white hover:bg-sky-200"
        onClick={handleClick}
      >
        <Bookmark />
      </button>
    </div>
  );
};

const ReportButton = ({ doc }) => {
  const handleClick = () => {
    alert('Coming soon....');
  };
  return (
    <div>
      <button
        className="flex flex-row p-2  rounded-xl bg-white hover:bg-sky-200"
        onClick={handleClick}
      >
        <BadgeAlert />
      </button>
    </div>
  );
};

const EditButton = ({ onClick }) => {
  return (
    <button
      className="flex flex-row p-2  rounded-xl bg-white hover:bg-sky-200"
      onClick={onClick}
    >
      <Pencil />
    </button>
  );
};

const DocumentDetailPage = () => {
  const { id } = useParams();
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );
  const [doc, setDoc] = useState(null);
  const [showDesc, setShowDesc] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setError(null);
      setLoading(true);
      try {
        const response = await api.get(`/documents/${id}`);
        setDoc(response.data?.data);
        console.log('document', response.data?.data);
      } catch (err) {
        setError(err.response.data?.message || err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="flex flex-row flex-1 bg-gray-100">
      {/*
        DOCUMENT DETAILS
      */}
      <div className="flex flex-col w-2/3 p-2">
        {/* INFO BAR */}
        <div>
          <div className="flex flex-row p-2 rounded-sm justify-between gap-1 bg-sky-100 ">
            <div className="flex text-lg font-bold  flex-col">
              <div>{doc.title}</div>
              <div className="text-sm">
                Post by
                <a href={`/users/${doc.owner}`}>{doc.owner}</a>
              </div>
            </div>
            <div className="flex flex-row items-center gap-2">
              <DownloadButton doc={doc} />
              <LikeButton doc={doc} onUpdate={setDoc} />
              <AddToCollectionButton doc={doc} />
              <ReportButton doc={doc} />
              {isAuthenticated &&
                currentUser &&
                currentUser.username === doc.owner && <EditButton />}
            </div>
          </div>

          <div className="flex flex-wrap">
            {doc &&
              doc?.tags?.map((tag) => (
                <div className="text-sm text-blue-500 font-semibold m-1 p-2 bg-sky-200/50 rounded-2xl">
                  #{tag}
                </div>
              ))}
          </div>
          {/*DESC*/}
          <div className="flex flex-row gap-x-1">
            <div>Description </div>
            {doc.desc ? (
              <div onClick={() => setShowDesc(!showDesc)}>
                {showDesc ? 'hide' : 'show'}
              </div>
            ) : (
              <div>No description</div>
            )}
          </div>
          {showDesc && <div>{doc.desc}</div>}
        </div>

        {/* PREVIEW */}
        <iframe
          src={doc.file_preview_url}
          className="flex h-screen flex-1"
        ></iframe>
      </div>

      {/*
        RECOMMEND SIMILAR
      */}
      <div className="flex flex-col flex-1 bg-green-200">
        <div className="text-xl font-bold text-black p-2">Similar Document</div>
      </div>
    </div>
  );
};
export default DocumentDetailPage;
