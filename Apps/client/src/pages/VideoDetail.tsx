import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ToolsService } from '../services/services/ToolsService';
import { Box, Stack, Paper, Group, Text, Center, Button, Grid, AspectRatio, useMantineColorScheme, Tooltip, ActionIcon, Modal } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import ChatPanel from '../components/videoDetail/ChatPanel';
import VideoDetailSkeleton from '../components/videoDetail/VideoDetailSkeleton';
import VideoHeader from '../components/videoDetail/VideoHeader';
import ToolActions from '../components/videoDetail/ToolActions';
import QuickQueries from '../components/videoDetail/QuickQueries';
import { useAppDispatch, useAppSelector } from '../hooks';
import { addUserMessage, sendMessage, clearChat } from '../store/chatSlice';
import { store } from '../store/store';
import { fetchVideoSummary } from '../store/summarySlice';
import { selectVideoFromHistory, fetchHistory, fetchSuggestedQuestions, processVideo, deleteVideo } from '../store/videoSlice';
import geminiService from '../services/geminiService';
import AIInsightsSection from '../components/common/AIInsightsSectionProps';
import youtubeService from '../services/youtubeService';
import ErrorDisplay from '../components/common/ErrorDisplay';


interface ChatFormData {
  message: string;
}

const VideoDetail: React.FC = () => {

  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { colorScheme } = useMantineColorScheme();
  const isDark = colorScheme === 'dark';
  const { messages, isLoading: isChatLoading, error: chatError } = useAppSelector((state) => state.chat);
  const { integrations } = useAppSelector((state) => state.tools);

  // Grouped state for chat UI
  const [chatUI, setChatUI] = useState({
    isChatMaximized: false,
    isSpeaking: false,
  });

  // Grouped state for tool sync
  const [syncingTools, setSyncingTools] = useState<Set<string>>(new Set());

  // Grouped state for save actions
  const [saveState, setSaveState] = useState({
    saving: false,
    saveError: null as string | null,
    saveSuccess: false,
    docLink: '',
    disableSave: false,
    documents: [] as any[],
  });


  const { currentVideo, transcript, status, error: videoError, suggestedQuestions } = useAppSelector((state) => state.video);

  // State for YouTube details
  const [ytDetails, setYtDetails] = useState<{ title?: string; author?: string; publishedAt?: string }>({});

  // Format ISO date string to readable date
  function formatDate(dateStr?: string) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }

  // Fetch YouTube details if video id is present
  useEffect(() => {
    if (id) {
      youtubeService.getVideoDetails(id).then((details: any) => {
        setYtDetails({
          title: details?.title,
          author: details?.author,
          publishedAt: details?.publishedAt
        });
      }).catch(() => {
        setYtDetails({});
      });
    }
  }, [id]);


  const { control, handleSubmit, formState: { errors }, reset } = useForm<ChatFormData>({
    defaultValues: {
      message: ''
    }
  });

  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        const result = await ToolsService.getSummaryDocLinkToolsSummaryDocLinkGet(id);
        if (result && result.exists && result.doc_link) {
          setSaveState((prev) => ({
            ...prev,
            docLink: result.doc_link,
            documents: result.documents || [],
            saveSuccess: true,
          }));
        } else {
          setSaveState((prev) => ({
            ...prev,
            docLink: '',
            documents: [],
            saveSuccess: false,
          }));
        }
      } catch (err) {
        setSaveState((prev) => ({
          ...prev,
          docLink: '',
          documents: [],
          saveSuccess: false,
        }));
      }
    })();
  }, [id]);

  const viewportRef = useRef<HTMLDivElement>(null);
  const maximizedViewportRef = useRef<HTMLDivElement>(null);
  // Handler for saving summary to Google Doc
  const handleSaveSummaryToDoc = async () => {
    if (!id) return;
    setSaveState((prev) => ({ ...prev, saving: true, saveError: null, saveSuccess: false }));
    try {
      await ToolsService.saveSummaryToDocToolsSaveSummaryToDocPost({ video_id: id });
      setSaveState((prev) => ({ ...prev, saveSuccess: true, disableSave: true }));
      notifications.show({
        title: 'Google Doc Created',
        message: 'The summary was saved to Google Docs.',
        color: 'green',
      });
      // Fetch updated doc link
      const result = await ToolsService.getSummaryDocLinkToolsSummaryDocLinkGet(id);
      if (result && result.exists && result.doc_link) {
        setSaveState((prev) => ({ ...prev, docLink: result.doc_link }));
      }
    } catch (err: any) {
      setSaveState((prev) => ({ ...prev, saveError: err?.body?.message || 'Failed to save summary to Google Doc.' }));
    } finally {
      setSaveState((prev) => ({ ...prev, saving: false }));
    }
  };

  const connectedTools = integrations.filter(t => t.isConnected);

  // Load video from history if not in state
  useEffect(() => {
    if (id && !currentVideo) {
      // Check if video exists in history
      const { history } = store.getState().video;
      const videoInHistory = history.find(v => v.id === id);

      if (videoInHistory) {
        // Select video from history
        dispatch(selectVideoFromHistory(videoInHistory));
      } else if (history.length === 0) {
        // Fetch history first to see if video exists
        dispatch(fetchHistory()).then((result) => {
          if (result.payload && Array.isArray(result.payload)) {
            const foundVideo = result.payload.find((v: any) => v.id === id);
            if (foundVideo) {
              dispatch(selectVideoFromHistory(foundVideo));
            } else {
              // Video not found in history, redirect to home
              notifications.show({
                title: 'Video Not Found',
                message: 'This video is not in your history. Please process it first.',
                color: 'red',
              });
              navigate('/');
            }
          }
        });
      } else {
        // History loaded but video not found
        notifications.show({
          title: 'Video Not Found',
          message: 'This video is not in your history. Please process it first.',
          color: 'red',
        });
        navigate('/');
      }
    }
  }, [id, currentVideo, dispatch, navigate]);

  // Fetch suggested questions when video is loaded
  useEffect(() => {
    if (id && currentVideo && suggestedQuestions.length === 0) {
      dispatch(fetchSuggestedQuestions(id));
    }
  }, [id, currentVideo, dispatch, suggestedQuestions.length]);

  // Fetch summary when video is loaded
  const summaryState = useAppSelector((state) => state.summary);
  useEffect(() => {
    if (id && currentVideo && !summaryState.summary && !summaryState.loading) {
      dispatch(fetchVideoSummary(id));
    }
  }, [id, currentVideo, dispatch, summaryState.summary, summaryState.loading]);

  useEffect(() => {
    if (viewportRef.current) {
      viewportRef.current.scrollTo({ top: viewportRef.current.scrollHeight, behavior: 'smooth' });
    }
    if (maximizedViewportRef.current) {
      maximizedViewportRef.current.scrollTo({ top: maximizedViewportRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, chatUI.isChatMaximized]);

  const onSendMessage = (data: ChatFormData) => {
    if (!id || isChatLoading) return;

    dispatch(addUserMessage(data.message));
    dispatch(sendMessage({ message: data.message, videoId: id, transcript }));
    reset();
  };

  const handleSuggestedQuestion = (question: string) => {
    if (!id || isChatLoading) return;

    dispatch(addUserMessage(question));
    dispatch(sendMessage({ message: question, videoId: id, transcript }));
  };

  const handleRetryVideo = () => {
    if (id) dispatch(processVideo(id));
  };

  const handleRetryChat = () => {
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMsg && id) {
      dispatch(sendMessage({ message: lastUserMsg.content, videoId: id, transcript }));
    }
  };

  const handleSave = async () => {
    if (!id) return;
    setSaveState((prev) => ({ ...prev, saving: true, saveError: null, saveSuccess: false }));
    try {
      setSaveState((prev) => ({ ...prev, saveSuccess: true }));
      notifications.show({
        title: 'Saved',
        message: 'Video saved to your library.',
        color: 'green',
        icon: <i className="fas fa-bookmark"></i>,
      });
    } catch (e: any) {
      setSaveState((prev) => ({ ...prev, saveError: e.message || 'Failed to save video' }));
      notifications.show({
        title: 'Save Failed',
        message: e.message || 'Failed to save video',
        color: 'red',
        icon: <i className="fas fa-times"></i>,
      });
    } finally {
      setSaveState((prev) => ({ ...prev, saving: false }));
    }
  };

  const [deleteModal, setDeleteModal] = useState({ open: false, deleting: false });
  const handleDelete = async () => {
    setDeleteModal((prev) => ({ ...prev, deleting: true }));
    try {
      dispatch(deleteVideo(id!));
      navigate('/history');
    } finally {
      setDeleteModal({ open: false, deleting: false });
    }
  };

  const handleToolSync = async (toolId: string, toolName: string) => {
    if (syncingTools.has(toolId)) return;

    setSyncingTools(prev => new Set(prev).add(toolId));

    await new Promise(resolve => setTimeout(resolve, 1500));

    const isSuccess = Math.random() > 0.1;

    setSyncingTools(prev => {
      const next = new Set(prev);
      next.delete(toolId);
      return next;
    });

    if (isSuccess) {
      notifications.show({
        title: 'Sync Successful',
        message: `Analysis successfully exported to ${toolName}.`,
        color: 'green',
        icon: <i className="fas fa-check"></i>,
      });
    } else {
      notifications.show({
        title: 'Sync Failed',
        message: `Could not reach ${toolName}. Please check your integration settings.`,
        color: 'red',
        icon: <i className="fas fa-times"></i>,
      });
    }
  };

  const handleTTS = async () => {
    if (chatUI.isSpeaking) return;

    const summaryText = summaryState.summary;
    if (!summaryText) {
      notifications.show({
        title: 'No Summary',
        message: 'There is no summary to read aloud.',
        color: 'red',
      });
      return;
    }
    setChatUI((prev) => ({ ...prev, isSpeaking: true }));
    try {
      const audioData = await geminiService.textToSpeech(summaryText, {
        voiceName: 'Kore',
      });
      if (audioData && audioData.byteLength > 0) {
        const ctx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
        const dataInt16 = new Int16Array(audioData);
        const buffer = ctx.createBuffer(1, dataInt16.length, 24000);
        buffer.getChannelData(0).set(Array.from(dataInt16).map(v => v / 32768.0));
        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.onended = () => setChatUI((prev) => ({ ...prev, isSpeaking: false }));
        source.start();
      } else {
        notifications.show({
          title: 'TTS Error',
          message: 'No audio data returned from Gemini TTS API.',
          color: 'red',
        });
        setChatUI((prev) => ({ ...prev, isSpeaking: false }));
      }
    } catch (err: any) {
      notifications.show({
        title: 'TTS Error',
        message: err?.message || 'Failed to generate audio from Gemini TTS API.',
        color: 'red',
      });
      setChatUI((prev) => ({ ...prev, isSpeaking: false }));
    }
  };


  if (status === 'FAILED') {
    return (
      <Center py={100}>
        <Stack align="center" maw={500} w="100%">
          <ErrorDisplay
            title="Analysis Failure"
            message={videoError || "We encountered an unexpected error while analyzing this video."}
            onRetry={handleRetryVideo}
            variant="filled"
          />
          <Button variant="subtle" color="gray" onClick={() => navigate('/')}>Back to Home</Button>
        </Stack>
      </Center>
    );
  }

  if (!currentVideo) {
    return <VideoDetailSkeleton />;
  }

  return (
    <Box pb={80}>
      <Grid gutter="xl">
        <Grid.Col span={{ base: 12, lg: 8 }}>
          <Stack gap="xl">
            <Paper radius="xl" style={{ overflow: 'hidden' }} shadow="xl">
              <AspectRatio ratio={16 / 9}>
                <iframe
                  src={`https://www.youtube.com/embed/${id}`}
                  title="Video Player"
                  allowFullScreen
                />
              </AspectRatio>
            </Paper>

            <Group justify="space-between" align="flex-start">
              <VideoHeader
                title={ytDetails.title}
                author={ytDetails.author}
                publishedAt={ytDetails.publishedAt}
                fallbackTitle={currentVideo.title}
                fallbackAuthor={currentVideo.author}
                fallbackPublishedAt={currentVideo.publishedAt}
                formatDate={formatDate}
              />
              <ToolActions
                connectedTools={connectedTools}
                syncingTools={syncingTools}
                handleToolSync={handleToolSync}
                setDeleteModal={setDeleteModal}
                deleteModal={deleteModal}
                handleDelete={handleDelete}
                saveState={saveState}
                handleSave={handleSave}
                isDark={isDark}
              />
            </Group>

            <AIInsightsSection
              summaryState={summaryState}
              isSpeaking={chatUI.isSpeaking}
              saving={saveState.saving}
              saveError={saveState.saveError}
              docLink={saveState.docLink}
              handleTTS={handleTTS}
              handleSaveSummaryToDoc={handleSaveSummaryToDoc}
              disableSave={saveState.disableSave}
            />

            <QuickQueries
              suggestedQuestions={suggestedQuestions}
              isDark={isDark}
              handleSuggestedQuestion={handleSuggestedQuestion}
            />
          </Stack>
        </Grid.Col>

        <Grid.Col span={{ base: 12, lg: 4 }}>
          <Paper
            radius="xl"
            withBorder
            shadow="lg"
            h={{ base: 600, lg: 'calc(100vh - 120px)' }}
            style={{
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              position: 'sticky',
              top: 90,
              background: isDark ? 'rgba(28, 29, 38, 0.98)' : 'rgba(255, 255, 255, 0.98)',
              color: isDark ? 'var(--mantine-color-gray-0)' : 'var(--mantine-color-dark-7)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'var(--mantine-color-dark-5)' : 'var(--mantine-color-gray-2)'}`
            }}
          >
            <Box
              p="md"
              style={{
                borderBottom: `1px solid ${isDark ? 'var(--mantine-color-dark-4)' : 'var(--mantine-color-gray-2)'}`,
                background: isDark ? 'rgba(36, 37, 46, 0.98)' : 'var(--mantine-color-gray-0)',
                color: isDark ? 'var(--mantine-color-gray-0)' : 'var(--mantine-color-dark-7)'
              }}
            >
              <Group justify="space-between">
                <Group gap="xs">
                  <Box bg="indigo.6" p={6} style={{ borderRadius: '6px', display: 'flex', color: 'white' }}>
                    <i className="fas fa-robot text-xs"></i>
                  </Box>
                  <Text fw={800} size="sm">RAG Engine</Text>
                </Group>
                <Group gap={4}>
                  <Tooltip label="Maximize Chat">
                    <ActionIcon variant="subtle" color={isDark ? 'gray' : 'dark'} onClick={() => setChatUI((prev) => ({ ...prev, isChatMaximized: true }))}>
                      <i className="fas fa-expand-alt"></i>
                    </ActionIcon>
                  </Tooltip>
                  <Tooltip label="Clear History">
                    <ActionIcon variant="subtle" color={isDark ? 'gray' : 'dark'} onClick={() => dispatch(clearChat())}>
                      <i className="fas fa-eraser"></i>
                    </ActionIcon>
                  </Tooltip>
                </Group>
              </Group>
            </Box>

            {/* ChatPanel renders messages using ChatBubble component */}
            <ChatPanel
              scrollRef={viewportRef}
              messages={messages}
              isLoading={isChatLoading}
              error={chatError}
              onSendMessage={onSendMessage}
              onRetry={handleRetryChat}
              control={control}
              errors={errors}
              handleSubmit={handleSubmit}
            />
          </Paper>
        </Grid.Col>
      </Grid>

      {/* Maximized Chat Modal */}
      <Modal
        opened={chatUI.isChatMaximized}
        onClose={() => setChatUI((prev) => ({ ...prev, isChatMaximized: false }))}
        size="70%"
        radius="lg"
        title={
          <Group gap="xs">
            <Box bg="indigo.6" p={6} style={{ borderRadius: '6px', display: 'flex', color: 'white' }}>
              <i className="fas fa-robot text-xs"></i>
            </Box>
            <Text fw={800}>Full Context Analysis Chat</Text>
          </Group>
        }
        styles={{
          header: {
            borderBottom: '1px solid var(--mantine-color-gray-2)',
            padding: '1.5rem',
          },
          body: {
            height: '80vh',
            display: 'flex',
            flexDirection: 'column',
            padding: 0
          }
        }}
      >
        <Box style={{ flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: isDark ? 'var(--mantine-color-dark-7)' : 'var(--mantine-color-gray-0)' }}>
          <ChatPanel
            scrollRef={maximizedViewportRef}
            messages={messages}
            isLoading={isChatLoading}
            error={chatError}
            onSendMessage={onSendMessage}
            onRetry={handleRetryChat}
            control={control}
            errors={errors}
            handleSubmit={handleSubmit}
          />
        </Box>
      </Modal>
    </Box>
  );
};

export default VideoDetail;
