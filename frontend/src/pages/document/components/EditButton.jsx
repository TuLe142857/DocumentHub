import useModal from '@/modal/useModal.jsx';
import DocumentEditForm from '@/components/forms/DocumentEditForm.jsx';
import { Pencil } from 'lucide-react';

const EditButton = ({ doc, onChange }) => {
  const { openModal, closeModal } = useModal();
  return (
    <button
      className="flex flex-row p-2  rounded-xl bg-white hover:bg-sky-200"
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

export default EditButton;
