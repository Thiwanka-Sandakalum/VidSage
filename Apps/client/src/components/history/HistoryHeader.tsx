import React from 'react';
import { Title, Text, Stack, Group, SegmentedControl, Select } from '@mantine/core';

interface HistoryHeaderProps {
    historyLength: number;
    viewMode: 'grid' | 'list';
    setViewMode: (v: 'grid' | 'list') => void;
    itemsPerPage: number;
    setItemsPerPage: (n: number) => void;
    setCurrentPage: (n: number) => void;
}

const HistoryHeader: React.FC<HistoryHeaderProps> = ({ historyLength, viewMode, setViewMode, itemsPerPage, setItemsPerPage, setCurrentPage }) => (
    <Group justify="space-between" align="flex-start" wrap="wrap">
        <Stack gap={5}>
            <Title order={1} fw={800}>Your Research Library</Title>
            <Text c="dimmed" size="lg">
                Access all your previously analyzed video insights and transcripts.
            </Text>
        </Stack>
        {historyLength > 0 && (
            <Group gap="md">
                <SegmentedControl
                    value={viewMode}
                    onChange={(value) => setViewMode(value as 'grid' | 'list')}
                    data={[
                        { label: <i className="fas fa-th"></i>, value: 'grid' },
                        { label: <i className="fas fa-list"></i>, value: 'list' }
                    ]}
                />
                <Select
                    value={itemsPerPage.toString()}
                    onChange={(value) => {
                        setItemsPerPage(Number(value));
                        setCurrentPage(1);
                    }}
                    data={[
                        { value: '6', label: '6 per page' },
                        { value: '9', label: '9 per page' },
                        { value: '12', label: '12 per page' },
                        { value: '24', label: '24 per page' }
                    ]}
                    w={140}
                />
            </Group>
        )}
    </Group>
);

export default HistoryHeader;