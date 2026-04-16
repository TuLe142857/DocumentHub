/**
 * @typedef Category
 * @property {Number} id
 * @property {string} name
 */

/**
 * @callback selectCategoryCallback
 * @param {Number} id
 */

/**
 * @callback removeCategoryCallback
 * @param {Number} id
 */

/**
 * @param {Object} props
 * @param {Array<Category>} props.categories
 * @param {Array<Number>} props.selectedCategories
 * @param {selectCategoryCallback} props.onSelect
 * @param {removeCategoryCallback} props.onRemove
 * @returns {React.JSX.Element}
 * @constructor
 */

const CategoriesFilter = ({
  categories,
  selectedCategories,
  onSelect,
  onRemove,
}) => {
  const handleChange = (e) => {
    const id = Number(e.target.value);
    if (e.target.checked) {
      onSelect(id);
    } else {
      onRemove(id);
    }
  };
  return (
    <div className={`flex flex-col`}>
      {categories &&
        categories.map((category) => (
          <label key={category.id}>
            <input
              type="checkbox"
              value={category.id}
              checked={selectedCategories.includes(category.id)}
              onChange={handleChange}
            />
            {category.name}
          </label>
        ))}
    </div>
  );
};
export default CategoriesFilter;
