
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { VideoMetadata } from '../../types/types';
import GridView from './VideoCard/GridView';
import ListView from './VideoCard/ListView';
import { youtubeService } from '../../services/youtubeService';
import { Button, Group, Modal, Stack, Text, Box } from '@mantine/core';
import { showNotification } from '@mantine/notifications';

interface VideoCardProps {
  video: VideoMetadata;
  onDelete?: (videoId: string) => void;
  viewMode?: 'grid' | 'list';
}

const VideoCard: React.FC<VideoCardProps> = ({ video, onDelete, viewMode = 'grid' }) => {
  const navigate = useNavigate();
  const [enrichedVideo, setEnrichedVideo] = useState(video);
  const [loading, setLoading] = useState(true);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [isDeleted, setIsDeleted] = useState(false);

  useEffect(() => {
    const enrichVideoData = async () => {
      try {
        const details = await youtubeService.getVideoDetails(video.id);
        setEnrichedVideo({
          ...video,
          title: details.title,
          author: details.author,
          thumbnail: details.thumbnail,
          duration: details.duration,
          publishedAt: details.publishedAt
        });
      } catch (error) {
        console.error('Failed to enrich video data:', error);
      } finally {
        setLoading(false);
      }
    };

    enrichVideoData();
  }, [video.id]);

  const handleNavigate = () => navigate(`/video/${video.id}`);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setDeleteModalOpen(true);
  };

  const confirmDelete = () => {
    setIsDeleted(true);
    // Only remove from array after fade-out
    setTimeout(() => {
      if (onDelete) {
        onDelete(video.id);
        showNotification({
          title: 'Video Deleted',
          message: `"${enrichedVideo.title}" was deleted successfully!`,
          color: 'green',
          autoClose: 2500,
        });
      }
      setDeleteModalOpen(false);
    }, 500); // Slightly longer for a smoother effect
  };

  const ViewComponent = viewMode === 'list' ? ListView : GridView;

  return (
    <>
      <Box
        className={`video-card-fade${isDeleted ? ' video-card-fade-out' : ''}`}
        style={{ cursor: 'pointer' }}
        onClick={handleNavigate}
        tabIndex={0}
        role="button"
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') handleNavigate(); }}
      >
        <ViewComponent
          video={enrichedVideo}
          onNavigate={handleNavigate}
          onDelete={onDelete ? handleDelete : undefined}
          loading={loading}
        />
      </Box>

      <Modal
        opened={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Delete Video"
        centered
        size="sm"
      >
        <Stack gap="md">
          <Text size="sm">
            Are you sure you want to delete "{enrichedVideo.title}"? This action cannot be undone.
          </Text>
          <Group justify="flex-end" gap="sm">
            <Button variant="subtle" color="gray" onClick={() => setDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button color="red" onClick={confirmDelete}>
              Delete
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
};

export default VideoCard;