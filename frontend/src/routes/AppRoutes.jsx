import { Routes, Route } from 'react-router-dom';
import PublicLayout from '@/layouts/PublicLayout.jsx';
import AdminLayout from '@/layouts/AdminLayout.jsx';
import NotFoundPage from '@/pages/NotFoundPage.jsx';
import ProtectedRoute from '@/routes/ProtectedRoute.jsx';
import HomePage from '@/pages/HomePage.jsx';
import LoginPage from '@/pages/LoginPage.jsx';
import RegisterPage from '@/pages/RegisterPage.jsx'
import ForgotPasswordPage from "@/pages/ForgotPasswordPage.jsx";

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="login" element={<LoginPage />} />
      <Route path="register" element={<RegisterPage />}/>
      <Route path="forgot-password" element={<ForgotPasswordPage />}/>
      <Route element={<PublicLayout />}>
        <Route index={true} element={<HomePage />} />
      </Route>

      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminLayout />
          </ProtectedRoute>
        }
      ></Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes;
