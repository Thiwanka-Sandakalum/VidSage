import React from 'react';
import { Paper, Title, SimpleGrid, Button, Stack, Loader, Text } from '@mantine/core';

interface QuickQueriesProps {
  suggestedQuestions: string[];
  isDark: boolean;
  handleSuggestedQuestion: (q: string) => void;
}

const QuickQueries: React.FC<QuickQueriesProps> = ({ suggestedQuestions, isDark, handleSuggestedQuestion }) => (
  <Paper
    p={30}
    radius="xl"
    withBorder
    shadow="sm"
    style={{
      background: isDark ? 'rgba(36, 37, 46, 0.98)' : 'rgba(245, 247, 250, 0.98)',
      border: `1px solid ${isDark ? 'var(--mantine-color-dark-5)' : 'var(--mantine-color-gray-2)'}`,
      boxShadow: isDark
        ? '0 2px 8px rgba(0,0,0,0.10)'
        : '0 2px 8px rgba(99,102,241,0.04)'
    }}
  >
    <Title order={4} mb="md" style={{ color: isDark ? 'var(--mantine-color-indigo-2)' : 'var(--mantine-color-indigo-7)' }}>
      <i className="fas fa-question-circle" style={{ marginRight: 8, color: isDark ? '#a5b4fc' : '#6366f1' }}></i>
      Quick Queries
    </Title>
    {suggestedQuestions.length > 0 ? (
      <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="xs">
        {suggestedQuestions.map((q, i) => (
          <Button
            key={i}
            variant={isDark ? 'light' : 'white'}
            color={isDark ? 'indigo' : 'gray'}
            size="sm"
            justify="flex-start"
            fw={500}
            radius="md"
            onClick={() => handleSuggestedQuestion(q)}
            style={{
              border: `1px solid ${isDark ? 'var(--mantine-color-dark-4)' : 'var(--mantine-color-gray-2)'}`,
              marginBottom: 6,
              textAlign: 'left',
              color: isDark ? 'var(--mantine-color-indigo-2)' : 'var(--mantine-color-dark-7)',
              background: isDark ? 'rgba(40, 41, 54, 0.95)' : 'rgba(255,255,255,0.95)',
              transition: 'background 0.2s, color 0.2s',
              boxShadow: isDark ? '0 1px 4px rgba(0,0,0,0.08)' : '0 1px 4px rgba(99,102,241,0.03)'
            }}
            onMouseOver={e => {
              (e.currentTarget as HTMLButtonElement).style.background = isDark ? 'var(--mantine-color-dark-6)' : 'var(--mantine-color-gray-0)';
              (e.currentTarget as HTMLButtonElement).style.color = isDark ? 'var(--mantine-color-indigo-1)' : 'var(--mantine-color-indigo-7)';
            }}
            onMouseOut={e => {
              (e.currentTarget as HTMLButtonElement).style.background = isDark ? 'rgba(40, 41, 54, 0.95)' : 'rgba(255,255,255,0.95)';
              (e.currentTarget as HTMLButtonElement).style.color = isDark ? 'var(--mantine-color-indigo-2)' : 'var(--mantine-color-dark-7)';
            }}
          >
            {q}
          </Button>
        ))}
      </SimpleGrid>
    ) : (
      <Stack align="center" py="md">
        <Loader size="sm" color={isDark ? 'indigo' : 'gray'} />
        <Text size="sm" c="dimmed">Generating suggested questions...</Text>
      </Stack>
    )}
  </Paper>
);

export default QuickQueries;