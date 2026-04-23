import { useParams } from 'react-router-dom';
import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api.js';

import Loading from '@/components/Loading.jsx';
import DocumentMetadata from '@/pages/document/components/DocumentMetadata.jsx';
import DocumentAction from '@/pages/document/components/DocumentAction.jsx';
import DocumentCard from '@/components/DocumentCard.jsx';

const DocumentDetailPage = () => {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);
  const [similarDocs, setSimilarDocs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDoc = useCallback(async () => {
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
  }, [id]);

  const fetchSimilarDocs = useCallback(async () => {
    if (!doc) return;
    try {
      const params = new URLSearchParams();
      params.set('page', '1');
      params.set('limit', '10');
      doc?.tags?.forEach((tag) => {
        params.append('tags', tag);
      });
      const response = await api.get(`/search`, { params: params });
      const docs = response.data?.data;
      setSimilarDocs(docs.filter((d) => d.id !== doc.id));
    } catch (err) {
      console.log('err fetch similar', err);
    }
  }, [doc]);

  useEffect(() => {
    fetchDoc();
  }, [fetchDoc]);

  useEffect(() => {
    fetchSimilarDocs();
  }, [fetchSimilarDocs]);

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="flex flex-col  sm:flex-row flex-1 min-h-screen  overflow-y-auto gap-2 p-2 bg-gray-100 ">
      {/*
        DOCUMENT
      */}
      <div className="flex flex-col flex-1 min-h-0 h-fit gap-1 bg-white p-1 rounded-xl ">
        <div className="flex flex-row p-2 rounded-sm justify-between gap-1">
          <div className="flex font-bold gap-1 flex-col">
            <div className="text-2xl">{doc.title}</div>
            <div className="text-sm">
              Post by
              <a className="text-blue-500" href={`/users/${doc.owner}`}>
                {' '}
                {doc.owner}
              </a>
            </div>
          </div>
          <DocumentAction
            doc={doc}
            onChange={setDoc}
            className="items-center gap-2"
          />
        </div>

        <DocumentMetadata
          doc={doc}
          className="rounded-md bg-white shadow-sm p-2"
        />

        <iframe src={doc.file_preview_url} className="h-150  w-full"></iframe>
      </div>

      {/*
        RECOMMEND SIMILAR
      */}
      <div className="flex flex-col items-center bg-white gap-1  rounded-xl p-2 ">
        <div className="text-xl font-bold text-black p-2">Similar Document</div>
        {similarDocs &&
          similarDocs.map((doc) => (
            <DocumentCard document={doc} key={doc.id} />
          ))}
      </div>
    </div>
  );
};
export default DocumentDetailPage;
