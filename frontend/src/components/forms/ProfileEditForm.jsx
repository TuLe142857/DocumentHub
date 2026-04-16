import { useState, useRef } from 'react';
import { toast } from 'react-toastify';
import api from '@/api/api.js';
import { Camera as AvatarSelectIcon, X as ExitIcon } from 'lucide-react';

const ProfileEditForm = ({
  initValue,
  onSuccess,
  onCancel,
  className = '',
}) => {
  const [formData, setFormData] = useState({
    avatar: initValue?.avatar || null,
    full_name: initValue?.full_name || '',
    gender: initValue?.gender || null,
    bio: initValue?.bio || '',
  });

  const [avatarPreviewURL, setAvatarPreviewURL] = useState(
    initValue?.avatar_url || null
  );

  const avatarRef = useRef();

  const handleChange = (e) => {
    e.preventDefault();
    const { name, value, files, type } = e.target;
    if (type === 'file' && name === 'avatar') {
      const file = files[0];
      if (!file) {
        return;
      }

      setFormData({ ...formData, avatar: file });
      if (avatarPreviewURL) {
        URL.revokeObjectURL(avatarPreviewURL);
      }
      setAvatarPreviewURL(URL.createObjectURL(file));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const updateProfile = async (e) => {
    e?.preventDefault();

    // check diff + build request body
    const keys = ['full_name', 'bio', 'gender'];
    const diff = keys.some((k) => formData[k] !== initValue[k]);
    if (!diff) {
      toast.warn('You not change any thing');
      return;
    }
    const data = {};
    keys.forEach((k) => {
      if (formData[k] !== initValue[k]) {
        data[k] = formData[k];
      }
    });

    try {
      const toast_id = toast.loading('Updating your profile...');
      await api.patch('/users/me/profile', data);
      toast.update(toast_id, {
        type: 'success',
        render: 'success',
        isLoading: false,
        autoClose: 2000,
      });
      setTimeout(() => onSuccess(), 1000);
    } catch (err) {
      const msg = err?.response?.data?.message;
      toast.error(msg);
    }
  };

  const updateAvatar = async (e) => {
    e?.preventDefault();
    if (!formData.avatar) {
      toast.warn('no avatar provided');
      return;
    }

    try {
      const toast_id = toast.loading('Updating your avatar...');
      await api.put(
        '/users/me/avatar',
        { avatar: formData.avatar },
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      toast.update(toast_id, {
        type: 'success',
        render: 'success',
        isLoading: false,
        autoClose: 2000,
      });
      setFormData({ ...formData, avatar: undefined });
      onSuccess();
    } catch (err) {
      const msg = err?.response?.data?.message || 'Something went wrong';
      toast.error(msg);
    }
  };

  return (
    <div className={`flex flex-col p-2 ${className}`}>
      <button
        type="button"
        onClick={() => onCancel && onCancel()}
        className="m-2 p-2 rounded-full text-gray-500 self-end hover:bg-slate-200 hover:text-gray-700"
      >
        <ExitIcon />
      </button>
      {/*Avatar*/}
      <div
        className={`relative group flex flex-col items-center self-center w-50 h-50`}
      >
        <input
          type="file"
          name="avatar"
          ref={avatarRef}
          hidden={true}
          onChange={handleChange}
        />

        <img
          src={avatarPreviewURL || null}
          alt={'Avatar'}
          className={'w-full h-full object-cover rounded-full shadow-2xl'}
        />

        <div className="absolute inset-0 flex items-end justify-end p-2">
          <button
            onClick={() => avatarRef.current.click()}
            className="backdrop-blur-sm border text-black border-slate-400 p-2 rounded-full hover:bg-blue-500 hover:backdrop-blur-none hover:text-white"
          >
            <AvatarSelectIcon />
          </button>
        </div>
      </div>

      <button
        type="button"
        onClick={updateAvatar}
        className={`${formData.avatar ? 'block' : 'hidden'} self-center mt-2 text-md p-1.5 rounded-md text-white bg-green-500`}
      >
        Update avatar
      </button>

      <hr className="mt-4 mb-2 text-gray-300" />

      {/*PROFILE*/}
      <div className="flex flex-col text-md gap-2">
        <div className="text-black font-bold">Full name</div>
        <input
          type="text"
          name="full_name"
          value={formData.full_name}
          onChange={handleChange}
          className="rounded-sm p-2 border border-gray-100 bg-gray-200 focus:outline-2 focus:outline-blue-500/50 focus:bg-white"
        />

        <div className="text-black font-bold">Gender</div>
        <select
          value={formData.gender}
          name="gender"
          onChange={handleChange}
          className="rounded-sm p-2 border border-gray-100 bg-gray-200 focus:outline-2 focus:outline-blue-500/50 focus:bg-white"
        >
          <option value={'MALE'}>male</option>
          <option value={'FEMALE'}>female</option>
          <option value={'OTHER'}>other</option>
        </select>

        <div className="text-black font-bold">Bio</div>
        <textarea
          rows={5}
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          className="rounded-sm p-2 border border-gray-100 bg-gray-200 focus:outline-2 focus:outline-blue-500/50 focus:bg-white"
        />

        <div className="flex flex-row justify-end gap-5 mr-5">
          <button
            type="button"
            onClick={() => onCancel()}
            className={`text-md font-semibold p-1.5 rounded-lg border border-gray-700 text-gray-500 bg-white`}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => updateProfile()}
            className={`text-md font-semibold p-1.5 rounded-lg text-white bg-blue-500`}
          >
            Save changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileEditForm;
