import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Grid3x3,
  TriangleAlert,
  FileX,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

const AdminDashboard = () => {
  const navigate = useNavigate();

  const adminModules = [
    {
      title: 'Quản lý Người dùng',
      description: 'Xem và quản lý tài khoản người dùng trong hệ thống.',
      icon: <Users className="w-8 h-8 text-blue-500" />,
      path: '/admin/users',
      bgColor: 'bg-blue-50',
      hoverColor: 'hover:border-blue-300 hover:shadow-blue-100',
    },
    {
      title: 'Quản lý Danh mục',
      description: 'Tạo và chỉnh sửa các chuyên mục để phân loại tài liệu.',
      icon: <Grid3x3 className="w-8 h-8 text-indigo-500" />,
      path: '/admin/categories',
      bgColor: 'bg-indigo-50',
      hoverColor: 'hover:border-indigo-300 hover:shadow-indigo-100',
    },
    {
      title: 'Báo cáo Vi phạm',
      description: 'Kiểm duyệt và xử lý các báo cáo về tài liệu không hợp lệ.',
      icon: <TriangleAlert className="w-8 h-8 text-amber-500" />,
      path: '/admin/reports',
      bgColor: 'bg-amber-50',
      hoverColor: 'hover:border-amber-300 hover:shadow-amber-100',
    },
    {
      title: 'Quản lý Tài liệu',
      description: 'Xem danh sách tài liệu',
      icon: <FileX className="w-8 h-8 text-emerald-500" />,
      path: '/admin/documents',
      bgColor: 'bg-emerald-50',
      hoverColor: 'hover:border-emerald-300 hover:shadow-emerald-100',
    },
  ];

  return (
    <div className="min-h-full p-8 lg:p-12 bg-white flex flex-col justify-center">
      <div className="max-w-5xl mx-auto w-full">
        {/* Welcome Section */}
        <div className="flex flex-col items-center text-center mb-16 relative">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-100 rounded-full blur-[100px] opacity-70 pointer-events-none"></div>

          <div className="relative z-10 w-20 h-20 bg-white rounded-2xl shadow-xl shadow-blue-100 flex items-center justify-center mb-6 transform rotate-3 hover:rotate-0 transition-transform duration-300">
            <ShieldCheck className="w-10 h-10 text-blue-600" />
          </div>
          <h1 className="relative z-10 text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
            Trung tâm Quản trị <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">DocumentHub</span>
          </h1>
          <p className="relative z-10 text-lg text-slate-500 max-w-2xl">
            Chào mừng bạn đến với không gian quản trị. Tại đây, bạn có toàn quyền kiểm soát hệ thống,
            quản lý nội dung và đảm bảo nền tảng hoạt động ổn định.
          </p>
        </div>

        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
          {adminModules.map((module, index) => (
            <div
              key={index}
              onClick={() => navigate(module.path)}
              className={`group bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm cursor-pointer transition-all duration-300 transform hover:-translate-y-1 hover:shadow-xl ${module.hoverColor}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${module.bgColor} transition-transform duration-300 group-hover:scale-110`}>
                  {module.icon}
                </div>
                <div className="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-white group-hover:shadow-sm transition-all duration-300">
                  <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-slate-800 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2 group-hover:text-slate-900 transition-colors">
                {module.title}
              </h3>
              <p className="text-slate-500 leading-relaxed">
                {module.description}
              </p>
            </div>
          ))}
        </div>

        {/* Footer info */}
        <div className="mt-16 text-center text-slate-400 text-sm">
          <p>DocumentHub Admin Portal &copy; {new Date().getFullYear()}</p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
