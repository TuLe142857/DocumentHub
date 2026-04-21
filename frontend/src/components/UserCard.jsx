import { useState, useEffect, useRef } from 'react';
import api from '@/api/api.js';
import avatar from '@/assets/avatar.jpg';
import { useSelector } from 'react-redux';
import { UserRoundPen, Pencil } from 'lucide-react';
import Loading from '@/components/Loading.jsx';
import ErrorPage from '@/pages/errors/ErrorPage.jsx';
import Modal from '@/modal/Modal.jsx';
import ProfileEditForm from '@/components/forms/ProfileEditForm.jsx';

const getGenderPronouns = (gender) => {
  if (!gender) return '';
  if (gender?.toLowerCase() === 'male') {
    return 'he/him';
  }
  if (gender?.toLowerCase() === 'female') {
    return 'she/her';
  }
  return '';
};

const UserCard = ({ username, editable = true, className = '' }) => {
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('hi');
  const [openModal, setOpenModal] = useState(false);
  const [profileChanged, setProfileChanged] = useState(false);

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

  useEffect(() => {
    fetchProfile();
  }, [username]);

  const handleModalClose = () => {
    setOpenModal(false);
    if (profileChanged) {
      setProfileChanged(false);
      fetchProfile();
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return <ErrorPage message={error} />;
  }

  return (
    <div className="flex flex-col gap-2 h-fit rounded-xl shadow-2xl m-3 p-3 bg-white">
      <Modal isOpen={openModal} onClose={() => handleModalClose()}>
        <ProfileEditForm
          initValue={profile}
          onSuccess={() => setProfileChanged(true)}
          onCancel={() => handleModalClose()}
          className={
            'bg-white min-w-100 rounded-xl overflow-auto max-h-screen max-w-screen'
          }
        />
      </Modal>

      <img
        src={profile?.avatar_url || avatar}
        alt="avatar"
        className="self-center aspect-square w-48 h-48 md:w-64 md:min-w-64 md:h-64 md:min-h-64 rounded-full object-cover shadow-xl"
      />
      <div className="text-xl font-bold flex flex-row gap-1">
        <div className="text-black">{profile.full_name || 'N/A'}</div>
        <div className="text-gray-600">
          {getGenderPronouns(profile?.gender)}
        </div>
      </div>
      <div className=" text-lg text-black font-medium">{profile.username}</div>
      <hr className="my-1 text-gray-200" />
      <pre className="text-sm font-semibold text-gray-500 whitespace-pre-wrap line-clamp-3 max-w-50">
        {profile.bio || 'No bio'}
      </pre>
      {editable &&
        isAuthenticated &&
        currentUser &&
        currentUser?.username === username && (
          <button
            onClick={() => setOpenModal(true)}
            className="flex flex-row justify-center text-lg text-blue-500 p-2 m-2 gap-1 border border-sky-200 bg-sky-100/50 rounded-lg hover:bg-sky-200/50"
          >
            <UserRoundPen />
            <div>Edit profile</div>
          </button>
        )}
    </div>
  );
};

export default UserCard;
