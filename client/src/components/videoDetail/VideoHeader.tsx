import React from 'react';
import { Stack, Title, Text } from '@mantine/core';

interface VideoHeaderProps {
  title?: string;
  author?: string;
  publishedAt?: string;
  fallbackTitle?: string;
  fallbackAuthor?: string;
  fallbackPublishedAt?: string;
  formatDate: (dateStr?: string) => string;
}

const VideoHeader: React.FC<VideoHeaderProps> = ({ title, author, publishedAt, fallbackTitle, fallbackAuthor, fallbackPublishedAt, formatDate }) => (
  <Stack gap={5}>
    <Title order={1} size="h2" fw={800}>{title || fallbackTitle}</Title>
    <Text size="sm" c="dimmed">
      by {author || fallbackAuthor}
      {((publishedAt || fallbackPublishedAt) && (author || fallbackAuthor)) && ' • '}
      {formatDate(publishedAt || fallbackPublishedAt)}
    </Text>
  </Stack>
);

export default VideoHeader;