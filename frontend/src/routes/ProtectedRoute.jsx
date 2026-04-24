import { Outlet, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Loading from '@/components/Loading.jsx';
import ForbiddenPage from '@/pages/errors/ForbiddenPage.jsx';

/**
 *
 * @param {Object} props
 * @param {Array<string>} props.allowedRoles
 * @param {string|null} props.defaultRedirect
 * @param {Map<string, string>| null} props.roleRedirect
 * @return {React.JSX.Element}
 * @constructor
 */
export default function ProtectedRoute({
  allowedRoles,
  defaultRedirect = null,
  roleRedirect = null,
}) {
  const { user, isLoading } = useSelector((state) => state.user);

  const role = user?.role || 'GUEST';

  if (isLoading) {
    return <Loading />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    if (roleRedirect instanceof Map && roleRedirect.has(role)) {
      return <Navigate to={roleRedirect.get(role)} replace />;
    } else if (defaultRedirect) {
      return <Navigate to={defaultRedirect} replace />;
    } else {
      return <ForbiddenPage />;
    }
  }

  return <Outlet />;
}
