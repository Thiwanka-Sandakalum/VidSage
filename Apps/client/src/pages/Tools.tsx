
import { Stack, Box, Title, Divider, SimpleGrid, Card, Group, Badge, Switch, Button, Paper, Text, Container } from '@mantine/core';
import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks';
import { checkGoogleStatus, connectGoogle, disconnectGoogle } from '../store/toolsSlice';
import { notifications } from '@mantine/notifications';

const Tools: React.FC = () => {
  const dispatch = useAppDispatch();
  const { integrations, loading } = useAppSelector((state) => state.tools);

  useEffect(() => {
    dispatch(checkGoogleStatus());
  }, [dispatch]);

  const handleToggleConnection = async (toolId: string) => {
    const tool = integrations.find(t => t.id === toolId);

    if (toolId === 'google-docs') {
      if (!tool?.isConnected) {
        try {
          await dispatch(connectGoogle()).unwrap();
          notifications.show({
            title: 'Connecting',
            message: 'Redirecting to Google OAuth...',
            color: 'blue',
          });
        } catch (error) {
          notifications.show({
            title: 'Error',
            message: 'Failed to connect Google account',
            color: 'red',
          });
        }
      } else {
        try {
          await dispatch(disconnectGoogle()).unwrap();
          notifications.show({
            title: 'Disconnected',
            message: 'Google Docs has been disconnected',
            color: 'green',
          });
          dispatch(checkGoogleStatus());
        } catch (error) {
          notifications.show({
            title: 'Error',
            message: 'Failed to disconnect Google account',
            color: 'red',
          });
        }
      }
    } else {
      notifications.show({
        title: 'Coming Soon',
        message: `${tool?.name} integration is not yet available`,
        color: 'blue',
      });
    }
  };

  return (
    <Container size="lg" py={40}>
      <Stack gap="xl">
        <Box>
          <Title order={1} mb={5}>AI Integrations & Tools</Title>
          <Text c="dimmed" size="lg">Connect external productivity tools to enhance your VidSage workflow.</Text>
        </Box>

        <Divider variant="dashed" />

        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="xl">
          {integrations.map((tool) => (
            <Card key={tool.id} withBorder padding="lg" radius="md" shadow="sm">
              <Group justify="space-between" mb="xs">
                <Group>
                  <Box
                    p={10}
                    bg={`${tool.color}.1`}
                    style={{ borderRadius: '12px', display: 'flex', color: `var(--mantine-color-${tool.color}-6)` }}
                  >
                    <i className={tool.icon}></i>
                  </Box>
                  <Title order={3} size="h4">{tool.name}</Title>
                </Group>
                <Badge color={tool.isConnected ? 'green' : 'gray'} variant="light">
                  {tool.isConnected ? 'Connected' : 'Offline'}
                </Badge>
              </Group>

              <Text size="sm" c="dimmed" mb="xl" style={{ minHeight: '3em' }}>
                {tool.description}
              </Text>

              <Group justify="space-between" mt="md" p="xs" bg="gray.0" style={{ borderRadius: '8px' }}>
                <Text size="sm" fw={600}>{tool.isConnected ? 'Active' : 'Enable Integration'}</Text>
                <Switch
                  checked={tool.isConnected}
                  onChange={() => handleToggleConnection(tool.id)}
                  color="green"
                  disabled={loading}
                />
              </Group>
            </Card>
          ))}
        </SimpleGrid>

        <Paper p="xl" radius="md" withBorder bg="indigo.0" mt={40}>
          <Group align="flex-start" gap="xl">
            <Box hiddenFrom="xs">
              <i className="fas fa-plug-circle-bolt text-4xl text-indigo-600"></i>
            </Box>
            <Stack gap="xs" style={{ flex: 1 }}>
              <Title order={3} size="h4" c="indigo.9">Request a Custom Integration</Title>
              <Text size="sm" c="indigo.7">
                Want to connect VidSage to your CRM, LMS, or proprietary software?
                Our API allows for custom webhook-based registrations.
              </Text>
              <Group mt="xs">
                <Button variant="filled" color="indigo" size="sm">Developer Docs</Button>
                <Button variant="subtle" color="indigo" size="sm">Contact Enterprise</Button>
              </Group>
            </Stack>
            <Box visibleFrom="xs">
              <i className="fas fa-plug-circle-bolt text-5xl text-indigo-200"></i>
            </Box>
          </Group>
        </Paper>
      </Stack>
    </Container>
  );
};

export default Tools;
