import React from 'react';
import { Card, Group, Skeleton, Stack } from '@mantine/core';
import VideoThumbnail from './VideoThumbnail';
import VideoInfo from './VideoInfo';
import DeleteButton from './DeleteButton';
import { VideoMetadata } from '../../../types/types';

interface ListViewProps {
    video: VideoMetadata;
    onNavigate: () => void;
    onDelete?: (e: React.MouseEvent) => void;
    loading?: boolean;
}

const ListView: React.FC<ListViewProps> = ({ video, onNavigate, onDelete, loading = false }) => {
    return (
        <Card
            shadow="sm"
            padding="md"
            radius="lg"
            withBorder
            onClick={onNavigate}
            style={{ position: 'relative', overflow: 'hidden', transition: 'box-shadow 0.2s, transform 0.2s' }}
        >
            <Group wrap="nowrap" gap="md">
                <VideoThumbnail
                    thumbnail={video.thumbnail}
                    title={video.title}
                    duration={video.duration}
                    width={200}
                    showPlayOverlay={false}
                    videoId={video.id}
                />

                {loading ? (
                    <Stack gap="xs" style={{ flex: 1, minWidth: 0 }}>
                        <Skeleton height={20} width="60%" radius="sm" />
                        <Skeleton height={14} width="40%" radius="sm" />
                    </Stack>
                ) : (
                    <VideoInfo
                        title={video.title}
                        author={video.author}
                        publishedAt={video.publishedAt}
                    />
                )}

                {onDelete && <DeleteButton onDelete={onDelete} position="relative" />}
            </Group>
        </Card>
    );
};

export default ListView;
