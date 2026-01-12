/**
 * API Service Adapter
 * Wraps OpenAPI-generated services for use throughout the application
 */

import type { VideoMetadata as APIVideoMetadata } from './main/models/VideoMetadata';
import type { SourceChunk } from './main/models/SourceChunk';
import type { VideoMetadata } from '../types/types';
import { GenerateService, StatsService, SuggestionsService, VideosService, IntegrationsService, OpenAPI } from '.';


/**
 * Transform API VideoMetadata to app VideoMetadata format
 */
const transformVideoMetadata = (apiVideo: APIVideoMetadata): VideoMetadata => {
    return {
        id: apiVideo.video_id,
        title: apiVideo.title || 'Untitled Video',
        thumbnail: `https://i.ytimg.com/vi/${apiVideo.video_id}/hqdefault.jpg`,
        description: '',
        duration: '0:00',
        author: 'Unknown',
        publishedAt: new Date().toISOString(),
        chunksCount: apiVideo.chunks_count,
        status: apiVideo.status as 'completed' | 'processing' | 'failed'
    };
};

/**
 * API Service for application
 */
export const api = {
    /**
     * Process a YouTube video
     */
    async processVideo(videoUrl: string) {
        try {
            const response = await VideosService.processVideoVideosProcessPost({
                url: videoUrl
            });

            // Store last process result globally for disclaimer notification
            (window as any).lastProcessVideoResult = response;

            // Fetch full video details after processing
            const videos = await VideosService.listVideosVideosGet();
            const video = videos.videos?.find(v => v.video_id === response.video_id);

            if (!video) {
                throw new Error('Video processed but metadata not found');
            }

            // Get suggested questions
            let questions: string[] = [];
            try {
                const suggestionsResponse = await SuggestionsService.getSuggestionsSuggestionsVideoIdGet(
                    response.video_id
                );
                questions = suggestionsResponse.questions || [];
            } catch (error) {
                console.warn('Failed to fetch suggested questions:', error);
            }

            return {
                video: transformVideoMetadata(video),
                transcript: '', // Transcript not returned by API
                summary: '', // Summary not returned by API
                questions
            };
        } catch (error: any) {
            console.error('Process video error:', error);
            throw new Error(error.message || 'Failed to process video');
        }
    },

    /**
     * List all videos for the current user
     */
    async listVideos(): Promise<VideoMetadata[]> {
        try {
            const response = await VideosService.listVideosVideosGet();
            return (response.videos || []).map(transformVideoMetadata);
        } catch (error: any) {
            console.error('List videos error:', error);
            throw new Error(error.message || 'Failed to fetch videos');
        }
    },

    /**
     * Delete a video
     */
    async deleteVideo(videoId: string) {
        try {
            await VideosService.deleteVideoVideosVideoIdDelete(videoId);

            return { status: 'deleted' };
        } catch (error: any) {
            console.error('Delete video error:', error);
            throw new Error(error.message || 'Failed to delete video');
        }
    },

    /**
     * Generate an AI answer using RAG
     */
    async generateAnswer(query: string, videoId: string, transcript?: string) {
        try {
            const response = await GenerateService.generateAnswerGeneratePost({
                query,
                video_id: videoId
            });

            return {
                answer: response.answer || '',
                sources: (response.sources || []) as SourceChunk[]
            };
        } catch (error: any) {
            console.error('Generate answer error:', error);
            throw new Error(error.message || 'Failed to generate answer');
        }
    },

    /**
     * Get system statistics
     */
    async getStats() {
        try {
            const stats = await StatsService.getStatsStatsGet();
            return {
                total_videos: stats.total_videos || 0,
                total_chunks: stats.total_chunks || 0,
                total_users: stats.total_users || 0
            };
        } catch (error: any) {
            console.error('Get stats error:', error);
            // Return default stats on error
            return {
                total_videos: 0,
                total_chunks: 0,
                total_users: 0
            };
        }
    },

    /**
     * Get suggested questions for a video
     */
    async getSuggestions(videoId: string): Promise<string[]> {
        try {
            const response = await SuggestionsService.getSuggestionsSuggestionsVideoIdGet(
                videoId
            );
            return response.questions || [];
        } catch (error: any) {
            console.error('Get suggestions error:', error);
            return [];
        }
    },

    /**
     * Save video to user library
     */
    async saveVideo(videoId: string) {
        try {
            await VideosService.saveVideoVideosSavePost({ video_id: videoId });
            return { status: 'saved' };
        } catch (error: any) {
            console.error('Save video error:', error);
            throw new Error(error.message || 'Failed to save video');
        }
    },
    /**
     * Initialize Google OAuth flow
     */
    async connectGoogle() {
        try {

            const res = await IntegrationsService.googleAuthInitIntegrationsGoogleAuthGet();
            console.log('Google Auth Init Response:', res);
            // Redirect to Google OAuth URL
            if (res.authUrl) {
                window.location.href = res.authUrl;
            } else {
                throw new Error('No auth URL returned from server');
            }
        } catch (error: any) {
            console.error('Connect Google error:', error);
            throw new Error(error.message || 'Failed to connect Google');
        }
    },

    /**
     * Check Google connection status
     */
    async getGoogleStatus() {
        try {
            const response = await IntegrationsService.googleAuthStatusIntegrationsGoogleStatusGet();
            return response;
        } catch (error: any) {
            console.error('Get Google status error:', error);
            // Return default status on error
            return { connected: false, scopes: [] };
        }
    },

    /**
     * Disconnect Google account
     */
    async disconnectGoogle() {
        try {
            const response = await IntegrationsService.googleDisconnectIntegrationsGoogleDisconnectDelete();
            return response;
        } catch (error: any) {
            console.error('Disconnect Google error:', error);
            throw new Error(error.message || 'Failed to disconnect Google');
        }
    }
};

export default api;
