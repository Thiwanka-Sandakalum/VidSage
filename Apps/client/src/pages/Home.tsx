
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Box } from '@mantine/core';
import ErrorDisplay from '../components/common/ErrorDisplay';
import ProcessingState from '../components/common/ProcessingState';
import HeroSection from '../components/home/HeroSection';
import StatsSection from '../components/home/StatsSection';
import RecentVideosSection from '../components/home/RecentVideosSection';
import { useAppDispatch, useAppSelector } from '../hooks';
import { fetchStats, fetchHistory, resetVideoState, processVideo } from '../store/videoSlice';
import { ProcessStatus } from '../types/types';

interface VideoFormData {
  url: string;
}

const Home: React.FC = () => {
  const { control, handleSubmit, formState: { errors }, reset } = useForm<VideoFormData>({
    defaultValues: {
      url: ''
    }
  });
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { status, progress, history, error, stats } = useAppSelector((state) => state.video);
  const [statsLoading, setStatsLoading] = React.useState(true);
  const [historyLoading, setHistoryLoading] = React.useState(true);

  useEffect(() => {
    dispatch(fetchStats()).finally(() => setStatsLoading(false));
    dispatch(fetchHistory()).finally(() => setHistoryLoading(false));
  }, [dispatch]);

  const onSubmit = (data: VideoFormData) => {
    dispatch(resetVideoState());
    dispatch(processVideo(data.url)).then((result) => {
      if (processVideo.fulfilled.match(result)) {
        navigate(`/video/${result.payload.video.id}`);
        reset();
      }
    });
  };

  const handleRetry = () => {
    handleSubmit(onSubmit)();
  };

  const isProcessing = status !== ProcessStatus.IDLE && status !== ProcessStatus.COMPLETED && status !== ProcessStatus.FAILED;

  if (isProcessing) return <ProcessingState status={status} progress={progress} />;

  return (
    <div>
      <HeroSection
        control={control}
        errors={errors}
        handleSubmit={handleSubmit}
        onSubmit={onSubmit}
        isProcessing={isProcessing}
      />
      {error && (
        <Box w="100%" maw={720} mx="auto">
          <ErrorDisplay
            title="Analysis Failed"
            message={error}
            onRetry={handleRetry}
          />
        </Box>
      )}
      <StatsSection stats={stats} loading={statsLoading} />
      <RecentVideosSection videos={history} loading={historyLoading} />
    </div>
  );
};

export default Home;
