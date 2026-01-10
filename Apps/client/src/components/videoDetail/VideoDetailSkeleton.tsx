import React from 'react';
import { Box, Grid, Stack, Paper, AspectRatio, Skeleton, Group, SimpleGrid } from '@mantine/core';

const VideoDetailSkeleton: React.FC = () => (
    <Box pb={80}>
        <Grid gutter="xl">
            <Grid.Col span={{ base: 12, lg: 8 }}>
                <Stack gap="xl">
                    {/* Video Player Skeleton */}
                    <Paper radius="xl" style={{ overflow: 'hidden' }} shadow="xl">
                        <AspectRatio ratio={16 / 9}>
                            <Skeleton height="100%" />
                        </AspectRatio>
                    </Paper>

                    {/* Title and Actions Skeleton */}
                    <Group justify="space-between" align="flex-start">
                        <Stack gap={5} style={{ flex: 1 }}>
                            <Skeleton height={32} width="70%" />
                            <Skeleton height={20} width="40%" />
                        </Stack>
                        <Group gap="sm">
                            <Skeleton height={36} width={36} circle />
                            <Skeleton height={36} width={36} circle />
                            <Skeleton height={36} width={36} circle />
                        </Group>
                    </Group>

                    {/* AI Insights Skeleton */}
                    <Paper p={30} radius="xl" withBorder shadow="sm">
                        <Group justify="space-between" mb="lg">
                            <Skeleton height={24} width={150} />
                            <Skeleton height={36} width={180} />
                        </Group>
                        <Stack gap="xs">
                            <Skeleton height={16} width="100%" />
                            <Skeleton height={16} width="95%" />
                            <Skeleton height={16} width="98%" />
                            <Skeleton height={16} width="92%" />
                        </Stack>
                    </Paper>

                    {/* Quick Queries Skeleton */}
                    <Paper p={30} radius="xl" withBorder shadow="sm" bg="gray.0">
                        <Skeleton height={20} width={120} mb="md" />
                        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="xs">
                            <Skeleton height={32} />
                            <Skeleton height={32} />
                            <Skeleton height={32} />
                            <Skeleton height={32} />
                        </SimpleGrid>
                    </Paper>
                </Stack>
            </Grid.Col>

            <Grid.Col span={{ base: 12, lg: 4 }}>
                {/* Chat Panel Skeleton */}
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
                    }}
                >
                    <Box p="md" bg="gray.0" style={{ borderBottom: '1px solid var(--mantine-color-gray-2)' }}>
                        <Group justify="space-between">
                            <Group gap="xs">
                                <Skeleton height={28} width={28} />
                                <Skeleton height={16} width={100} />
                            </Group>
                            <Group gap={4}>
                                <Skeleton height={28} width={28} circle />
                                <Skeleton height={28} width={28} circle />
                            </Group>
                        </Group>
                    </Box>
                    <Box style={{ flex: 1 }} p="md">
                        <Stack gap="md" align="center" justify="center" h="100%">
                            <Skeleton height={40} width={40} circle />
                            <Skeleton height={20} width={200} />
                            <Skeleton height={14} width={250} />
                        </Stack>
                    </Box>
                    <Box p="md" style={{ borderTop: '1px solid var(--mantine-color-gray-2)' }}>
                        <Skeleton height={44} radius="xl" />
                    </Box>
                </Paper>
            </Grid.Col>
        </Grid>
    </Box>
);

export default VideoDetailSkeleton;