import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Bounce, ToastContainer } from 'react-toastify';

import { fetchUserInfo } from '@/store/slice/userSlice.jsx';
import Loading from '@/components/Loading.jsx';
import AppRoutes from '@/routes/AppRoutes.jsx';

export default function App() {
  const dispatch = useDispatch();
  const { isLoading } = useSelector((state) => state.user);

  useEffect(() => {
    console.log('Fetch current user information and set into Redux');
    dispatch(fetchUserInfo());
  }, [dispatch]);

  return (
    <>
      <ToastContainer
        position="top-center"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick={false}
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        transition={Bounce}
        style={{ zIndex: 10000 }}
      />
      {isLoading ? <Loading /> : <AppRoutes />}
    </>
  );
}
