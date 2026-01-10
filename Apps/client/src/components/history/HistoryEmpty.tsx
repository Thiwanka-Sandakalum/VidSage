import React from 'react';
import { Paper, Stack, Box, Title, Text, Button } from '@mantine/core';
import { Link } from 'react-router-dom';

const HistoryEmpty: React.FC = () => (
    <Paper p={100} radius="xl" withBorder style={{ borderStyle: 'dashed', backgroundColor: 'transparent' }}>
        <Stack align="center" gap="md">
            <Box p={20} bg="gray.0" style={{ borderRadius: '50%' }}>
                <i className="fas fa-video-slash text-4xl text-gray-400"></i>
            </Box>
            <Title order={3} fw={600} c="dimmed">Your library is empty</Title>
            <Text c="dimmed" ta="center" maw={400}>
                Start analyzing videos to build your research library
            </Text>
            <Button component={Link} to="/" variant="gradient" gradient={{ from: 'indigo', to: 'cyan' }} mt="md" size="md">
                <i className="fas fa-plus mr-2"></i> Analyze Your First Video
            </Button>
        </Stack>
    </Paper>
);

export default HistoryEmpty;