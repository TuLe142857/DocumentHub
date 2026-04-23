import { Outlet } from 'react-router-dom';
import AdminSidebar from '@/layouts/AdminSidebar.jsx';
export default function AdminLayout() {
  return (
    <div className="flex flex-row w-screen h-screen bg-white">
      <AdminSidebar />
      <main className="w-full h-screen overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
