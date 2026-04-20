import { useState, useEffect } from 'react';
import authApi from '@/api/authApi.js';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const RegisterPage = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    otp_code: '',
    registration_code: '',
    username: '',
    password: '',
  });

  useEffect(() => {});

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRequestOTP = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const response = await authApi.requestRegister({ email: formData.email });
      console.log(response.data);
      setStep(2);
    } catch (err) {
      setError(
        err?.response?.data?.message || 'Something went wrong, please try again'
      );
      console.log(err?.response?.data?.error_code);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        email: formData.email,
        otp_code: formData.otp_code,
      };
      const response = await authApi.verifyRegister(payload);
      setFormData({
        ...formData,
        registration_code: response.data.data.registration_code,
      });
      setStep(3);
    } catch (err) {
      setError(
        err?.response?.data?.message || 'Something went wrong, please try again'
      );
      console.log(err?.response?.data?.error_code);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteRegistration = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        email: formData.email,
        username: formData.username,
        password: formData.password,
        registration_code: formData.registration_code,
      };
      await authApi.completeRegister(payload);
      toast.success('Register successfully', { autoClose: 2000 });
      setTimeout(() => navigate(`/login?identity=${formData.username}`), 500);
    } catch (err) {
      setError(
        err?.response?.data?.message || 'Something went wrong, please try again'
      );
      console.log(err?.response?.data?.error_code);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="flex items-center justify-center h-screen w-screen bg-sky-100">
      <div className="flex flex-col w-1/2 bg-white shadow-lg rounded-2xl p-10">
        <h1 className="flex  items-center justify-center font-bold">
          Register Account
        </h1>
        {error && <div className="text-red-500">{error}</div>}
        {loading && <div>Loading</div>}
        {step === 1 && (
          <form className="flex flex-col h-full" onSubmit={handleRequestOTP}>
            <div className="font-bold text-lg">Email</div>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="rounded-sm p-2 my-2 bg-gray-100"
            />
            <button
              type="submit"
              className="w-1/3  mt-auto p-2 self-center rounded-lg font-bold text-white bg-sky-400 hover:bg-sky-300"
            >
              {loading ? 'Loading...' : 'Next ->'}
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={handleVerifyOTP} className="flex flex-col h-full">
            <div className="font-bold text-lg">Email</div>
            <div className="rounded-sm p-2 my-2 bg-gray-50">
              {formData.email}
            </div>

            <div>We just send an OTP to your email to verify registration</div>
            <div className="font-bold text-lg">OTP</div>
            <input
              type="text"
              name="otp_code"
              value={formData.otp_code}
              onChange={handleChange}
              className="rounded-sm p-2 my-2 bg-gray-100"
            />
            <button
              type="submit"
              className="w-1/3  mt-auto p-2 self-center rounded-lg font-bold text-white bg-sky-400 hover:bg-sky-300"
            >
              {loading ? 'Loading...' : 'Next ->'}
            </button>
          </form>
        )}

        {step === 3 && (
          <form
            onSubmit={handleCompleteRegistration}
            className="flex flex-col h-full"
          >
            <div className="font-bold text-lg">Email</div>
            <div className="rounded-sm p-2 my-2 bg-gray-50">
              {formData.email}
            </div>

            <div className="font-bold text-lg">Username</div>
            <div className="text-sm text-sky-400">
              Note: After register success, you can login by username or email
            </div>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="rounded-sm p-2 my-2 bg-gray-100"
            />

            <div className="font-bold text-lg">Password</div>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="rounded-sm p-2 my-2 bg-gray-100"
            />
            <button
              type="submit"
              className="w-1/3  mt-auto p-2 self-center rounded-lg font-bold text-white bg-sky-400 hover:bg-sky-300"
            >
              {loading ? 'Loading...' : 'Finish'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default RegisterPage;
