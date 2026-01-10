import React from 'react';
import { Stack, Text, Group } from '@mantine/core';

interface VideoInfoProps {
    title: string;
    author?: string;
    publishedAt: string;
    titleSize?: string;
    layout?: 'vertical' | 'compact';
}

const VideoInfo: React.FC<VideoInfoProps> = ({
    title,
    author,
    publishedAt,
    titleSize = 'lg',
    layout = 'vertical'
}) => {
    return (
        <Stack gap="xs" style={{ flex: 1, minWidth: 0 }}>
            <Text fw={700} lineClamp={2} size={titleSize} lh={1.2}>
                {title}
            </Text>
            <Group gap="xs">
                <Text size="sm" c="dimmed" fw={500}>
                    {author || 'Unknown'}
                </Text>
                <Text size="sm" c="dimmed">•</Text>
                <Text size="sm" c="dimmed">
                    {publishedAt}
                </Text>
            </Group>
        </Stack>
    );
};

export default VideoInfo;
