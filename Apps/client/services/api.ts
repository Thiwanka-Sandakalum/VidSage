import apiClient from '../config/api.config';
import {
  ProcessVideoRequest,
  ProcessVideoResponse,
  SearchRequest,
  SearchResponse,
  GenerateRequest,
  GenerateResponse,
  ListVideosResponse,
  StatsResponse,
  HealthResponse,
  VideoDisplayMetadata,
  SuggestQuestionsRequest,
  SuggestQuestionsResponse,
} from '../types';


/**
 * Save a video for the current user (no re-processing)
 */
export const saveVideo = async (videoId: string): Promise<{ status: string; video_id: string }> => {
  const response = await apiClient.post<{ status: string; video_id: string }>(
    '/videos/save',
    { video_id: videoId }
  );
  return response.data;
};


/**
 * Process a YouTube video (extract transcript, chunk, embed, store)
 */
export const processVideo = async (url: string): Promise<ProcessVideoResponse> => {
  const request: ProcessVideoRequest = { url };
  const response = await apiClient.post<ProcessVideoResponse>('/process', request);
  return response.data;
};

/**
 * Search for relevant chunks within a video
 */
export const searchVideo = async (
  videoId: string,
  query: string,
  topK: number = 2  // Reduced default from 5 to 2 to minimize API quota usage
): Promise<SearchResponse> => {
  const request: SearchRequest = {
    video_id: videoId,
    query,
    top_k: topK,
  };
  const response = await apiClient.post<SearchResponse>('/search', request);
  return response.data;
};

/**
 * Generate AI answer based on video content using RAG
 */
export const generateAnswer = async (
  videoId: string,
  query: string,
  topK: number = 4
): Promise<GenerateResponse> => {
  const request: GenerateRequest = {
    video_id: videoId,
    query,
    top_k: topK,
    stream: false,
  };
  const response = await apiClient.post<GenerateResponse>('/generate', request);
  return response.data;
};

/**
 * List all processed videos
 */
export const listVideos = async (): Promise<ListVideosResponse> => {
  const response = await apiClient.get<ListVideosResponse>('/videos');
  return response.data;
};

/**
 * Delete a video and its embeddings
 */
export const deleteVideo = async (videoId: string): Promise<void> => {
  await apiClient.delete(`/videos/${videoId}`);
};

/**
 * Get database statistics
 */
export const getStats = async (): Promise<StatsResponse> => {
  const response = await apiClient.get<StatsResponse>('/stats');
  return response.data;
};

/**
 * Health check
 */
export const healthCheck = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

// ============================================
// Helper Functions
// ============================================

/**
 * Extract YouTube video ID from URL
 */
export const extractYoutubeId = (url: string): string | null => {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
};

/**
 * Get YouTube video metadata from video ID
 * This creates display metadata for the UI
 */
export const getVideoDisplayMetadata = (
  videoId: string,
  title: string = '',
  chunksCount: number = 0,
  status: string = 'completed'
): VideoDisplayMetadata => {
  return {
    videoId,
    title: title || `Video ${videoId}`,
    thumbnail: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
    channel: 'YouTube', // Could be enhanced with YouTube Data API
    viewCount: undefined,
    publishedAt: undefined,
    chunksCount,
    status,
  };
};

/**
 * Get suggested questions for a video
 */
export const getSuggestedQuestions = async (
  videoId: string,
  count: number = 5
): Promise<SuggestQuestionsResponse> => {
  const request: SuggestQuestionsRequest = {
    video_id: videoId,
    count,
  };
  const response = await apiClient.post<SuggestQuestionsResponse>(
    '/api/suggestions/questions',
    request
  );
  return response.data;
};

/**
 * Format error message from API error
 */
export const formatApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};