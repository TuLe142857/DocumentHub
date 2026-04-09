import { Outlet, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Loading from '@/components/Loading.jsx';
import ForbiddenPage from '@/pages/ForbiddenPage.jsx';

export default function ProtectedRoute({ allowedRoles }) {
  const { user, isLoading, isAuthenticated } = useSelector(
    (state) => state.user
  );

  if (isLoading) {
    return <Loading />;
  }

  if (!isAuthenticated) {
    return <Navigate to={'/login'} />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <ForbiddenPage />;
  }

  return <Outlet />;
}
