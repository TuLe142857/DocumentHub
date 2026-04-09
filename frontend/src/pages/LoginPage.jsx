import {useState, useEffect} from "react";
import {useNavigate, useSearchParams} from "react-router-dom";
import api from "@/api/api.js"

const LoginPage = () =>{

  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [loginData, setLoginData] = useState({
    identity: searchParams.get('identity'),
    password: searchParams.get('password'),
  });

  const handleChange = (e) => {
    setLoginData({...loginData, [e.target.name]: e.target.value});
  }

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try{
      await api.post('/auth/login', loginData);
      alert("Login successfully");
      navigate('/');
    }catch(err){
      setError(err.response.data?.message);
    }finally{
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen bg-sky-100">
      <div className="flex flex-col items-center justify-center w-1/3 bg-white rounded-sm">
        <div>Login</div>
        {error && <div className="text-red-500">{error}</div>}
        <form
          onSubmit={handleLogin}
          className="flex flex-col h-full"
        >
          <input
          type="text"
          name="identity"
          value={loginData.identity}
          onChange={handleChange}
          placeholder="Email or Username"
          />
          <input
            type="password"
            name="password"
            value={loginData.password}
            onChange={handleChange}
            placeholder="Password"
          />
          <div className="flex flex-col">
            <div onClick={()=>navigate("/forgot-password")}>forgot password</div>
            <div onClick={()=>navigate("/register")}>register</div>
          </div>
          <button
            type="submit"
            className="bg-sky-100 w-full"
          >{loading ? 'Loading....' : 'Login'}</button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;

