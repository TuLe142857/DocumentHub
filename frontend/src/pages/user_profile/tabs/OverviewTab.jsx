import { useEffect, useState } from 'react';
import api from '@/api/api.js';
import Loading from '@/components/Loading.jsx';

const OverviewTab = ({ username }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.get(`users/${username}/profile`);
        setProfile(response.data?.data);
        console.log(response.data.data);
      } catch (error) {
        setError(
          error.response.data?.message ||
            'Something went wrong, please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [username]);

  if (error) return <div>Error</div>;
  if (!profile || loading) return <Loading />;
  return (
    <div className="flex flex-col rounded-xl m-2 p-2">
      {profile?.bio && (
        <pre className="bg-white border border-gray-200 p-2 rounded-md w-full text-wrap">
          {profile?.bio}
        </pre>
      )}
    </div>
  );
};

export default OverviewTab;
