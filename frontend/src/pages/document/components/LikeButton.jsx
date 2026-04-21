import { ThumbsUp } from 'lucide-react';

import api from '@/api/api.js';
const LikeButton = ({ doc, onUpdate }) => {
  const handleLike = async () => {
    try {
      if (doc.liked) {
        await api.delete(`/documents/${doc.id}/like`);
      } else {
        await api.put(`/documents/${doc.id}/like`);
      }
      onUpdate((prevState) => ({
        ...prevState,
        liked: !doc.liked,
        like_count: prevState.like_count + (doc.liked ? -1 : 1),
      }));
    } catch (err) {
      const msg = err.response.data?.message || 'Something went wrong';
      alert(`Can not ${doc.liked ? 'unlike ' : ''}like document: ${msg}`);
    }
  };
  return (
    <div>
      <button
        className="flex flex-row p-2  rounded-xl bg-white hover:bg-sky-200"
        onClick={handleLike}
      >
        <ThumbsUp fill={doc?.liked ? '#27CFF5' : 'white'} />
        <div>{doc?.like_count}</div>
      </button>
    </div>
  );
};

export default LikeButton;
