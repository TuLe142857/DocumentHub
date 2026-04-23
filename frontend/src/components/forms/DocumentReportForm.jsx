import { useState, useEffect } from 'react';
import api from '@/api/api.js';
import { toast } from 'react-toastify';
import { BadgeAlert as ReportIcon, X as ExitIcon } from 'lucide-react';
/**
 * @import {Document} from '@/types/document,jsx'
 * @param {Document} doc
 * @param onCancel
 * @param onSuccess
 * @returns {React.JSX.Element}
 * @constructor
 */
const DocumentReportForm = ({ doc, onCancel, onSuccess, className }) => {
  const [reportReasons, setReasons] = useState([]);

  const [data, setData] = useState({
    reason: null,
    desc: '',
  });

  const fetchReportReason = async () => {
    try {
      const response = await api.get(`/reports/available_reasons`);
      setReasons(response.data.data);
    } catch (err) {
      toast.error(
        err?.response?.data?.message ||
          'Something went wrong, please try again later'
      );
    }
  };
  useEffect(() => {
    fetchReportReason();
  });

  const onChange = (e) => {
    e?.preventDefault();
    setData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleReport = async () => {
    if (!data.reason) {
      toast.warn('Please select report reason');
      return;
    }
    const toast_id = toast.loading('Reporting...');
    try {
      await api.post(`/reports/documents/${doc.id}`, data);
      toast.update(toast_id, {
        type: 'success',
        render: 'Report Successful',
        isLoading: false,
        autoClose: 2000,
      });
      onSuccess && onSuccess();
      onCancel && onCancel();
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err.message ||
        'Something went wrong, please try again';
      toast.update(toast_id, {
        type: 'error',
        render: msg,
        isLoading: false,
        autoClose: 2000,
      });
    }
  };
  return (
    <div
      className={`relative flex flex-col gap-2 bg-white rounded-xl ${className}`}
    >
      <button
        className="absolute top-1 right-1 p-2 rounded-full text-red-400 hover:bg-red-300/50 hover:text-red-500"
        onClick={() => onCancel()}
      >
        <ExitIcon />
      </button>

      <div className="justify-center flex w-full rounded-t-xl py-3 self-center text-xl text-red-500 bg-red-200/50 gap-2 font-bold">
        <ReportIcon />
        <div>Report</div>
      </div>

      <div className="flex flex-col gap-2 p-2">
        <div className="text-black font-bold">
          <span>Please select the reason belows </span>
          <span className="text-red-500">*</span>
        </div>
        <select
          name="reason"
          value={data.reason}
          onChange={onChange}
          className="rounded-sm p-2 border border-gray-300 focus:outline-sky-500"
        >
          {data?.reason || <option>--</option>}
          {reportReasons?.map((reason) => (
            <option key={reason.id} value={reason.id}>
              {reason.code}
            </option>
          ))}
        </select>

        <div className="text-black font-bold">Why do you want to report?</div>
        <textarea
          name="desc"
          value={data.desc}
          onChange={onChange}
          rows={3}
          className="rounded-sm p-2 border border-gray-300 focus:outline-sky-500"
        />

        <div className="self-end mr-5 flex flex-row gap-2 text-lg font-semibold">
          <button
            onClick={() => onCancel()}
            className="rounded-md p-2 0 text-gray-600 hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={() => handleReport()}
            className="rounded-md p-2 bg-red-500 text-white"
          >
            Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentReportForm;
