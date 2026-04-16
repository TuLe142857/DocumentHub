/**
 * @typedef TabConfig
 * @property {string} key
 * @property {string} label
 * @property {React.JSX.Element} icon
 */

/**
 *
 * @param {TabConfig} config
 * @returns {React.JSX.Element}
 * @constructor
 */

/**
 * @callback tabChangeCallBack
 * @param {string} key
 */

/**
 * @param {Array<TabConfig>} tabs
 * @param {tabChangeCallBack} onChangeTab
 * @param {string} activeTab - key of active tab or first tab by default
 * @param {string} className
 * @returns {React.JSX.Element}
 * @constructor
 */
const TabBar = ({ tabs, activeTab, onChangeTab, className = '' }) => {
  return (
    <div
      className={`
      flex flex-row w-fit p-1 items-center justify-center rounded-2xl border border-slate-200
      text-gray-500 ${className}
      `}
    >
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`
            flex flex-row m-2 p-3 items-start justify-center font-semibold border-b-2
            rounded-2xl border-none
            ${
              activeTab === tab.key
                ? 'text-blue-500 bg-sky-100/50 border-sky-200/50 shadow-xs shadow-sky-200'
                : 'text-gray-500 border-transparent hover:bg-gray-200/50'
            } 
            `}
          onClick={() => onChangeTab(tab.key)}
        >
          <div>{tab.icon}</div>
          <div className="hidden sm:block">{tab.label}</div>
        </button>
      ))}
    </div>
    // </div>
  );
};

export default TabBar;
