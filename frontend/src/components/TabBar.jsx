import { useState } from 'react';

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
 * @returns {React.JSX.Element}
 * @constructor
 */
const TabBar = ({ tabs, activeTab, onChangeTab }) => {
  return (
    <div className="flex flex-col w-full ">
      <div className="flex flex-row">
        {tabs.map((tab) => (
          <div
            key={tab.key}
            className={`flex flex-row p-2 items-start justify-center font-medium border-b-2 ${activeTab === tab.key ? 'border-red-500 shadow-2xl' : 'border-transparent'} `}
            onClick={() => onChangeTab(tab.key)}
          >
            <button className={`flex flex-row p-2 rounded-sm hover:bg-sky-100`}>
              {tab.icon}
              <div>{tab.label}</div>
            </button>
          </div>
        ))}
      </div>
      <hr />
    </div>
  );
};

export default TabBar;
