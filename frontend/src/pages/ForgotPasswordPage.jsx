import { useState } from 'react';
import { Link } from 'react-router-dom';
import authApi from '@/api/authApi.js';
import AppLogo from '@/components/AppLogo.jsx';

const ForgotPasswordPage = () => {
  const [step, setStep] = useState(2);
  const [formData, setFormData] = useState({
    identity: '',
    otp_code: '',
    new_password: '',
  });

  return (
    <div className="flex items-center justify-center w-screen h-screen bg-sky-100">
      {step === 1 && (
        <div className="flex flex-col p-2 rounded-lg shadow-xl bg-white">
          <div className="flex flex-col items-center ">
            <AppLogo alwaysFull={true} />
            <div>Forgot Password?</div>
            <div className="flex flex-row">
              <div>Remember your password?</div>
              <Link to={'/login'}>Login here</Link>
            </div>
          </div>

          <form>
            <input className="flex w-full rounded-sm p-2 border bg-gray-100 border-gray-300 focus:outline-sky-500" />
            <button type="submit" className="bg-sky-100 rounded-sm my-2 p-2">
              Next
            </button>
          </form>
        </div>
      )}

      {step === 2 && (
        <div className="flex flex-col p-2 rounded-lg shadow-xl bg-white">
          <div className="flex flex-col items-center ">
            <AppLogo alwaysFull={true} />
            <div>Forgot Password?</div>
            <div className="flex flex-row">
              <div>Remember your password?</div>
              <Link to={'/login'}>Login here</Link>
            </div>
          </div>

          <form className="flex flex-col gap-2">
            <div>OTP</div>
            <input className="flex rounded-sm p-2 border bg-gray-100 border-gray-300 focus:outline-sky-500" />
            <div>New Password</div>
            <input className="flex rounded-sm p-2 border bg-gray-100 border-gray-300 focus:outline-sky-500" />

            <button
              type="submit"
              className="bg-sky-300 w-full rounded-sm font-bold p-2 text-white hover:bg-sky-400"
            >
              Next
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ForgotPasswordPage;
