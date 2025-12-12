import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import {
    ProcessingStep,
    VideoDisplayMetadata,
    ChatMessage,
    TranscriptSegment,
    VideoMetadata,
    AppView
} from '../types';
import {
    processVideo,
    generateAnswer,
    listVideos,
    deleteVideo as deleteVideoApi,
    getVideoDisplayMetadata,
    getSuggestedQuestions,
    formatApiError,
} from '../services/api';

interface AppContextType {
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
    currentSeekTime: number | null;
    suggestedQuestions: string[];

    // Actions
    toggleDarkMode: () => void;
    setView: (view: AppView) => void;
    setVideoUrl: (url: string) => void;
    setVideoId: (id: string | null) => void;
    enterApp: () => void;
    startProcessing: (videoId: string) => Promise<void>;
    resetApp: () => void;
    addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
    askQuestion: (question: string) => Promise<void>;
    seekVideo: (seconds: number) => void;
    clearSeek: () => void;
    loadVideos: () => Promise<void>;
    deleteVideo: (videoId: string) => Promise<void>;
    loadSuggestedQuestions: (videoId: string) => Promise<void>;
    loadVideoById: (videoId: string) => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [view, setView] = useState<AppView>('landing');
    const [darkMode, setDarkMode] = useState(false);
    const [videoUrl, setVideoUrlState] = useState('');
    const [videoId, setVideoIdState] = useState<string | null>(null);
    const [metadata, setMetadata] = useState<VideoDisplayMetadata | null>(null);
    const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
    const [processingStep, setProcessingStep] = useState<ProcessingStep>('idle');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isChatLoading, setIsChatLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [processedVideos, setProcessedVideos] = useState<VideoMetadata[]>([]);
    const [currentSeekTime, setCurrentSeekTime] = useState<number | null>(null);
    const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);

    const toggleDarkMode = useCallback(() => {
        setDarkMode(prev => {
            const newMode = !prev;
            if (newMode) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
            return newMode;
        });
    }, []);

    const setVideoUrl = useCallback((url: string) => {
        setVideoUrlState(url);
        setError(null);
    }, []);

    const setVideoId = useCallback((id: string | null) => {
        setVideoIdState(id);
    }, []);

    const enterApp = useCallback(() => {
        setView('home');
    }, []);

    const resetApp = useCallback(() => {
        setView('landing');
        setVideoUrlState('');
        setVideoIdState(null);
        setMetadata(null);
        setTranscript([]);
        setProcessingStep('idle');
        setMessages([]);
        setError(null);
    }, []);

    const startProcessing = useCallback(async (id: string) => {
        setProcessingStep('fetching');
        setVideoIdState(id);
        setError(null);

        try {
            // Simulate UI steps
            const steps: ProcessingStep[] = ['fetching', 'chunking', 'embedding', 'saving'];

            for (let i = 0; i < steps.length; i++) {
                setProcessingStep(steps[i]);
                if (i === 0) {
                    await new Promise(r => setTimeout(r, 500));
                } else {
                    await new Promise(r => setTimeout(r, 800));
                }
            }

            const response = await processVideo(videoUrl);

            const displayMetadata = getVideoDisplayMetadata(
                response.video_id,
                `Video ${response.video_id}`,
                response.chunks_count,
                response.status
            );

            setMetadata(displayMetadata);
            setVideoIdState(response.video_id);
            setProcessingStep('complete');
            setMessages([
                {
                    id: 'welcome-msg',
                    role: 'ai',
                    content: `Hello! 👋 I've analyzed this video and I'm ready to help. You can ask me:\n\n• What's this video about?\n• Summarize the main points\n• Explain specific topics\n• Find information on...\n\nWhat would you like to know?`,
                    timestamp: Date.now()
                }
            ]);

            setTimeout(() => {
                window.location.href = `/dashboard/${response.video_id}`;
            }, 500);

        } catch (err: any) {
            const errorMessage = formatApiError(err);
            console.error('Processing Error:', errorMessage);
            setError('Unable to process this video. Please check the URL and try again.');
            setProcessingStep('idle');
        }
    }, [videoUrl]);

    const addMessage = useCallback((msg: Omit<ChatMessage, 'id' | 'timestamp'>) => {
        setMessages(prev => [...prev, {
            ...msg,
            id: crypto.randomUUID(),
            timestamp: Date.now()
        }]);
    }, []);

    const askQuestion = useCallback(async (question: string) => {
        if (!videoId) {
            console.error('No video ID available');
            return;
        }

        addMessage({ role: 'user', content: question });
        setIsChatLoading(true);

        try {
            const response = await generateAnswer(videoId, question, 4);
            addMessage({
                role: 'ai',
                content: response.answer
            });
        } catch (err) {
            const errorMessage = formatApiError(err);
            addMessage({
                role: 'ai',
                content: `I apologize, but I'm having trouble answering that question right now. Please try again or rephrase your question.`
            });
            console.error('AI Error:', errorMessage);
        } finally {
            setIsChatLoading(false);
        }
    }, [videoId, addMessage]);

    const seekVideo = useCallback((seconds: number) => {
        setCurrentSeekTime(seconds);
    }, []);

    const clearSeek = useCallback(() => {
        setCurrentSeekTime(null);
    }, []);

    const loadVideos = useCallback(async () => {
        try {
            const response = await listVideos();
            setProcessedVideos(response.videos);
        } catch (err) {
            console.error('Failed to load videos:', formatApiError(err));
        }
    }, []);

    const deleteVideo = useCallback(async (videoId: string) => {
        try {
            await deleteVideoApi(videoId);
            setProcessedVideos(prev => prev.filter(v => v.video_id !== videoId));
        } catch (err) {
            console.error('Failed to delete video:', formatApiError(err));
            throw err;
        }
    }, []);

    const loadSuggestedQuestions = useCallback(async (videoId: string) => {
        try {
            const response = await getSuggestedQuestions(videoId, 5);
            setSuggestedQuestions(response.questions);
        } catch (err) {
            console.error('Failed to load suggested questions:', formatApiError(err));
            setSuggestedQuestions([
                "What's this video about?",
                "Can you summarize the main points?",
                "What are the key takeaways?",
                "Tell me something interesting from this video"
            ]);
        }
    }, []);

    const loadVideoById = useCallback(async (videoId: string) => {
        try {
            setVideoIdState(videoId);
            // Load video metadata from backend
            const videos = await listVideos();
            const video = videos.videos.find(v => v.video_id === videoId);

            if (video) {
                const displayMetadata = getVideoDisplayMetadata(
                    video.video_id,
                    video.title,
                    video.chunks_count,
                    video.status
                );
                setMetadata(displayMetadata);

                // Load suggested questions
                await loadSuggestedQuestions(videoId);

                // Set welcome message
                setMessages([
                    {
                        id: 'welcome-msg',
                        role: 'ai',
                        content: `Hello! 👋 I've loaded this video and I'm ready to help. You can ask me:\n\n• What's this video about?\n• Summarize the main points\n• Explain specific topics\n• Find information on...\n\nWhat would you like to know?`,
                        timestamp: Date.now()
                    }
                ]);
            } else {
                setError('Video not found');
            }
        } catch (err) {
            console.error('Failed to load video:', formatApiError(err));
            setError('Failed to load video');
        }
    }, [loadSuggestedQuestions]);

    const value: AppContextType = {
        view,
        darkMode,
        videoUrl,
        videoId,
        metadata,
        transcript,
        processingStep,
        messages,
        isChatLoading,
        error,
        processedVideos,
        currentSeekTime,
        suggestedQuestions,
        toggleDarkMode,
        setView,
        setVideoUrl,
        setVideoId,
        enterApp,
        startProcessing,
        resetApp,
        addMessage,
        askQuestion,
        seekVideo,
        clearSeek,
        loadVideos,
        deleteVideo,
        loadSuggestedQuestions,
        loadVideoById,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Custom hook to use the context
export const useApp = () => {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
};