import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import api from '@/api/api.js';
import Loading from '@/components/Loading.jsx';
import DownloadButton from '@/pages/document/components/DownloadButton.jsx';
import LikeButton from '@/pages/document/components/LikeButton.jsx';
import AddToCollectionButton from '@/pages/document/components/AddToCollectionButton.jsx';
import ReportButton from '@/pages/document/components/ReportButton.jsx';
import EditButton from '@/pages/document/components/EditButton.jsx';

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
                currentUser.username === doc.owner && (
                  <EditButton doc={doc} onChange={setDoc} />
                )}
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
