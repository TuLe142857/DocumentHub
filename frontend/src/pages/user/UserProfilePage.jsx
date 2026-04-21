import { useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  LayoutDashboard as OverviewIcon,
  FileText as DocumentIcon,
  Heart as LikeIcon,
  Library as CollectionIcon,
  Trash2 as TrashIcon,
} from 'lucide-react';

import TabBar from '@/components/TabBar.jsx';
import UserCard from '@/components/UserCard.jsx';
import OverviewTab from '@/pages/user/tabs/OverviewTab.jsx';
import DocumentsTab from '@/pages/user/tabs/DocumentsTab.jsx';
import CollectionsTab from '@/pages/user/tabs/CollectionsTab.jsx';
import LikedDocumentsTab from '@/pages/user/tabs/LikedDocumentsTab.jsx';
import TrashTab from '@/pages/user/tabs/TrashTab.jsx';

import AppLogo from '@/components/AppLogo.jsx';

const publicTab = [
  {
    key: 'overview',
    label: 'Overview',
    icon: <OverviewIcon />,
  },
  {
    key: 'documents',
    label: 'Documents',
    icon: <DocumentIcon />,
  },
];

const UserProfilePage = () => {
  const { username } = useParams();

  // viewer
  const { user: currentUser, isAuthenticated } = useSelector(
    (state) => state.user
  );

  const [queryParams, setQueryParams] = useSearchParams();

  const [activeTab, setActiveTab] = useState(
    queryParams.get('tab') || 'overview'
  );

  const [tabs, setTabs] = useState(publicTab);

  useEffect(() => {
    const setup = () => {
      if (isAuthenticated && currentUser.username === username) {
        setTabs([
          ...publicTab,
          {
            key: 'collections',
            label: 'Collections',
            icon: <CollectionIcon />,
          },
          {
            key: 'liked',
            label: 'Liked',
            icon: <LikeIcon />,
          },
          {
            key: 'trash',
            label: 'Trash',
            icon: <TrashIcon />,
          },
        ]);
      } else {
        setTabs(publicTab);
      }
    };

    setup();
  }, [username, currentUser, isAuthenticated]);

  // useEffect(() => {
  //   setActiveTab(queryParams.get('tab') || 'overview');
  // }, [queryParams]);

  const onTabChange = (key) => {
    setActiveTab(key);
    setQueryParams({ tab: key });
  };

  return (
    <div className="flex flex-col md:flex-row w-screen max-w-screen bg-slate-50">
      <div className="static md:sticky md:top-0 md:h-fit">
        <AppLogo className="m-2" alwaysFull={true} />
        <UserCard username={username} />
      </div>

      <div className="flex flex-col flex-1">
        <TabBar
          tabs={tabs}
          activeTab={activeTab}
          onChangeTab={onTabChange}
          className="sticky top-2 z-999  self-center m-2 bg-white "
        />
        {activeTab === 'overview' && <OverviewTab username={username} />}
        {activeTab === 'documents' && <DocumentsTab username={username} />}
        {activeTab === 'collections' && <CollectionsTab />}
        {activeTab === 'liked' && <LikedDocumentsTab />}
        {activeTab === 'trash' && <TrashTab />}
      </div>
    </div>
  );
};

export default UserProfilePage;
