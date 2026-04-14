import { useState, useEffect, useRef } from 'react';
import api from '@/api/api.js';
import avatar from '@/assets/avatar.jpg';
import { useSelector } from 'react-redux';
import { UserRoundPen, Pencil } from 'lucide-react';
import Loading from '@/components/Loading.jsx';
import ErrorPage from '@/pages/errors/ErrorPage.jsx';

const getGenderCall = (gender) => {
  if (!gender) return '';
  if (gender?.toLowerCase() === 'male') {
    return 'he/him';
  }
  if (gender?.toLowerCase() === 'female') {
    return 'she/her';
  }
  if (gender?.toLowerCase() === 'other') {
    return 'they/them';
  }
};

const ProfileTab = ({ username }) => {
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );

  const [editMode, setEditMode] = useState(false);

  const fileInputRef = useRef(null);
  const [updateForm, setUpdateForm] = useState({
    avatar: null,
    full_name: currentUser?.full_name || null,
    gender: currentUser?.gender || null,
    bio: currentUser?.bio || null,
  });

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('hi');

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
  }, []);

  const handleSwitchToEditMode = () => {
    setEditMode(true);
    setUpdateForm({
      avatar: null,
      full_name: profile?.full_name || null,
      gender: profile?.gender || null,
      bio: profile?.bio || null,
    });
  };

  const handleFormChange = (e) => {
    const { name, type, files, value } = e.target;
    if (type === 'file' && name === 'avatar') {
      const file = files[0];
      if (!file) {
        alert('invalid file');
        return;
      }
      const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
      if (!validTypes.includes(file.type)) {
        alert('Chỉ chấp nhận file ảnh (JPG, PNG, WEBP)!');
        return;
      }

      setUpdateForm({ ...updateForm, avatar: file });
    } else {
      setUpdateForm({ ...updateForm, [name]: value });
    }
  };

  const handleSubmitUpdate = async (e) => {
    const updateAvatar = async () => {
      try {
        await api.put(
          `users/me/avatar`,
          { avatar: updateForm.avatar },
          { headers: { 'Content-Type': 'multipart/form-data' } }
        );
      } catch (err) {
        const msg =
          err.response.data?.message ||
          'Something went wrong, please try again.';
        alert(`Error when update user avatar: ${msg}`);
      }
    };

    const updateProfile = async () => {
      try {
        const body = {
          full_name: updateForm?.full_name || null,
          gender: updateForm?.gender || null,
          bio: updateForm?.bio || null,
        };
        await api.patch(`users/me/profile`, body);
      } catch (err) {
        const msg =
          err.response.data?.message ||
          'Something went wrong, please try again.';
        alert(`Error when update user profile: ${msg}`);
      }
    };

    e.preventDefault();
    if (updateForm.avatar) {
      await updateAvatar();
    }
    const checkDiff =
      updateForm.full_name !== profile.full_name ||
      updateForm.gender !== profile.gender ||
      updateForm.bio !== profile.bio;
    if (checkDiff) {
      await updateProfile();
    }
    setEditMode(false);
  };

  if (loading && !editMode) {
    return <Loading />;
  }

  if (error) {
    return <ErrorPage message={error} />;
  }

  return !editMode ? (
    <div className="flex flex-col h-fit rounded-xl shadow-2xl m-3 p-3 bg-white">
      <img
        src={profile?.avatar_url || avatar}
        alt="avatar"
        className="self-center shadow-2xl rounded-full w-75 h-75"
      />

      <div className="text-xl font-bold flex flex-row gap-1">
        <div className="text-black">{profile.full_name || 'N/A'}</div>
        <div className="text-gray-600">{getGenderCall(profile?.gender)}</div>
      </div>
      <div className="text-black text-lg font-medium">{profile.username}</div>
      <hr className="border-black" />
      <pre className="text-lg text-black m-2 p-2">
        {profile.bio || 'No bio'}
      </pre>
      {isAuthenticated && currentUser && currentUser?.username === username && (
        <button
          onClick={handleSwitchToEditMode}
          className="flex flex-row text-lg p-2 m-2 gap-1 border border-white bg-sky-100 rounded-lg hover:bg-sky-300 hover:text-white"
        >
          <UserRoundPen />
          <div>Edit profile</div>
        </button>
      )}
    </div>
  ) : (
    // Form update
    <form
      onSubmit={handleSubmitUpdate}
      className="flex flex-col h-fit rounded-xl shadow-2xl m-3 p-3 bg-gray-100"
    >
      <img
        src={
          updateForm?.avatar
            ? URL.createObjectURL(updateForm?.avatar)
            : profile?.avatar_url
        }
        alt="avatar"
        className="self-center rounded-full w-50 h-50 bg-sky-400"
      />
      <input
        type="file"
        name="avatar"
        hidden={true}
        ref={fileInputRef}
        onChange={handleFormChange}
      />
      <button
        type="button"
        className="flex flex-row text-lg p-2 m-2 gap-1 border border-white bg-sky-100 rounded-lg hover:bg-sky-300 hover:text-white "
        onClick={() => fileInputRef.current.click()}
      >
        <Pencil />
        <div>Select Avatar</div>
      </button>

      <div className="font-bold text-black text-lg">Full name</div>
      <input
        type="text"
        name="full_name"
        value={updateForm.full_name}
        placeholder="full name"
        onChange={handleFormChange}
        className="p-2 m-2 rounded-sm bg-gray-200 focus:outline-sky-500"
      />

      <div className="font-bold text-black text-lg">Gender</div>
      <select
        value={updateForm.gender}
        name="gender"
        onChange={handleFormChange}
        className="p-2 m-2 rounded-sm bg-gray-200"
      >
        <option value={'MALE'}>male</option>
        <option value={'FEMALE'}>female</option>
        <option value={'OTHER'}>other</option>
      </select>

      <div className="font-bold text-black text-lg p-2 m-2">Bio</div>
      <textarea
        rows={3}
        name="bio"
        value={updateForm.bio}
        placeholder="bio"
        onChange={handleFormChange}
        className="flex p-2 m-5"
      >
        {currentUser?.bio || ''}
      </textarea>

      {/*button*/}
      <div className="flex flex-row items-center">
        <button
          type="submit"
          className="flex flex-row text-lg p-2 m-2 gap-1 border border-white bg-sky-100 rounded-lg hover:bg-sky-300 hover:text-white"
        >
          Save
        </button>
        <button
          type="button"
          onClick={() => setEditMode(false)}
          className="flex flex-row text-lg p-2 m-2 gap-1 border border-white bg-sky-100 rounded-lg hover:bg-sky-300 hover:text-white"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default ProfileTab;
