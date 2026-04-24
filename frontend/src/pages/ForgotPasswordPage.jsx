import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authApi from '@/api/authApi.js';
import AppLogo from '@/components/AppLogo.jsx';
import { toast } from 'react-toastify';

const ForgotPasswordPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    identity: '',
    otp_code: '',
    new_password: '',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    e.preventDefault();
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRequestOTP = async (e) => {
    e.preventDefault();
    try {
      await authApi.forgotPassword(formData.identity);
      setStep(2);
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        'Something went wrong please try again.';
      toast.error(msg);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    try {
      await authApi.resetPassword(
        formData.identity,
        formData.otp_code,
        formData.new_password
      );
      toast.success('Password reset successfully.');
      setTimeout(() => {
        navigate(`/login?identity=${formData.identity}`);
      }, 500);
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        'Something went wrong please try again.';
      toast.error(msg);
    }
  };

  return (
    <div className="flex items-center justify-center w-screen h-screen bg-sky-100">
      <div className="flex flex-col p-5 gap-1 rounded-lg shadow-xl bg-white">
        <div className="flex flex-col gap-1 items-center ">
          <AppLogo alwaysFull={true} />
          <div className="text-lg text-black font-bold">Forgot Password?</div>
          <div className="flex flex-row">
            <div>Remember your password?</div>
            <Link
              to={'/login'}
              className="font-bold text-blue-500 hover:cursor-pointer hover:text-blue-700"
            >
              Login here
            </Link>
          </div>
        </div>

        {step === 1 && (
          <form>
            <input
              type="text"
              value={formData.identity}
              name="identity"
              onChange={handleChange}
              className="flex w-full rounded-sm p-2 border bg-gray-100 border-gray-300 focus:outline-sky-500"
              placeholder="Username or email"
            />
            <button
              type="submit"
              className="bg-sky-500 w-full rounded-sm font-bold p-2 text-white hover:bg-sky-600"
              onClick={handleRequestOTP}
            >
              Next
            </button>
          </form>
        )}

        {step === 2 && (
          <form className="flex flex-col gap-2">
            <div>OTP</div>
            <input
              type="text"
              name="otp_code"
              value={formData.otp_code}
              placeholder="OTP code"
              onChange={handleChange}
              className="flex rounded-sm p-2 border bg-gray-100 border-gray-300 focus:outline-sky-500"
            />
            <div>New Password</div>
            <input
              type="password"
              name="new_password"
              value={formData.new_password}
              placeholder="New Password"
              onChange={handleChange}
              className="flex rounded-sm p-2 border bg-gray-100 border-gray-300 focus:outline-sky-500"
            />

            <button
              type="submit"
              onClick={handleResetPassword}
              className="bg-sky-500 w-full rounded-sm font-bold p-2 text-white hover:bg-sky-600"
            >
              Reset Password
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
