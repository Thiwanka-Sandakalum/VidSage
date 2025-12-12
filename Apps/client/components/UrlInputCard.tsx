import React from 'react';
import { useForm } from 'react-hook-form';
import { useApp } from '../context/AppContext';
import { extractYoutubeId } from '../services/api';
import { Search, AlertCircle } from 'lucide-react';

interface FormInputs {
  url: string;
}

export const UrlInputCard: React.FC = () => {
  const { startProcessing, setVideoUrl, error, darkMode } = useApp();

  const { register, handleSubmit, formState: { errors } } = useForm<FormInputs>();

  const onSubmit = (data: FormInputs) => {
    const videoId = extractYoutubeId(data.url);
    if (videoId) {
      setVideoUrl(data.url);
      startProcessing(videoId);
    } else {
      // Manual error handling if regex fails but basic validation passed
    }
  };

  const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';
  const inputBg = darkMode ? 'bg-[#1A1B1E] border-gray-700 text-white focus:border-blue-500' : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500';

  return (
    <div className={`max-w-xl mx-auto mt-20 p-8 rounded-xl shadow-lg border ${cardBg}`}>
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">
          YouTube Video Analyst
        </h1>
        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          Paste a YouTube URL below to extract insights, transcripts, and chat with the content.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="relative">
          <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
            Video URL
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-gray-400" />
            </div>
            <input
              {...register("url", {
                required: "URL is required",
                validate: (value) => !!extractYoutubeId(value) || "Invalid YouTube URL"
              })}
              placeholder="https://www.youtube.com/watch?v=..."
              className={`w-full pl-10 pr-4 py-3 rounded-lg border outline-none transition-all ring-0 focus:ring-2 focus:ring-blue-500/50 ${inputBg}`}
            />
          </div>
          {errors.url && (
            <div className="flex items-center gap-1 mt-1 text-red-500 text-xs">
              <AlertCircle size={12} />
              <span>{errors.url.message}</span>
            </div>
          )}
        </div>

        {error && (
          <div className="p-3 rounded bg-red-500/10 border border-red-500/20 text-red-500 text-sm flex items-center gap-2">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg transform active:scale-[0.98]"
        >
          Process Video
        </button>
      </form>

      <div className={`mt-6 pt-6 border-t text-center text-xs ${darkMode ? 'border-gray-800 text-gray-500' : 'border-gray-100 text-gray-400'}`}>
        Supported formats: Regular videos, Shorts, Live streams
      </div>
    </div>
  );
};