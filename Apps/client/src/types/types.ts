
export interface VideoMetadata {
  id: string;
  title: string;
  thumbnail: string;
  description: string;
  duration: string;
  author: string;
  publishedAt: string;
  chunksCount?: number;
  status: 'completed' | 'processing' | 'failed';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  sources?: SourceChunk[];
}

export interface SourceChunk {
  chunk_id: string;
  relevance_score: number;
  text_preview: string;
}

export enum ProcessStatus {
  IDLE = 'IDLE',
  EXTRACTING = 'EXTRACTING',
  TRANSCRIBING = 'TRANSCRIBING',
  ANALYZING = 'ANALYZING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

export interface VideoState {
  currentVideo: VideoMetadata | null;
  transcript: string;
  summary: string;
  suggestedQuestions: string[];
  status: ProcessStatus;
  progress: number;
  error: string | null;
  history: VideoMetadata[];
  stats: {
    total_videos: number;
    total_chunks: number;
    total_users: number;
  } | null;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

export interface ToolIntegration {
  id: string;
  name: string;
  description: string;
  icon: string;
  isConnected: boolean;
  color: string;
}

export interface ToolsState {
  integrations: ToolIntegration[];
  loading: boolean;
  error: string | null;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
