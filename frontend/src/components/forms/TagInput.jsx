import { Delete } from 'lucide-react';
import { useState } from 'react';

/**
 * @callback addTagCallback
 * @param {string} tag
 */

/**
 * @callback removeTagCallback
 * @param {string} tag
 */

/**
 * @param {Object} props
 * @param {Array<string>} props.tags
 * @param {addTagCallback} props.onAdd
 * @param {removeTagCallback} props.onRemove
 * @param {string} props.className
 * @param {string} props.placeHolder
 * @returns {React.JSX.Element}
 * @constructor
 */

const TagInput = ({
  tags,
  onAdd,
  onRemove,
  className = '',
  placeHolder = 'Enter tag and press Space',
}) => {
  const [input, setInput] = useState('');

  const handleAddTag = (t) => {
    if (tags.includes(t)) {
      return;
    }
    onAdd && onAdd(t);
  };

  const handleRemoveTag = (t) => {
    if (tags.includes(t)) {
      onRemove && onRemove(t);
    }
  };

  const handleInputChange = (e) => {
    e?.preventDefault();
    const value = e.target.value;
    if (value.endsWith(' ')) {
      handleAddTag(value.replaceAll(' ', ''));
      setInput('');
    } else {
      setInput(value);
    }
  };

  return (
    <div className={`flex flex-col gap-y-1 ${className}`}>
      <div className="flex flex-row flex-wrap gap-y-1 gap-x-1.5">
        {tags &&
          tags.map((tag) => (
            <div
              className="flex flex-row items-center gap-x-1 text-blue-500 text-sm font-semibold bg-sky-200/50 border border-sky-400 rounded-lg p-0.5 px-2"
              key={tag}
            >
              <span>{tag}</span>
              <span
                className="text-sky-500 hover:text-red-500 hover:cursor-pointer"
                onClick={() => handleRemoveTag(tag)}
              >
                <Delete size={16} />
              </span>
            </div>
          ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={handleInputChange}
        placeholder={placeHolder}
        className="text-md pl-2 p-1 border border-gray-200 focus:outline-sky-400 rounded-md"
      />
    </div>
  );
};

export default TagInput;
