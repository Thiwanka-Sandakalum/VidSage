import React from 'react';
import { SimpleGrid, Box, Skeleton } from '@mantine/core';

const HistorySkeleton: React.FC = () => (
    <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="xl">
        {[...Array(6)].map((_, i) => (
            <Box key={i}>
                <Skeleton height={200} radius="lg" mb="md" />
                <Skeleton height={20} width="80%" radius="sm" mb={8} />
                <Skeleton height={14} width="60%" radius="sm" />
            </Box>
        ))}
    </SimpleGrid>
);

export default HistorySkeleton;