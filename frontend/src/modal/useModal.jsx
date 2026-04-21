import { useContext } from 'react';
import { ModalContext } from '@/modal/ModalProvider.jsx';

const useModal = () => {
  return useContext(ModalContext);
};

export default useModal;
