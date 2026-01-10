/**
 * YouTube Service
 * Provides YouTube video metadata and details
 */

interface VideoDetails {
    title: string;
    author: string;
    thumbnail: string;
    description: string;
    duration: string;
    publishedAt: string;
}

interface YouTubeService {
    getVideoDetails: (videoId: string) => Promise<VideoDetails>;
}

/**
 * Extract video ID from YouTube URL or return as-is if already an ID
 */
function extractVideoId(videoIdOrUrl: string): string {
    if (videoIdOrUrl.includes('youtube.com') || videoIdOrUrl.includes('youtu.be')) {
        const url = new URL(videoIdOrUrl);
        return url.searchParams.get('v') || url.pathname.split('/').pop() || videoIdOrUrl;
    }
    return videoIdOrUrl;
}

/**
 * Format duration from seconds to MM:SS or HH:MM:SS
 */
function formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

export const youtubeService: YouTubeService = {
    /**
     * Get video details from YouTube
     * Note: This uses oEmbed API which has limited data
     * For production, consider using YouTube Data API v3
     */
    async getVideoDetails(videoId: string): Promise<VideoDetails> {
        try {
            const id = extractVideoId(videoId);

            // Use YouTube oEmbed API (no API key required, but limited data)
            const oembedUrl = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${id}&format=json`;
            const response = await fetch(oembedUrl);

            if (!response.ok) {
                throw new Error('Failed to fetch video details');
            }

            const data = await response.json();

            return {
                title: data.title || 'Untitled Video',
                author: data.author_name || 'Unknown',
                thumbnail: data.thumbnail_url || `https://i.ytimg.com/vi/${id}/hqdefault.jpg`,
                description: '',
                duration: '0:00', // oEmbed doesn't provide duration
                publishedAt: new Date().toISOString()
            };
        } catch (error) {
            console.error('Failed to fetch YouTube video details:', error);

            // Return fallback data
            const id = extractVideoId(videoId);
            return {
                title: 'Video',
                author: 'Unknown',
                thumbnail: `https://i.ytimg.com/vi/${id}/hqdefault.jpg`,
                description: '',
                duration: '0:00',
                publishedAt: new Date().toISOString()
            };
        }
    }
};

export default youtubeService;
