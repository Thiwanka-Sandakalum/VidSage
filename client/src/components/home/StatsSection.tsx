import React from 'react';
import { Group, Stack, Text, Divider, rem, Skeleton } from '@mantine/core';

interface Stats {
    total_videos: number;
    total_chunks: number;
    total_users: number;
}

interface StatsSectionProps {
    stats: Stats | null;
    loading?: boolean;
}

const StatsSection: React.FC<StatsSectionProps> = ({ stats, loading = false }) => {
    if (loading) {
        return (
            <Group gap={50} mt="lg" wrap="nowrap" justify="center">
                <Stack gap={0} align="center">
                    <Skeleton height={28} width={60} radius="md" mb={4} />
                    <Skeleton height={12} width={80} radius="sm" />
                </Stack>
                <Divider orientation="vertical" />
                <Stack gap={0} align="center">
                    <Skeleton height={28} width={60} radius="md" mb={4} />
                    <Skeleton height={12} width={80} radius="sm" />
                </Stack>
            </Group>
        );
    }

    if (!stats) return null;

    return (
        <Group gap={50} mt="lg" wrap="nowrap" justify="center">
            <Stack gap={0} align="center">
                <Text fw={900} size={rem(28)} variant="gradient" gradient={{ from: 'dark', to: 'gray.6' }}>
                    {stats.total_videos}
                </Text>
                <Text size="xs" c="dimmed" tt="uppercase" fw={800} style={{ letterSpacing: '1px' }}>
                    Processed
                </Text>
            </Stack>
            <Divider orientation="vertical" />
            <Stack gap={0} align="center">
                <Text fw={900} size={rem(28)} variant="gradient" gradient={{ from: 'dark', to: 'gray.6' }}>
                    {stats.total_chunks}
                </Text>
                <Text size="xs" c="dimmed" tt="uppercase" fw={800} style={{ letterSpacing: '1px' }}>
                    Chunks
                </Text>
            </Stack>
        </Group>
    );
};

export default StatsSection;
