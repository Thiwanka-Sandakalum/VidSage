import React from 'react';
import { Card, Stack, Skeleton } from '@mantine/core';
import VideoThumbnail from './VideoThumbnail';
import VideoInfo from './VideoInfo';
import DeleteButton from './DeleteButton';
import { VideoMetadata } from '../../../types/types';

interface GridViewProps {
    video: VideoMetadata;
    onNavigate: () => void;
    onDelete?: (e: React.MouseEvent) => void;
    loading?: boolean;
}

const GridView: React.FC<GridViewProps> = ({ video, onNavigate, onDelete, loading = false }) => {
    return (
        <Card
            shadow="sm"
            padding="lg"
            radius="md"
            withBorder
            onClick={onNavigate}
            style={{ position: 'relative', overflow: 'hidden', transition: 'box-shadow 0.2s, transform 0.2s' }}
            onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = 'var(--mantine-shadow-md)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--mantine-shadow-sm)';
            }}
        >
            <Card.Section style={{ position: 'relative' }}>
                <VideoThumbnail
                    thumbnail={video.thumbnail}
                    title={video.title}
                    duration={video.duration}
                    showPlayOverlay
                    videoId={video.id}
                />
                {onDelete && <DeleteButton onDelete={onDelete} position="absolute" />}
            </Card.Section>

            <Stack gap="xs" mt="md">
                {loading ? (
                    <>
                        <Skeleton height={20} width="80%" radius="sm" />
                        <Skeleton height={14} width="60%" radius="sm" />
                    </>
                ) : (
                    <VideoInfo
                        title={video.title}
                        author={video.author}
                        publishedAt={video.publishedAt}
                    />
                )}
            </Stack>
        </Card>
    );
};

export default GridView;
