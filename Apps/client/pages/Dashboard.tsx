import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { VideoPlayerCard } from '../components/VideoPlayerCard';
import { ChatPanel } from '../components/ChatPanel';
import { useApp } from '../context/AppContext';

export const Dashboard: React.FC = () => {
  const { videoId: urlVideoId } = useParams<{ videoId?: string }>();
  const { metadata, videoId, loadVideoById } = useApp();

  useEffect(() => {
    if (urlVideoId && urlVideoId !== videoId) {
      loadVideoById(urlVideoId);
    }
  }, [urlVideoId, videoId, loadVideoById]);

  if (!metadata) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading video...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
      <div className="space-y-6">
        <VideoPlayerCard />
        <div className="lg:hidden">
          <ChatPanel />
        </div>
      </div>

      <div className="hidden lg:flex flex-col gap-6">
        <ChatPanel />
      </div>
    </div>
  );
};