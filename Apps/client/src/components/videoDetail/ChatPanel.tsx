import React from 'react';
import { Box, ScrollArea, Stack, Group, Loader, TextInput, ActionIcon, Text, rem } from '@mantine/core';
import { Controller } from 'react-hook-form';
import ChatBubble from '../common/ChatBubble';
import ErrorDisplay from '../common/ErrorDisplay';

interface ChatPanelProps {
    scrollRef: React.RefObject<HTMLDivElement | null>;
    messages: any[];
    isLoading: boolean;
    error: string | null;
    onSendMessage: (data: { message: string }) => void;
    onRetry: () => void;
    control: any;
    errors: any;
    handleSubmit: any;
}

const ChatPanel: React.FC<ChatPanelProps> = ({
    scrollRef,
    messages,
    isLoading,
    error,
    onSendMessage,
    onRetry,
    control,
    errors,
    handleSubmit
}) => (
    <Box style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <ScrollArea viewportRef={scrollRef} style={{ flex: 1 }} p="md">
            {messages.length === 0 ? (
                <Stack align="center" py={50} ta="center">
                    <Text fw={700}>Ask anything about the video.</Text>
                    <Text size="xs" c="dimmed">The AI will use the video transcript as ground truth.</Text>
                </Stack>
            ) : messages.map((msg) => (
                <Box key={msg.id} mb="md">
                    <ChatBubble message={msg} />
                </Box>
            ))}

            {error && (
                <Box mb="md">
                    <ErrorDisplay
                        message={error}
                        onRetry={onRetry}
                        variant="light"
                    />
                </Box>
            )}

            {isLoading && (
                <Group gap="xs" mt="md" ml="md">
                    <Loader size="sm" variant="dots" color="indigo" />
                    <Text size="xs" c="dimmed" fs="italic">VidSage is thinking...</Text>
                </Group>
            )}
        </ScrollArea>

        <Box p="md" style={{ borderTop: '1px solid var(--mantine-color-gray-2)' }}>
            <form onSubmit={handleSubmit(onSendMessage)}>
                <Controller
                    name="message"
                    control={control}
                    rules={{
                        required: 'Please enter a message',
                        minLength: {
                            value: 2,
                            message: 'Message must be at least 2 characters'
                        }
                    }}
                    render={({ field }) => (
                        <TextInput
                            {...field}
                            placeholder="Ask a question about this video..."
                            radius="xl"
                            size="md"
                            error={errors.message?.message}
                            rightSection={
                                <ActionIcon
                                    type="submit"
                                    radius="xl"
                                    color="indigo"
                                    variant="filled"
                                    size="lg"
                                    disabled={isLoading}
                                >
                                    <i className="fas fa-paper-plane text-xs"></i>
                                </ActionIcon>
                            }
                            styles={{
                                input: {
                                    paddingRight: rem(50)
                                }
                            }}
                        />
                    )}
                />
            </form>
        </Box>
    </Box>
);

export default ChatPanel;