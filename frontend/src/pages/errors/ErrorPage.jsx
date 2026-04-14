const ErrorPage = ({ message = '' }) => {
  return (
    <div className="flex h-screen w-full items-center justify-center text-red-500 font-bold text-xl">
      Error {message ? `: ${message}` : ''}
    </div>
  );
};

export default ErrorPage;
