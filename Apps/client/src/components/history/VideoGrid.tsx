import React from 'react';
import { SimpleGrid } from '@mantine/core';
import VideoCard from '../common/VideoCard';

const VideoGrid: React.FC<{ videos: any[]; onDelete: (id: string) => void }> = ({ videos, onDelete }) => (
    <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="xl">
        {videos.map((video) => (
            <VideoCard key={video.id} video={video} onDelete={onDelete} viewMode="grid" />
        ))}
    </SimpleGrid>
);

export default VideoGrid;