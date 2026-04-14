import { useNavigate } from 'react-router-dom';
export default function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center justify-center h-screen text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p>Not found</p>
      <button
        onClick={() => navigate('/')}
        className="rounded-xl font-bold text-white bg-sky-300 p-2"
      >
        Back to Home
      </button>
    </div>
  );
}
