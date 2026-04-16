import { Routes, Route } from 'react-router-dom';
import PublicLayout from '@/layouts/PublicLayout.jsx';
import AdminLayout from '@/layouts/AdminLayout.jsx';
import NotFoundPage from '@/pages/errors/NotFoundPage.jsx';
import ProtectedRoute from '@/routes/ProtectedRoute.jsx';
import HomePage from '@/pages/HomePage.jsx';
import LoginPage from '@/pages/LoginPage.jsx';
import RegisterPage from '@/pages/RegisterPage.jsx';
import ForgotPasswordPage from '@/pages/ForgotPasswordPage.jsx';
import UploadDocumentPage from '@/pages/UploadDocumentPage.jsx';
import DocumentDetailPage from '@/pages/DocumentDetailPage.jsx';
import SearchPage from '@/pages/SearchPage.jsx';
import UserProfilePage from '@/pages/user_profile/UserProfilePage.jsx';
import CollectionPage from '@/pages/CollectionPage.jsx';

const AppRoutes = () => {
  return (
    <Routes>
      {/*
          PUBLIC PAGES
          - Allow both users & guest
      */}
      <Route path="login" element={<LoginPage />} />
      <Route path="register" element={<RegisterPage />} />
      <Route path="forgot-password" element={<ForgotPasswordPage />} />
      <Route path="users/:username" element={<UserProfilePage />} />
      {/*
          USER PAGES
          - Required login
          - When not login, redirect to login page
      */}

      <Route element={<ProtectedRoute allowedRoles={['USER']} />}></Route>

      <Route element={<PublicLayout />}>
        <Route index={true} element={<HomePage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="documents/:id" element={<DocumentDetailPage />} />

        <Route element={<ProtectedRoute allowedRoles={['USER']} />}>
          <Route path="upload" element={<UploadDocumentPage />} />
          <Route path="collections/:id" element={<CollectionPage />} />
        </Route>
      </Route>

      {/*
          ADMIN PAGES
          - For admin only
          - When not login, redirect to login page
          - When login but is not admin, return forbidden page
      */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminLayout />
          </ProtectedRoute>
        }
      ></Route>

      {/*
          ON NOT FOUND PAGE
      */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes;
