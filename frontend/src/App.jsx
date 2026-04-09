import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import api from '@/api/api.js';
import { fetchUserInfo } from '@/store/slice/userSlice.jsx';
import Loading from '@/components/Loading.jsx';
import AppRoutes from '@/routes/AppRoutes.jsx';
import ConnectionErrorPage from '@/pages/ConnectionErrorPage.jsx';

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const dispatch = useDispatch();

  useEffect(() => {
    const ping = async () => {
      try {
        setIsLoading(true);
        await api.get('http://localhost:8000/health');
        setConnected(true);
      } catch {
        setConnected(false);
      } finally {
        setIsLoading(false);
      }
    };
    ping();
  }, []);

  useEffect(() => {
    dispatch(fetchUserInfo());
  }, [dispatch]);

  if (isLoading) {
    return <Loading />;
  }

  if (!connected) {
    return <ConnectionErrorPage />;
  }

  return <AppRoutes />;
}
