import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
// import api from '@/api/api.js';
import { fetchUserInfo } from '@/store/slice/userSlice.jsx';
import Loading from '@/components/Loading.jsx';
import AppRoutes from '@/routes/AppRoutes.jsx';
import ConnectionErrorPage from '@/pages/errors/ConnectionErrorPage.jsx';

export default function App() {
  // const [isLoading, setIsLoading] = useState(true);
  // const [connected, setConnected] = useState(false);
  const dispatch = useDispatch();
  const { isLoading } = useSelector((state) => state.user);

  // useEffect(() => {
  //   console.log("Use Effect 1")
  //   const ping = async () => {
  //     try {
  //       setIsLoading(true);
  //       await api.get('http://localhost:8000/health');
  //       setConnected(true);
  //     } catch {
  //       setConnected(false);
  //     } finally {
  //       setIsLoading(false);
  //     }
  //   };
  //   ping();
  // }, []);

  useEffect(() => {
    console.log('Use Effect fetch redux user stored');
    // alert("fetch user from app.jsx")
    dispatch(fetchUserInfo());
  }, [dispatch]);

  if (isLoading) {
    return <Loading />;
  }

  // if (!connected) {
  //   return <ConnectionErrorPage />;
  // }

  return <AppRoutes />;
}
