import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import {
    Grid,
    List,
    Search,
    Trash2,
    Play,
    ChevronDown,
    CheckSquare,
    Square,
    X
} from 'lucide-react';
import { VideoMetadata } from '../types';
import { saveVideo } from '../services/api';

type ViewMode = 'grid' | 'list';
type SortOption = 'date' | 'title' | 'chunks';
type SortOrder = 'asc' | 'desc';

export const Library: React.FC = () => {
    const navigate = useNavigate();
    const {
        darkMode,
        processedVideos,
        loadVideos,
        deleteVideo } = useApp();

    const [viewMode, setViewMode] = useState<ViewMode>('grid');
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState<SortOption>('date');
    const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
    const [selectedVideos, setSelectedVideos] = useState<Set<string>>(new Set());
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [filterStatus, setFilterStatus] = useState<string>('all');

    useEffect(() => {
        loadVideos();
    }, []);

    // Filter and sort videos
    const filteredAndSortedVideos = React.useMemo(() => {
        let filtered = processedVideos;

        // Search filter
        if (searchQuery) {
            filtered = filtered.filter(video =>
                video.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                video.video_id.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        // Status filter
        if (filterStatus !== 'all') {
            filtered = filtered.filter(video => video.status === filterStatus);
        }

        // Sort
        const sorted = [...filtered].sort((a, b) => {
            let comparison = 0;

            switch (sortBy) {
                case 'title':
                    comparison = a.title.localeCompare(b.title);
                    break;
                case 'chunks':
                    comparison = a.chunks_count - b.chunks_count;
                    break;
                case 'date':
                default:
                    // Assuming newer videos have higher video_id or you can add created_at field
                    comparison = a.video_id.localeCompare(b.video_id);
                    break;
            }

            return sortOrder === 'asc' ? comparison : -comparison;
        });

        return sorted;
    }, [processedVideos, searchQuery, sortBy, sortOrder, filterStatus]);

    // Select/deselect video
    const toggleVideoSelection = (videoId: string) => {
        const newSelected = new Set(selectedVideos);
        if (newSelected.has(videoId)) {
            newSelected.delete(videoId);
        } else {
            newSelected.add(videoId);
        }
        setSelectedVideos(newSelected);
    };

    // Select all / deselect all
    const toggleSelectAll = () => {
        if (selectedVideos.size === filteredAndSortedVideos.length) {
            setSelectedVideos(new Set());
        } else {
            setSelectedVideos(new Set(filteredAndSortedVideos.map(v => v.video_id)));
        }
    };

    // Delete selected videos
    const handleBulkDelete = async () => {
        setIsDeleting(true);
        try {
            await Promise.all(
                Array.from(selectedVideos).map(videoId => deleteVideo(videoId))
            );
            setSelectedVideos(new Set());
            setShowDeleteModal(false);
        } catch (error) {
            console.error('Failed to delete videos:', error);
        } finally {
            setIsDeleting(false);
        }
    };

    // Open video - Navigate to dashboard with video ID
    const handleOpenVideo = (video: VideoMetadata) => {
        navigate(`/dashboard/${video.video_id}`);
    };

    const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';
    const textMain = darkMode ? 'text-gray-100' : 'text-gray-900';
    const textSub = darkMode ? 'text-gray-400' : 'text-gray-600';
    const inputBg = darkMode ? 'bg-[#1A1B1E] border-gray-700 text-white' : 'bg-white border-gray-300 text-gray-900';
    const hoverBg = darkMode ? 'hover:bg-[#2C2E33]' : 'hover:bg-gray-50';

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 animate-fade-in">
            {/* Header */}
            <div className="mb-8">
                <h1 className={`text-3xl font-bold mb-2 ${textMain}`}>Video Library</h1>
                <p className={textSub}>
                    {processedVideos.length} video{processedVideos.length !== 1 ? 's' : ''} processed
                </p>
            </div>

            {/* Toolbar */}
            <div className={`${cardBg} border rounded-xl p-4 mb-6`}>
                <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
                    {/* Search */}
                    <div className="relative flex-1 w-full lg:max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search videos..."
                            className={`w-full pl-10 pr-4 py-2 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                        />
                        {searchQuery && (
                            <button
                                onClick={() => setSearchQuery('')}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                            >
                                <X size={18} />
                            </button>
                        )}
                    </div>

                    {/* Controls */}
                    <div className="flex gap-2 items-center flex-wrap">
                        {/* Filter */}
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className={`px-3 py-2 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                        >
                            <option value="all">All Videos</option>
                            <option value="completed">Ready to Watch</option>
                            <option value="processing">Processing</option>
                        </select>

                        {/* Sort */}
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as SortOption)}
                            className={`px-3 py-2 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                        >
                            <option value="date">Recently Added</option>
                            <option value="title">Title (A-Z)</option>
                            <option value="chunks">Content Length</option>
                        </select>

                        {/* Sort Order */}
                        <button
                            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                            className={`px-3 py-2 rounded-lg border ${inputBg} ${hoverBg} transition-colors`}
                            title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
                        >
                            <ChevronDown
                                size={18}
                                className={`transform transition-transform ${sortOrder === 'asc' ? 'rotate-180' : ''}`}
                            />
                        </button>

                        {/* View Mode */}
                        <div className={`flex border rounded-lg ${darkMode ? 'border-gray-700' : 'border-gray-300'}`}>
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`px-3 py-2 rounded-l-lg transition-colors ${viewMode === 'grid'
                                    ? 'bg-blue-600 text-white'
                                    : `${inputBg} ${hoverBg}`
                                    }`}
                                title="Grid View"
                            >
                                <Grid size={18} />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`px-3 py-2 rounded-r-lg border-l transition-colors ${darkMode ? 'border-l-gray-700' : 'border-l-gray-300'
                                    } ${viewMode === 'list'
                                        ? 'bg-blue-600 text-white'
                                        : `${inputBg} ${hoverBg}`
                                    }`}
                                title="List View"
                            >
                                <List size={18} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Bulk Actions */}
                {selectedVideos.size > 0 && (
                    <div className="mt-4 pt-4 border-t flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <button
                                onClick={toggleSelectAll}
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg ${hoverBg} transition-colors ${textMain}`}
                            >
                                {selectedVideos.size === filteredAndSortedVideos.length ? (
                                    <CheckSquare size={18} className="text-blue-500" />
                                ) : (
                                    <Square size={18} />
                                )}
                                <span className="text-sm font-medium">
                                    {selectedVideos.size} selected
                                </span>
                            </button>
                        </div>

                        <button
                            onClick={() => setShowDeleteModal(true)}
                            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                        >
                            <Trash2 size={16} />
                            <span>Delete Selected</span>
                        </button>
                    </div>
                )}
            </div>

            {/* Videos Grid/List */}
            {filteredAndSortedVideos.length === 0 ? (
                <div className={`${cardBg} border rounded-xl p-12 text-center`}>
                    <div className="text-gray-400 mb-4">
                        <Grid size={48} className="mx-auto opacity-50" />
                    </div>
                    <h3 className={`text-xl font-semibold mb-2 ${textMain}`}>
                        {searchQuery ? 'No videos found' : 'No videos yet'}
                    </h3>
                    <p className={textSub}>
                        {searchQuery
                            ? 'Try adjusting your search or filters'
                            : 'Process your first video to get started'
                        }
                    </p>
                </div>
            ) : (
                <div className={
                    viewMode === 'grid'
                        ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                        : 'space-y-4'
                }>
                    {filteredAndSortedVideos.map(video => (
                        <VideoCard
                            key={video.video_id}
                            video={video}
                            viewMode={viewMode}
                            isSelected={selectedVideos.has(video.video_id)}
                            onToggleSelect={() => toggleVideoSelection(video.video_id)}
                            onOpen={() => handleOpenVideo(video)}
                            onDelete={() => {
                                setSelectedVideos(new Set([video.video_id]));
                                setShowDeleteModal(true);
                            }}
                            darkMode={darkMode}
                        />
                    ))}
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {showDeleteModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className={`${cardBg} border rounded-xl p-6 max-w-md w-full`}>
                        <h3 className={`text-xl font-bold mb-4 ${textMain}`}>Confirm Deletion</h3>
                        <p className={`mb-6 ${textSub}`}>
                            Are you sure you want to delete {selectedVideos.size} video{selectedVideos.size !== 1 ? 's' : ''}?
                            This action cannot be undone.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setShowDeleteModal(false)}
                                disabled={isDeleting}
                                className={`px-4 py-2 rounded-lg border ${inputBg} ${hoverBg} transition-colors disabled:opacity-50`}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleBulkDelete}
                                disabled={isDeleting}
                                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
                            >
                                {isDeleting ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                        Deleting...
                                    </>
                                ) : (
                                    <>
                                        <Trash2 size={16} />
                                        Delete
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Video Card Component
interface VideoCardProps {
    video: VideoMetadata;
    viewMode: ViewMode;
    isSelected: boolean;
    onToggleSelect: () => void;
    onOpen: () => void;
    onDelete: () => void;
    darkMode: boolean;
}

const VideoCard: React.FC<VideoCardProps> = ({
    video,
    viewMode,
    isSelected,
    onToggleSelect,
    onOpen,
    onDelete,
    darkMode
}) => {
    const [isSaving, setIsSaving] = React.useState(false);
    const [saved, setSaved] = React.useState(false);
    const handleSave = async () => {
        setIsSaving(true);
        try {
            await saveVideo(video.video_id);
            setSaved(true);
        } catch (err) {
            // Optionally show error
        } finally {
            setIsSaving(false);
        }
    };
    const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';
    const textMain = darkMode ? 'text-gray-100' : 'text-gray-900';
    const hoverBg = darkMode ? 'hover:bg-[#2C2E33]' : 'hover:bg-gray-50';

    if (viewMode === 'list') {
        return (
            <div className={`${cardBg} border rounded-xl p-4 flex items-center gap-4 transition-all ${hoverBg} ${isSelected ? 'ring-2 ring-blue-500' : ''}`}>
                <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={onToggleSelect}
                    className="w-5 h-5 rounded cursor-pointer"
                />

                <img
                    src={`https://img.youtube.com/vi/${video.video_id}/default.jpg`}
                    alt={video.title}
                    className="w-32 h-20 object-cover rounded"
                />

                <div className="flex-1 min-w-0">
                    <h3 className={`font-semibold mb-2 truncate ${textMain}`}>{video.title}</h3>
                    {video.status !== 'completed' && (
                        <span className={`inline-block px-2 py-1 rounded text-xs bg-yellow-500/20 text-yellow-600`}>
                            Processing...
                        </span>
                    )}
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={onOpen}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2 font-medium"
                    >
                        <Play size={16} />
                        <span>Watch & Ask</span>
                    </button>
                    <button
                        onClick={onDelete}
                        className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Delete video"
                    >
                        <Trash2 size={16} />
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaving || saved}
                        className={`p-2 text-green-600 hover:bg-green-500/10 rounded-lg transition-colors ${saved ? 'opacity-50' : ''}`}
                        title={saved ? 'Saved' : 'Save for later'}
                    >
                        {saved ? 'Saved' : 'Save'}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className={`${cardBg} border rounded-xl overflow-hidden transition-all ${isSelected ? 'ring-2 ring-blue-500' : ''}`}>
            <div className="relative">
                <img
                    src={`https://img.youtube.com/vi/${video.video_id}/maxresdefault.jpg`}
                    alt={video.title}
                    className="w-full h-48 object-cover"
                />
                <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={onToggleSelect}
                    className="absolute top-3 left-3 w-5 h-5 rounded cursor-pointer"
                />
                <button
                    onClick={onOpen}
                    className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 hover:opacity-100 transition-opacity"
                >
                    <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
                        <Play size={24} className="text-white ml-1" />
                    </div>
                </button>
            </div>

            <div className="p-4">
                <h3 className={`font-semibold mb-3 line-clamp-2 min-h-[3rem] ${textMain}`}>{video.title}</h3>

                {video.status !== 'completed' && (
                    <div className="mb-3">
                        <span className={`inline-block px-2 py-1 rounded text-xs bg-yellow-500/20 text-yellow-600`}>
                            Processing...
                        </span>
                    </div>
                )}

                <div className="flex gap-2 mt-auto">
                    <button
                        onClick={onOpen}
                        className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2 font-medium"
                    >
                        <Play size={16} />
                        <span>Watch & Ask</span>
                    </button>
                    <button
                        onClick={onDelete}
                        className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Delete video"
                    >
                        <Trash2 size={16} />
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaving || saved}
                        className={`p-2 text-green-600 hover:bg-green-500/10 rounded-lg transition-colors ${saved ? 'opacity-50' : ''}`}
                        title={saved ? 'Saved' : 'Save for later'}
                    >
                        {saved ? 'Saved' : 'Save'}
                    </button>
                </div>
            </div>
        </div>
    );
};
