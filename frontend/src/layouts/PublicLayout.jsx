import { Outlet } from 'react-router-dom';
import Header from '@/layouts/Header.jsx';
import Footer from '@/layouts/Footer.jsx';
export default function PublicLayout() {
  return (
    <div className="flex flex-col w-screen min-h-screen bg-white">
      <Header />

      <main className="flex flex-1 w-full h-full">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}
