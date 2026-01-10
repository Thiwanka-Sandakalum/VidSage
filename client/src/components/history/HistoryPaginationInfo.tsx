import React from 'react';
import { Paper, Group, Text } from '@mantine/core';

interface HistoryPaginationInfoProps {
    startIndex: number;
    endIndex: number;
    total: number;
    currentPage: number;
    totalPages: number;
}

const HistoryPaginationInfo: React.FC<HistoryPaginationInfoProps> = ({ startIndex, endIndex, total, currentPage, totalPages }) => (
    <Paper
        p="md"
        radius="lg"
        withBorder
        bg={document.body.classList.contains('mantine-dark') ? 'dark.7' : 'gray.0'}
    >
        <Group justify="space-between">
            <Text size="sm" c="dimmed">
                Showing {startIndex + 1}-{Math.min(endIndex, total)} of {total} videos
            </Text>
            <Text size="sm" c="dimmed">
                Page {currentPage} of {totalPages}
            </Text>
        </Group>
    </Paper>
);

export default HistoryPaginationInfo;