import { useState } from 'react';
import useModal from '@/modal/useModal.jsx';
import AddDocumentToCollectionForm from '@/components/forms/AddDocumentToCollectionForm.jsx';
import { Bookmark } from 'lucide-react';
const AddToCollectionButton = ({ doc }) => {
  const { openModal, closeModal } = useModal();
  return (
    <div className="relative flex flex-col">
      <button
        className=" flex flex-row p-2 rounded-xl bg-white hover:bg-sky-200"
        onClick={() =>
          openModal(
            <AddDocumentToCollectionForm
              doc={doc}
              onExit={() => closeModal()}
            />
          )
        }
      >
        <Bookmark />
      </button>
    </div>
  );
};
export default AddToCollectionButton;
