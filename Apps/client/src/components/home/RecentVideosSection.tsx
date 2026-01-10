import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '../../hooks';
import { processVideo, resetVideoState } from '../../store/videoSlice';
import { Link } from 'react-router-dom';
import { Stack, Group, Title, Button, SimpleGrid, Paper, Box, Text, ThemeIcon, Skeleton, Card, Modal, Tooltip, Badge, ActionIcon } from '@mantine/core';
// Example podcast videos for first-time users
const EXAMPLE_VIDEOS = [
    {
        id: 'yt1',
        title: 'Lex Fridman Podcast #400 – Sam Altman',
        author: 'Lex Fridman',
        publishedAt: '2023-11-01',
        thumbnailUrl: 'https://i.ytimg.com/vi/L_Guz73e6fw/hqdefault.jpg',
        youtubeUrl: 'https://www.youtube.com/watch?v=L_Guz73e6fw',
    },
    {
        id: 'yt2',
        title: 'The Diary Of A CEO – Dr. Andrew Huberman',
        author: 'Steven Bartlett',
        publishedAt: '2024-01-15',
        thumbnailUrl: 'https://i.ytimg.com/vi/SwQhKFMxmDY/hqdefault.jpg',
        youtubeUrl: 'https://www.youtube.com/watch?v=SwQhKFMxmDY',
    },
    {
        id: 'yt3',
        title: 'The Knowledge Project – Naval Ravikant',
        author: 'Shane Parrish',
        publishedAt: '2023-09-10',
        thumbnailUrl: 'https://i.ytimg.com/vi/3qHkcs3kG44/hqdefault.jpg',
        youtubeUrl: 'https://www.youtube.com/watch?v=3qHkcs3kG44',
    },
];
import VideoCard from '../common/VideoCard';

interface Video {
    id: string;
    title: string;
    author: string;
    publishedAt: string;
    thumbnailUrl?: string;
}

interface RecentVideosSectionProps {
    videos: Video[];
    loading?: boolean;
}

const VideoCardSkeleton: React.FC = () => (
    <Card padding="lg" radius="xl" withBorder>
        <Card.Section>
            <Skeleton height={180} />
        </Card.Section>
        <Stack gap="sm" mt="md">
            <Skeleton height={20} width="80%" radius="sm" />
            <Skeleton height={14} width="60%" radius="sm" />
            <Skeleton height={14} width="40%" radius="sm" />
        </Stack>
    </Card>
);

const RecentVideosSection: React.FC<RecentVideosSectionProps> = ({ videos, loading = false }) => {
    const dispatch = useAppDispatch();
    const navigate = useNavigate();
    const [processingId, setProcessingId] = useState<string | null>(null);
    // Local state for videos to allow immediate removal on delete
    const [localVideos, setLocalVideos] = useState(videos);

    React.useEffect(() => {
        setLocalVideos(videos);
    }, [videos]);

    const handleChatClick = async (video: typeof EXAMPLE_VIDEOS[0]) => {
        setProcessingId(video.id);
        dispatch(resetVideoState());
        const result = await dispatch(processVideo(video.youtubeUrl));
        setProcessingId(null);
        // If successful, navigate to video detail
        if (processVideo.fulfilled.match(result)) {
            navigate(`/video/${result.payload.video.id}`);
        }
    };

    const handleDelete = (videoId: string) => {
        setLocalVideos((prev) => prev.filter((v) => v.id !== videoId));
    };

    return (
        <Stack gap="xl">
            <Group justify="space-between" align="center">
                <Group gap="xs">
                    <ThemeIcon variant="light" color="indigo" radius="md">
                        <i className="fas fa-bolt text-xs"></i>
                    </ThemeIcon>
                    <Title order={2} fw={800}>Recent Discoveries</Title>
                </Group>
                <Button component={Link} to="/history" variant="subtle" color="indigo" size="sm" radius="md">
                    View Library
                </Button>
            </Group>

            {loading ? (
                <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="xl">
                    <VideoCardSkeleton />
                    <VideoCardSkeleton />
                    <VideoCardSkeleton />
                </SimpleGrid>
            ) : localVideos.length > 0 ? (
                <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="xl">
                    {localVideos.slice(0, 3).map((video) => (
                        <VideoCard key={video.id} video={video} onDelete={handleDelete} />
                    ))}
                </SimpleGrid>
            ) : (
                <>
                    <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="xl">
                        {EXAMPLE_VIDEOS.map((video) => (
                            <Card
                                key={video.id}
                                padding="lg"
                                radius="xl"
                                withBorder
                                style={{ position: 'relative', overflow: 'hidden', transition: 'box-shadow 0.2s, transform 0.2s' }}
                                className="video-card-hover"
                            >
                                <Card.Section>
                                    <img src={video.thumbnailUrl} alt={video.title} style={{ width: '100%', height: 180, objectFit: 'cover', borderRadius: '16px' }} />
                                    <Badge color="violet" variant="filled" style={{ position: 'absolute', top: 12, left: 12 }}>Try</Badge>
                                    <Tooltip label="Analyze and chat with this video" withArrow>
                                        <ActionIcon
                                            color="violet"
                                            size="lg"
                                            radius="xl"
                                            variant="filled"
                                            style={{ position: 'absolute', top: 12, right: 12, zIndex: 2 }}
                                            onClick={() => handleChatClick(video)}
                                            loading={processingId === video.id}
                                            disabled={!!processingId}
                                        >
                                            <i className="fas fa-comments"></i>
                                        </ActionIcon>
                                    </Tooltip>
                                </Card.Section>
                                <Stack gap="xs" mt="md">
                                    <Text fw={700} size="lg">{video.title}</Text>
                                    <Text c="dimmed" size="sm">{video.author}</Text>
                                    <Text c="dimmed" size="xs">{video.publishedAt}</Text>
                                </Stack>
                            </Card>
                        ))}
                    </SimpleGrid>
                </>
            )}
        </Stack>
    );
};

export default RecentVideosSection;
