import React, { useEffect, useRef, useState } from 'react';
import { useApp } from '../context/AppContext';
import { User, Bookmark, BookmarkCheck } from 'lucide-react';

interface VideoDetails {
  title: string;
  author_name: string;
  author_url: string;
  thumbnail_url: string;
}

interface SavedVideo {
  videoId: string;
  title: string;
  author: string;
  savedAt: string;
}

export const VideoPlayerCard: React.FC = () => {
  const { videoId, darkMode, currentSeekTime, clearSeek } = useApp();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [videoDetails, setVideoDetails] = useState<VideoDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    if (videoId) {
      setLoading(true);
      fetch(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`)
        .then(res => res.json())
        .then(data => {
          setVideoDetails(data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to fetch video details:', err);
          setLoading(false);
        });

      checkIfSaved(videoId);
    }
  }, [videoId]);

  const checkIfSaved = (id: string) => {
    const saved = localStorage.getItem('savedVideos');
    if (saved) {
      const savedVideos: SavedVideo[] = JSON.parse(saved);
      setIsSaved(savedVideos.some(v => v.videoId === id));
    }
  };

  const toggleSave = () => {
    if (!videoDetails) return;

    const saved = localStorage.getItem('savedVideos');
    let savedVideos: SavedVideo[] = saved ? JSON.parse(saved) : [];

    if (isSaved) {
      savedVideos = savedVideos.filter(v => v.videoId !== videoId);
      setIsSaved(false);
    } else {
      savedVideos.push({
        videoId: videoId,
        title: videoDetails.title,
        author: videoDetails.author_name,
        savedAt: new Date().toISOString()
      });
      setIsSaved(true);
    }

    localStorage.setItem('savedVideos', JSON.stringify(savedVideos));
  };

  useEffect(() => {
    if (currentSeekTime !== null && iframeRef.current) {
      const currentSrc = iframeRef.current.src.split('?')[0];
      iframeRef.current.src = `${currentSrc}?autoplay=1&start=${Math.floor(currentSeekTime)}`;
      clearSeek();
    }
  }, [currentSeekTime, clearSeek]);

  if (!videoId) return null;

  const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';
  const textMain = darkMode ? 'text-gray-100' : 'text-gray-900';
  const textSub = darkMode ? 'text-gray-400' : 'text-gray-500';
  const linkColor = darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700';

  return (
    <div className={`flex flex-col gap-4 rounded-xl shadow-md border overflow-hidden ${cardBg}`}>
      <div className="relative pt-[56.25%] bg-black">
        <iframe
          ref={iframeRef}
          src={`https://www.youtube.com/embed/${videoId}`}
          title="YouTube video player"
          className="absolute top-0 left-0 w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>

      <div className="p-4 space-y-3">
        {loading ? (
          <div className={`animate-pulse space-y-3`}>
            <div className={`h-6 ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} rounded w-3/4`}></div>
            <div className={`h-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} rounded w-1/2`}></div>
          </div>
        ) : videoDetails ? (
          <>
            <div className="flex items-start justify-between gap-3">
              <h2 className={`text-lg font-bold leading-tight flex-1 ${textMain}`}>
                {videoDetails.title}
              </h2>
              <button
                onClick={toggleSave}
                className={`flex-shrink-0 p-2 rounded-lg transition-all ${isSaved
                  ? darkMode
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                  : darkMode
                    ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                title={isSaved ? 'Remove from saved' : 'Save video'}
              >
                {isSaved ? <BookmarkCheck size={20} /> : <Bookmark size={20} />}
              </button>
            </div>

            <div className="flex flex-col gap-2">
              <a
                href={videoDetails.author_url}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex items-center gap-2 text-sm font-medium ${linkColor} transition-colors`}
              >
                <User size={16} />
                <span>{videoDetails.author_name}</span>
              </a>

              <div className="flex items-center gap-2 text-xs">
                <a
                  href={`https://www.youtube.com/watch?v=${videoId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`${linkColor} transition-colors`}
                >
                  Watch on YouTube
                </a>
              </div>
            </div>
          </>
        ) : (
          <div className={textSub}>
            <p>Video ID: {videoId}</p>
          </div>
        )}
      </div>
    </div>
  );
};