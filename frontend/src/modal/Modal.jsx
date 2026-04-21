import { createPortal } from 'react-dom';
import { useEffect, useRef } from 'react';
const Modal = ({ isOpen, onClose, children, background = 'bg-black/50' }) => {
  const childrenRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (e.target.closest('.Toastify__toast')) return;
      if (childrenRef.current && !childrenRef.current.contains(e.target)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;
  return createPortal(
    <div
      className={`fixed top-0 left-0 z-9999 flex items-center justify-center  w-screen h-screen ${background}`}
    >
      <div
        ref={childrenRef}
        // className="flex items-center justify-center w-full h-full"
      >
        {children}
      </div>
    </div>,
    document.body
  );
};

export default Modal;
