import React from 'react';
import { Stack } from '@mantine/core';
import VideoCard from '../common/VideoCard';

const VideoList: React.FC<{ videos: any[]; onDelete: (id: string) => void }> = ({ videos, onDelete }) => (
    <Stack gap="md">
        {videos.map((video) => (
            <VideoCard key={video.id} video={video} onDelete={onDelete} viewMode="list" />
        ))}
    </Stack>
);

export default VideoList;