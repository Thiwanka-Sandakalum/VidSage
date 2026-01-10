
import React from 'react';

import { Card, Text, Stack, Center, Box, Title, useMantineColorScheme, useMantineTheme } from '@mantine/core';
import { ProcessStatus } from '../../types/types';
import ProcessingStep from './ProcessingStep';

interface ProcessingStateProps {
  status: ProcessStatus;
  progress: number;
}

const ProcessingState: React.FC<ProcessingStateProps> = ({ status }) => {
  const steps = [
    {
      label: 'Fetching video metadata & transcript',
      activeOn: [ProcessStatus.EXTRACTING],
      completedOn: [ProcessStatus.TRANSCRIBING, ProcessStatus.ANALYZING, ProcessStatus.COMPLETED]
    },
    {
      label: 'Chunking text for analysis',
      activeOn: [ProcessStatus.TRANSCRIBING],
      completedOn: [ProcessStatus.ANALYZING, ProcessStatus.COMPLETED]
    },
    {
      label: 'Generating vector embeddings',
      activeOn: [ProcessStatus.ANALYZING],
      completedOn: [ProcessStatus.COMPLETED]
    },
    {
      label: 'Finalizing knowledge base',
      activeOn: [ProcessStatus.COMPLETED],
      completedOn: []
    },
  ];

  const getStepState = (step: typeof steps[0]) => {
    if (step.completedOn.includes(status)) return 'completed' as const;
    if (step.activeOn.includes(status)) return 'active' as const;
    return 'pending' as const;
  };

  const theme = useMantineTheme();
  const { colorScheme } = useMantineColorScheme();
  const isDark = colorScheme === 'dark';

  return (
    <Center h="80vh">
      <Card
        shadow={isDark ? '0 20px 40px rgba(0,0,0,0.32)' : '0 20px 40px rgba(0,0,0,0.08)'}
        p={45}
        radius="lg"
        withBorder
        w={500}
        bg={isDark ? theme.colors.dark[7] : 'white'}
        style={{
          borderColor: isDark ? theme.colors.dark[4] : theme.colors.gray[2],
          color: isDark ? theme.white : theme.black
        }}
      >
        <Stack align="center" gap="xs" mb={40}>
          <Title order={2} fw={800} style={{ letterSpacing: '-0.5px', color: isDark ? theme.white : theme.black }}>Processing Video...</Title>
          <Text size="sm" c={isDark ? 'gray.4' : 'dimmed'} fw={500}>Please wait while we analyze the content.</Text>
        </Stack>

        <Box px={10}>
          {steps.map((step, index) => (
            <ProcessingStep
              key={index}
              label={step.label}
              state={getStepState(step)}
            />
          ))}
        </Box>
      </Card>
    </Center>
  );
};

export default ProcessingState;
