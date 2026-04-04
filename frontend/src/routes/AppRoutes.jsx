import { Routes, Route } from 'react-router-dom';
import PublicLayout from '@/layouts/PublicLayout.jsx';
import AdminLayout from '@/layouts/AdminLayout.jsx';
import NotFound from '@/pages/NotFound.jsx';
import ProtectedRoute from '@/routes/ProtectedRoute.jsx';
import Home from '@/pages/Home.jsx';
import Login from '@/pages/Login.jsx';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="login" element={<Login />} />

      <Route element={<PublicLayout />}>
        <Route index={true} element={<Home />} />
      </Route>

      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminLayout />
          </ProtectedRoute>
        }
      ></Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default AppRoutes;
