import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Search } from 'lucide-react';

export const TranscriptPanel: React.FC = () => {
  const { transcript, seekVideo, darkMode } = useApp();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredTranscript = transcript.filter(segment =>
    segment.text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';
  const inputBg = darkMode ? 'bg-[#1A1B1E] border-gray-700 text-white' : 'bg-gray-50 border-gray-300 text-gray-900';
  const rowHover = darkMode ? 'hover:bg-[#2C2E33]' : 'hover:bg-blue-50';

  return (
    <div className={`flex flex-col h-[500px] lg:h-[600px] rounded-xl shadow-md border overflow-hidden ${cardBg}`}>
      {/* Header */}
      <div className={`p-4 border-b ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
        <h3 className="font-bold text-lg mb-3">Transcript</h3>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={16} />
          <input
            type="text"
            placeholder="Search transcript..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-9 pr-4 py-2 text-sm rounded-lg border outline-none focus:ring-1 focus:ring-blue-500 ${inputBg}`}
          />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
        {filteredTranscript.length > 0 ? (
          filteredTranscript.map((segment) => (
            <div
              key={segment.id}
              onClick={() => seekVideo(segment.start)}
              className={`group p-3 rounded-lg cursor-pointer transition-colors duration-150 flex gap-3 ${rowHover}`}
            >
              <span className="text-blue-500 font-mono text-xs font-semibold pt-1 min-w-[40px]">
                {formatTime(segment.start)}
              </span>
              <p className={`text-sm leading-relaxed ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                {segment.text}
              </p>
            </div>
          ))
        ) : (
          <div className="text-center p-8 text-gray-500 text-sm">
            No matching segments found.
          </div>
        )}
      </div>
    </div>
  );
};