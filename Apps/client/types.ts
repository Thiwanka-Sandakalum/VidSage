// ============================================
// API Request/Response Types (aligned with backend)
// ============================================

export interface ProcessVideoRequest {
  url: string;
}

export interface ProcessVideoResponse {
  video_id: string;
  status: 'completed' | 'already_processed' | 'processing';
  chunks_count: number;
}

export interface SearchRequest {
  video_id: string;
  query: string;
  top_k?: number;
}

export interface SearchResult {
  chunk_id: string;
  text: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface SearchResponse {
  results: SearchResult[];
}

export interface GenerateRequest {
  query: string;
  video_id: string;
  top_k?: number;
  stream?: boolean;
}

export interface SourceChunk {
  chunk_id: string;
  relevance_score: number;
  text_preview: string;
}

export interface GenerateResponse {
  answer: string;
  sources: SourceChunk[];
  model: string;
}

export interface VideoMetadata {
  video_id: string;
  title: string;
  chunks_count: number;
  status: string;
}

export interface ListVideosResponse {
  videos: VideoMetadata[];
}

export interface ErrorResponse {
  detail: string;
  error?: string;
}

export interface StatsResponse {
  total_videos: number;
  total_chunks: number;
  total_embeddings: number;
}

export interface HealthResponse {
  status: string;
  api_key_configured: boolean;
  mongodb_uri_configured: boolean;
  mongodb_connected: boolean;
}

export interface SuggestQuestionsRequest {
  video_id: string;
  count?: number;
}

export interface SuggestQuestionsResponse {
  video_id: string;
  questions: string[];
  count: number;
}

// ============================================
// UI-Specific Types
// ============================================

export interface VideoDisplayMetadata {
  videoId: string;
  title: string;
  channel?: string;
  thumbnail: string;
  viewCount?: string;
  publishedAt?: string;
  chunksCount?: number;
  status?: string;
}

export interface TranscriptSegment {
  id: number;
  start: number;
  end: number;
  text: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: number;
  sources?: SourceChunk[];
}

export type ProcessingStep = 'idle' | 'fetching' | 'chunking' | 'embedding' | 'saving' | 'complete';

export type AppView = 'landing' | 'home' | 'processing' | 'dashboard' | 'library';

// ============================================
// App State
// ============================================

export interface AppState {
  // State
  view: AppView;
  darkMode: boolean;
  videoUrl: string;
  videoId: string | null;
  metadata: VideoDisplayMetadata | null;
  transcript: TranscriptSegment[];
  processingStep: ProcessingStep;
  messages: ChatMessage[];
  isChatLoading: boolean;
  error: string | null;
  processedVideos: VideoMetadata[];

  // Actions
  toggleDarkMode: () => void;
  setView: (view: AppView) => void;
  setVideoUrl: (url: string) => void;
  enterApp: () => void;
  startProcessing: (videoId: string) => Promise<void>;
  resetApp: () => void;
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  askQuestion: (question: string) => Promise<void>;
  seekVideo: (seconds: number) => void;
  loadVideos: () => Promise<void>;
  deleteVideo: (videoId: string) => Promise<void>;

  // Player Ref
  currentSeekTime: number | null;
  clearSeek: () => void;
}