import { useState, useEffect, useCallback } from 'react';
import adminApi from '@/api/adminApi.js';
import { X as ExitIcon, BadgeAlert as ReportIcon } from 'lucide-react';
import usePagination from '@/hooks/usePagination.jsx';

import DocumentMetadata from '@/pages/document/components/DocumentMetadata.jsx';
import { toast } from 'react-toastify';

const DocumentView = ({ doc }) => {
  const [showPreview, setShowPreview] = useState(false);

  return (
    <div className="flex flex-col">
      <div className="text-2xl font-bold">{doc.title}</div>
      <div className="text-sm text-gray-500 font-semibold">{`Post by ${doc.owner}`}</div>

      <DocumentMetadata doc={doc} />
      <button
        className="w-fit self-center rounded-sm p-2 text-green-500 bg-green-100/50 border border-green-500 hover:bg-green-200/50"
        onClick={() => setShowPreview(!showPreview)}
      >
        {showPreview ? 'Hide Preview' : 'Show Preview'}
      </button>
      {showPreview && (
        <iframe
          src={doc?.file_preview_url}
          className="w-full h-100 rounded-xl"
        />
      )}
    </div>
  );
};

const ReportDetails = ({ docId, onExit, onHandled, classname = '' }) => {
  const [doc, setDoc] = useState();
  const [reports, setReports] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);

  const fetchDoc = useCallback(async () => {
    try {
      const response = await adminApi.getDocumentDetails(docId);
      setDoc(response.data.data);
    } catch (err) {
      console.log('err fetch doc', err);
    }
  }, [docId]);

  const fetchReports = useCallback(async () => {
    try {
      const response = await adminApi.getReportedDocumentDetails(docId, {
        page: page,
        limit: 1,
      });
      const meta = response.data.meta;
      setHasNext(meta.has_next);
      setReports((prev) => [...prev, ...response.data.data]);
    } catch (err) {
      console.log('err fetch reports', err);
    }
  }, [docId, page]);

  const handleReport = async (accept) => {
    if (!confirm(`${accept ? 'Accept' : 'Reject'} this reports?`)) {
      return;
    }

    const reason = prompt('Enter reason');
    if (!reason) return;

    const toastId = toast.loading('Loading...');
    try {
      await adminApi.handleReportedDocument(docId, accept, '');
      toast.update(toastId, {
        type: 'success',
        render: 'Sucessful!',
        isLoading: false,
        autoClose: 500,
      });
      onHandled && onHandled();
      onExit && onExit();
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        'Something went wrong, please try again later';
      toast.update(toastId, {
        type: 'error',
        render: msg,
        isLoading: false,
        autoClose: 500,
      });
    }
  };

  useEffect(() => {
    fetchDoc();
    fetchReports();
  }, [fetchDoc, fetchReports]);

  return (
    <div className={`relative flex flex-col ${classname}`}>
      {/*Header*/}
      <button
        className="absolute top-1 right-1 p-2 rounded-full text-gray-500 hover:bg-gray-300/50"
        onClick={onExit}
      >
        <ExitIcon />
      </button>
      <div className="flex flex-row justify-center items-center gap-2 p-2 bg-red-200/50">
        <ReportIcon className={'text-red-500'} size={32} />
        <div className="text-black font-semibold text-xl">Reports</div>
      </div>

      {/*Content*/}
      <div className="flex flex-col flex-1 p-2 gap-2 w-full min-h-0 overflow-auto">
        {doc && <DocumentView doc={doc} />}

        <div>Report list:</div>
        <div className="flex flex-col p-2 gap-2 w-full max-h-100 shrink-0 overflow-auto rounded-sm bg-white shadow border border-gray-200">
          {reports &&
            reports.map((report) => (
              <div
                key={report.id}
                className="flex flex-col text-md rounded-sm p-2 bg-gray-100"
              >
                <div className="text-red-500 font-semibold">
                  {report.report_reason}
                </div>
                <div className="text-gray-700 text-xs">{report.created_at}</div>
                <div className="text-gray-700">{report.desc}</div>
              </div>
            ))}

          {hasNext && (
            <button className="" onClick={() => setPage(page + 1)}>
              Load more..
            </button>
          )}
        </div>
      </div>

      <hr className="my-1 text-gray-300" />
      {/*Footer*/}
      <div className="flex flex-row p-2 gap-2 justify-end items-center">
        <button
          className="p-2  rounded-md text-md font-semibold text-white bg-red-500 border border-red-300 hover:bg-red-700"
          onClick={() => handleReport(true)}
        >
          Accept reports
        </button>

        <button
          className="p-2  rounded-md text-md font-semibold text-gray-700 border border-gray-300 hover:bg-gray-100"
          onClick={() => handleReport(false)}
        >
          Reject Report
        </button>
      </div>
    </div>
  );
};

export default ReportDetails;
