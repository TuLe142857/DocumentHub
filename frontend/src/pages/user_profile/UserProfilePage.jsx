import { useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { BookOpen, Heart, Bookmark, FileUser, Trash2 } from 'lucide-react';

import TabBar from '@/components/TabBar.jsx';
import ProfileTab from '@/pages/user_profile/tabs/ProfileTab.jsx';
import OverviewTab from '@/pages/user_profile/tabs/OverviewTab.jsx';
import DocumentsTab from '@/pages/user_profile/tabs/DocumentsTab.jsx';
import CollectionsTab from '@/pages/user_profile/tabs/CollectionsTab.jsx';
import LikedDocumentsTab from '@/pages/user_profile/tabs/LikedDocumentsTab.jsx';
import TrashTab from '@/pages/user_profile/tabs/TrashTab.jsx';

const publicTab = [
  {
    key: 'overview',
    label: 'Overview',
    icon: <FileUser />,
  },
  {
    key: 'documents',
    label: 'Documents',
    icon: <BookOpen />,
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
            icon: <Bookmark />,
          },
          {
            key: 'liked',
            label: 'Liked',
            icon: <Heart />,
          },
          {
            key: 'trash',
            label: 'Trash',
            icon: <Trash2 />,
          },
        ]);
      }
    };

    setup();
  }, [username, currentUser, isAuthenticated]);

  useEffect(() => {
    setActiveTab(queryParams.get('tab') || 'overview');
  }, [queryParams]);

  const onTabChange = (key) => {
    setActiveTab(key);
    setQueryParams({ tab: key });
  };

  return (
    <div className="flex flex-col w-screen">
      {/* TAB BAR*/}
      <TabBar tabs={tabs} activeTab={activeTab} onChangeTab={onTabChange} />

      <div className="grid sm:grid-cols-1 lg:grid-cols-3">
        {/*Profile Tab*/}
        <ProfileTab username={username} />

        {/*Content Tab*/}
        <div className="lg:col-span-2 ">
          {activeTab === 'overview' && <OverviewTab username={username} />}
          {activeTab === 'documents' && <DocumentsTab username={username} />}
          {activeTab === 'collections' && (
            <CollectionsTab username={username} />
          )}
          {activeTab === 'liked' && <LikedDocumentsTab username={username} />}
          {activeTab === 'trash' && <TrashTab />}
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage;
