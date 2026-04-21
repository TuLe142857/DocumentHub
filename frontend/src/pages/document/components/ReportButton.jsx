import { useState } from 'react';
import DocumentReportForm from '@/components/forms/DocumentReportForm.jsx';
import Modal from '@/modal/Modal.jsx';
import { BadgeAlert } from 'lucide-react';

const ReportButton = ({ doc }) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Modal isOpen={open} onClose={() => setOpen(false)}>
        <DocumentReportForm
          doc={doc}
          onCancel={() => setOpen(false)}
          className="min-w-100 min-h-100"
        />
      </Modal>
      <button
        className="flex flex-row p-2  rounded-xl bg-white hover:bg-sky-200"
        onClick={() => setOpen(!open)}
      >
        <BadgeAlert />
      </button>
    </>
  );
};

export default ReportButton;
