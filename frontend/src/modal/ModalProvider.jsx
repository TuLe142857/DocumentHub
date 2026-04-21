import { createContext, useState, useEffect } from 'react';
import Modal from '@/modal/Modal.jsx';

export const ModalContext = createContext(null);
const ModalProvider = ({ children }) => {
  const [modalContent, setModalContent] = useState(null);

  const openModal = (content) => {
    setModalContent(content);
  };
  const closeModal = () => {
    setModalContent(null);
  };

  return (
    <ModalContext.Provider value={{ openModal, closeModal }}>
      {children}
      <Modal
        isOpen={modalContent !== null}
        onClose={closeModal}
        children={modalContent}
      />
    </ModalContext.Provider>
  );
};

export default ModalProvider;
