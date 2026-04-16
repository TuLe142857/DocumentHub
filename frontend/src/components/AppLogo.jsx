import { BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';
const AppLogo = ({ className = '', alwaysFull = false }) => {
  return (
    <Link
      to="/"
      className={`flex flex-row items-center gap-2 hover:cursor-pointer ${className}`}
    >
      <BookOpen size={48} className="p-2 text-white bg-blue-500 rounded-xl" />
      <div
        className={`${alwaysFull ? 'flex' : 'hidden sm:flex '}
        flex-row text-xl text-center font-bold`}
      >
        <span className="textblack">Document</span>
        <span className="text-blue-500">Hub</span>
      </div>
    </Link>
  );
};
export default AppLogo;
