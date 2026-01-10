import React from 'react';
import { Controller, UseFormHandleSubmit, Control, FieldErrors } from 'react-hook-form';
import { Box, Stack, Badge, Title, rem, Paper, Group, TextInput, Button, Text } from '@mantine/core';

interface VideoFormData {
    url: string;
}

interface HeroSectionProps {
    control: Control<VideoFormData>;
    errors: FieldErrors<VideoFormData>;
    handleSubmit: UseFormHandleSubmit<VideoFormData>;
    onSubmit: (data: VideoFormData) => void;
    isProcessing: boolean;
}

const HeroSection: React.FC<HeroSectionProps> = ({
    control,
    errors,
    handleSubmit,
    onSubmit,
    isProcessing
}) => {
    return (
        <Stack align="center" gap="xl" ta="center">
            {/* Decorative background element */}
            <Box
                style={{
                    position: 'fixed',
                    top: '-10%',
                    right: '-5%',
                    width: '500px',
                    height: '500px',
                    background: 'radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, rgba(255,255,255,0) 70%)',
                    zIndex: -1,
                    pointerEvents: 'none'
                }}
            />

            <Badge
                size="lg"
                variant="gradient"
                gradient={{ from: 'indigo', to: 'cyan' }}
                radius="xl"
                py={15}
                px={20}
                style={{ border: 'none' }}
            >
                AI-POWERED VIDEO INTELLIGENCE
            </Badge>

            <Box maw={900}>
                <Title order={1} size={rem(72)} fw={900} lh={1.05} style={{ letterSpacing: '-3px' }}>
                    Understand Videos in <Text component="span" variant="gradient" gradient={{ from: 'indigo.6', to: 'violet.5' }} inherit>Seconds</Text>
                </Title>
                <Text size="xl" c="dimmed" mt="xl" fw={500} maw={600} mx="auto">
                    Analyze transcripts, generate RAG-powered summaries, and chat with content using advanced Gemini AI.
                </Text>
            </Box>

            <Paper
                shadow="0 25px 50px -12px rgba(0, 0, 0, 0.08)"
                p={6}
                radius="100px"
                withBorder
                w="100%"
                maw={720}
                style={{
                    overflow: 'hidden',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(8px)',
                    borderColor: 'var(--mantine-color-gray-2)'
                }}
            >
                <form onSubmit={handleSubmit(onSubmit)}>
                    <Group gap={0} wrap="nowrap">
                        <Controller
                            name="url"
                            control={control}
                            rules={{
                                required: 'Please enter a YouTube URL',
                                pattern: {
                                    value: /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})/,
                                    message: 'Please enter a valid YouTube URL'
                                }
                            }}
                            render={({ field }) => (
                                <TextInput
                                    {...field}
                                    placeholder="Paste YouTube Video URL here..."
                                    variant="unstyled"
                                    size="lg"
                                    style={{ flex: 1 }}
                                    px={30}
                                    error={errors.url?.message}
                                    styles={{
                                        input: {
                                            fontSize: rem(18),
                                            fontWeight: 500,
                                            height: rem(58)
                                        }
                                    }}
                                    leftSection={<i className="fab fa-youtube text-red-600 ml-4 text-xl"></i>}
                                    leftSectionPointerEvents="none"
                                />
                            )}
                        />
                        <Button
                            type="submit"
                            size="lg"
                            radius="100px"
                            color="indigo"
                            px={40}
                            h={58}
                            loading={isProcessing}
                            style={{ boxShadow: 'var(--mantine-shadow-md)' }}
                            leftSection={<i className="fas fa-wand-magic-sparkles"></i>}
                        >
                            Analyze
                        </Button>
                    </Group>
                </form>
            </Paper>
        </Stack>
    );
};

export default HeroSection;
