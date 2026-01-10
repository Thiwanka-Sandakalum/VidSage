
import React from 'react';
import { Alert, Button, Group, Text, Stack, Box, rem } from '@mantine/core';

interface ErrorDisplayProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  variant?: 'light' | 'filled' | 'outline';
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ 
  title = "Connection Error", 
  message, 
  onRetry,
  variant = "light"
}) => {
  return (
    <Alert 
      variant={variant} 
      color="red" 
      title={title} 
      icon={<i className="fas fa-exclamation-circle"></i>}
      radius="md"
    >
      <Stack gap="sm">
        <Text size="sm">{message}</Text>
        {onRetry && (
          <Group justify="flex-end">
            <Button 
              size="xs" 
              variant="white" 
              color="red" 
              onClick={onRetry}
              leftSection={<i className="fas fa-redo text-[10px]"></i>}
            >
              Try Again
            </Button>
          </Group>
        )}
      </Stack>
    </Alert>
  );
};

export default ErrorDisplay;
