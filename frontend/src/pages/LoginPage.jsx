import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { fetchUserInfo } from '@/store/slice/userSlice.jsx';
import api from '@/api/api.js';

const LoginPage = () => {
  const dispatch = useDispatch(); // redux
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [loginData, setLoginData] = useState({
    identity: searchParams.get('identity'),
    password: searchParams.get('password'),
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setLoginData({ ...loginData, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post('/auth/login', loginData);

      // fetch user data to redux
      dispatch(fetchUserInfo());
      alert('Login successfully');
      navigate('/');
    } catch (err) {
      setError(err.response.data?.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen bg-sky-100">
      <div className="flex flex-col items-center justify-center p-5 bg-white rounded-xl">
        <div className="font-bold text-xl">Login</div>
        {error && <div className="text-red-500">{error}</div>}
        <form onSubmit={handleLogin} className="flex flex-col h-full">
          <input
            type="text"
            name="identity"
            value={loginData.identity}
            onChange={handleChange}
            placeholder="Email or Username"
            className="rounded-sm p-2 my-2 bg-gray-100"
          />

          <div className="flex flex-row h-full gap-2">
            <input
              type={showPassword ? 'text' : 'password'}
              name="password"
              value={loginData.password}
              onChange={handleChange}
              placeholder="Password"
              className="rounded-sm p-2 my-2 bg-gray-100"
            />

            <button
              className="bg-sky-100 rounded-sm my-2 p-2"
              type="button"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
          </div>

          <div
            className="flex flex-col text-right font-bold text-blue-500 px-2 m-2 hover:cursor-pointer hover:text-blue-700"
            onClick={() => navigate('/forgot-password')}
          >
            Forgot password
          </div>

          <button
            type="submit"
            className="bg-sky-300 w-full rounded-sm font-bold p-2 text-white hover:bg-sky-400"
          >
            {loading ? 'Loading....' : 'Login'}
          </button>
        </form>

        <div className="flex flex-row items-center justify-center p-5 gap-1 bg-white rounded-xl">
          <span>Dont have an account?</span>

          <span
            className="font-bold text-blue-500 hover:cursor-pointer hover:text-blue-700"
            onClick={() => navigate('/register')}
          >
            Sign up here
          </span>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
