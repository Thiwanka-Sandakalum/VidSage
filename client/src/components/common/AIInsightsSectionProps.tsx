import React, { useState } from 'react';
import { Paper, Group, Title, Button, Stack, Loader, Text, Box, Modal } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './AIInsights.css';
import { useAppSelector } from '../../hooks/useAppSelector';
import { useNavigate } from 'react-router-dom';

interface AIInsightsSectionProps {
    summaryState: {
        loading: boolean;
        summary: string | null;
        sources?: Array<{ text_preview: string; chunk_id: string; relevance_score: number }>;
        error?: string | null;
    };
    isSpeaking: boolean;
    saving: boolean;
    saveError: string | null;
    docLink?: string;
    handleTTS: () => void;
    handleSaveSummaryToDoc: () => void;
    disableSave?: boolean;
}

import { useMantineColorScheme, useMantineTheme } from '@mantine/core';

const AIInsightsSection: React.FC<AIInsightsSectionProps> = ({
    summaryState,
    isSpeaking,
    saving,
    saveError,
    docLink,
    handleTTS,
    handleSaveSummaryToDoc,
    disableSave = false,
}) => {
    const { colorScheme } = useMantineColorScheme();
    const theme = useMantineTheme();
    const isDark = colorScheme === 'dark';
    const navigate = useNavigate();
    const integrations = useAppSelector(state => state.tools.integrations);
    const googleDocs = integrations?.find(t => t.id === 'google-docs');
    const [modalOpen, setModalOpen] = useState(false);

    return (
        <>
            <Modal
                opened={modalOpen}
                onClose={() => setModalOpen(false)}
                title="Google Docs Integration Required"
                centered
            >
                <Text mb="md">
                    To save to Google Docs, you need to integrate your Google account first.
                </Text>
                <Group position="right">
                    <Button variant="default" onClick={() => setModalOpen(false)}>
                        Cancel
                    </Button>
                    <Button color="blue" onClick={() => { setModalOpen(false); navigate('/tools'); }}>
                        Integrate Now
                    </Button>
                </Group>
            </Modal>

            <Paper
                p={30}
                radius="xl"
                withBorder
                shadow="sm"
                style={{
                    background: isDark ? 'rgba(36, 37, 46, 0.98)' : 'rgba(245, 247, 250, 0.98)',
                    border: `1px solid ${isDark ? theme.colors.dark[5] : theme.colors.gray[2]}`,
                    color: isDark ? theme.white : theme.colors.dark[7],
                    boxShadow: isDark
                        ? '0 2px 8px rgba(0,0,0,0.10)'
                        : '0 2px 8px rgba(99,102,241,0.04)'
                }}
            >
                <Group justify="space-between" mb="lg">
                    <Title order={3} style={{ color: isDark ? theme.colors.indigo[2] : theme.colors.indigo[7] }}>
                        <i className="fas fa-magic mr-2" style={{ color: isDark ? '#a5b4fc' : '#6366f1', marginRight: 8 }}></i>
                        AI Insights
                    </Title>
                    <Button
                        variant={isDark ? 'light' : 'white'}
                        color="indigo"
                        radius="md"
                        onClick={handleTTS}
                        loading={isSpeaking}
                        disabled={!summaryState.summary || summaryState.loading}
                        leftSection={<i className="fas fa-volume-up"></i>}
                        style={{
                            border: `1px solid ${isDark ? theme.colors.indigo[6] : theme.colors.gray[2]}`,
                            color: isDark ? theme.colors.indigo[2] : theme.colors.indigo[7],
                            background: isDark ? 'rgba(40, 41, 54, 0.95)' : 'rgba(255,255,255,0.95)',
                            transition: 'background 0.2s, color 0.2s',
                            boxShadow: isDark ? '0 1px 4px rgba(0,0,0,0.08)' : '0 1px 4px rgba(99,102,241,0.03)'
                        }}
                        onMouseOver={e => {
                            (e.currentTarget as HTMLButtonElement).style.background = isDark ? theme.colors.indigo[8] : theme.colors.gray[0];
                            (e.currentTarget as HTMLButtonElement).style.color = isDark ? theme.colors.indigo[1] : theme.colors.indigo[7];
                        }}
                        onMouseOut={e => {
                            (e.currentTarget as HTMLButtonElement).style.background = isDark ? 'rgba(40, 41, 54, 0.95)' : 'rgba(255,255,255,0.95)';
                            (e.currentTarget as HTMLButtonElement).style.color = isDark ? theme.colors.indigo[2] : theme.colors.indigo[7];
                        }}
                    >
                        Listen to Summary
                    </Button>
                </Group>

                {summaryState.loading ? (
                    <Stack align="center" py="xl">
                        <Loader size="lg" color="indigo" type="dots" />
                        <Text size="sm" c="dimmed" fw={500}>
                            Generating comprehensive summary...
                        </Text>
                    </Stack>
                ) : summaryState.summary ? (
                    <Box>
                        {/* Markdown-formatted Summary */}
                        <Box
                            className="ai-insights-markdown"
                            mb="lg"
                            style={{ color: isDark ? theme.white : theme.colors.dark[7] }}
                        >
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    // Headers
                                    h1: ({ children }) => (
                                        <Text component="h1" size="xl" fw={700} mb="sm" mt="lg" c="indigo.8">
                                            {children}
                                        </Text>
                                    ),
                                    h2: ({ children }) => (
                                        <Text component="h2" size="lg" fw={700} mb="xs" mt="md" c="indigo.7">
                                            {children}
                                        </Text>
                                    ),
                                    h3: ({ children }) => (
                                        <Text component="h3" size="md" fw={600} mb="xs" mt="sm" c="indigo.6">
                                            {children}
                                        </Text>
                                    ),
                                    h4: ({ children }) => (
                                        <Text component="h4" size="sm" fw={600} mb="xs" mt="sm" c="dark.6">
                                            {children}
                                        </Text>
                                    ),

                                    // Paragraphs
                                    p: ({ children }) => (
                                        <Text
                                            component="p"
                                            size="sm"
                                            mb="sm"
                                            style={{
                                                lineHeight: 1.7,
                                                color: isDark ? theme.white : theme.colors.dark[7],
                                            }}
                                        >
                                            {children}
                                        </Text>
                                    ),

                                    // Lists
                                    ul: ({ children }) => (
                                        <Box
                                            component="ul"
                                            pl="lg"
                                            mb="md"
                                            style={{
                                                listStyleType: 'disc',
                                                listStylePosition: 'outside',
                                            }}
                                        >
                                            {children}
                                        </Box>
                                    ),
                                    ol: ({ children }) => (
                                        <Box
                                            component="ol"
                                            pl="lg"
                                            mb="md"
                                            style={{
                                                listStyleType: 'decimal',
                                                listStylePosition: 'outside',
                                            }}
                                        >
                                            {children}
                                        </Box>
                                    ),
                                    li: ({ children }) => (
                                        <Text
                                            component="li"
                                            size="sm"
                                            mb="xs"
                                            pl="xs"
                                            style={{
                                                lineHeight: 1.7,
                                                color: isDark ? theme.white : theme.colors.dark[7],
                                            }}
                                        >
                                            {children}
                                        </Text>
                                    ),

                                    // Inline code
                                    code: ({ inline, className, children, ...props }: any) => {
                                        const match = /language-(\w+)/.exec(className || '');
                                        return !inline && match ? (
                                            <Box mb="sm" style={{ borderRadius: '8px', overflow: 'hidden' }}>
                                                <SyntaxHighlighter
                                                    style={oneDark}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    customStyle={{
                                                        margin: 0,
                                                        borderRadius: '8px',
                                                        fontSize: '13px',
                                                        color: isDark ? theme.white : theme.colors.dark[7],
                                                    }}
                                                    {...props}
                                                >
                                                    {String(children).replace(/\n$/, '')}
                                                </SyntaxHighlighter>
                                            </Box>
                                        ) : (
                                            <Text
                                                component="code"
                                                size="sm"
                                                px={6}
                                                py={2}
                                                style={{
                                                    backgroundColor: 'var(--mantine-color-gray-1)',
                                                    color: isDark ? theme.white : 'var(--mantine-color-indigo-7)',
                                                    borderRadius: '4px',
                                                    fontFamily: 'monospace',
                                                    fontSize: '0.9em',
                                                    fontWeight: 500,
                                                }}
                                            >
                                                {children}
                                            </Text>
                                        );
                                    },

                                    // Strong (bold)
                                    strong: ({ children }) => (
                                        <Text component="strong" fw={700} c="indigo.8" inherit>
                                            {children}
                                        </Text>
                                    ),

                                    // Emphasis (italic)
                                    em: ({ children }) => (
                                        <Text component="em" fs="italic" inherit>
                                            {children}
                                        </Text>
                                    ),

                                    // Blockquote
                                    blockquote: ({ children }) => (
                                        <Paper
                                            p="sm"
                                            pl="md"
                                            mb="sm"
                                            radius="md"
                                            style={{
                                                borderLeft: '4px solid var(--mantine-color-indigo-5)',
                                                backgroundColor: 'var(--mantine-color-gray-0)',
                                                fontStyle: 'italic',
                                            }}
                                        >
                                            <Text size="sm" c="dimmed">
                                                {children}
                                            </Text>
                                        </Paper>
                                    ),

                                    // Links
                                    a: ({ href, children }) => (
                                        <Text
                                            component="a"
                                            href={href}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            c="indigo.6"
                                            style={{
                                                textDecoration: 'underline',
                                                cursor: 'pointer',
                                                fontWeight: 500,
                                            }}
                                            inherit
                                        >
                                            {children}
                                        </Text>
                                    ),

                                    // Horizontal rule
                                    hr: () => (
                                        <Box
                                            component="hr"
                                            my="md"
                                            style={{
                                                border: 'none',
                                                borderTop: '1px solid var(--mantine-color-gray-3)',
                                            }}
                                        />
                                    ),

                                    // Tables
                                    table: ({ children }) => (
                                        <Box style={{ overflowX: 'auto' }} mb="sm">
                                            <table
                                                style={{
                                                    width: '100%',
                                                    borderCollapse: 'collapse',
                                                    fontSize: '0.875rem',
                                                }}
                                            >
                                                {children}
                                            </table>
                                        </Box>
                                    ),
                                    th: ({ children }) => (
                                        <th
                                            style={{
                                                padding: '8px 12px',
                                                textAlign: 'left',
                                                backgroundColor: 'var(--mantine-color-gray-1)',
                                                fontWeight: 600,
                                                borderBottom: '2px solid var(--mantine-color-gray-3)',
                                            }}
                                        >
                                            {children}
                                        </th>
                                    ),
                                    td: ({ children }) => (
                                        <td
                                            style={{
                                                padding: '8px 12px',
                                                borderBottom: '1px solid var(--mantine-color-gray-2)',
                                            }}
                                        >
                                            {children}
                                        </td>
                                    ),
                                }}
                            >
                                {summaryState.summary}
                            </ReactMarkdown>
                        </Box>

                        {/* Cited Sources */}
                        {
                            summaryState.sources && summaryState.sources.length > 0 && (
                                <Box mt="xl" pt="md" style={{ borderTop: '1px solid var(--mantine-color-gray-2)' }}>
                                    <Group mb="sm" gap="xs">
                                        <i className="fas fa-link text-sm" style={{ color: 'var(--mantine-color-dimmed)' }}></i>
                                        <Text size="xs" fw={700} c="dimmed" tt="uppercase" style={{ letterSpacing: '0.5px' }}>
                                            Cited Sources ({summaryState.sources.length})
                                        </Text>
                                    </Group>
                                    <Stack gap="xs">
                                        {summaryState.sources.map((source: any, index: number) => (
                                            <Paper
                                                key={index}
                                                p="xs"
                                                px="sm"
                                                radius="md"
                                                withBorder
                                                style={{
                                                    backgroundColor: 'var(--mantine-color-gray-0)',
                                                    borderColor: 'var(--mantine-color-gray-2)',
                                                    transition: 'all 0.2s ease',
                                                    cursor: 'default',
                                                }}
                                                className="source-card"
                                            >
                                                <Group gap="xs" wrap="nowrap">
                                                    <Box
                                                        style={{
                                                            minWidth: '24px',
                                                            height: '24px',
                                                            borderRadius: '50%',
                                                            backgroundColor: 'var(--mantine-color-indigo-1)',
                                                            color: 'var(--mantine-color-indigo-6)',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center',
                                                            fontSize: '11px',
                                                            fontWeight: 700,
                                                        }}
                                                    >
                                                        {index + 1}
                                                    </Box>
                                                    <Box style={{ flex: 1, minWidth: 0 }}>
                                                        <Text size="xs" c="dark" lineClamp={2} style={{ lineHeight: 1.5 }}>
                                                            "{source.text_preview}"
                                                        </Text>
                                                        <Group gap={4} mt={4}>
                                                            <Text size="10px" c="dimmed" fw={500}>
                                                                Relevance: {(source.relevance_score * 100).toFixed(0)}%
                                                            </Text>
                                                            <Text size="10px" c="dimmed">•</Text>
                                                            <Text size="10px" c="dimmed" fw={500}>
                                                                {source.chunk_id}
                                                            </Text>
                                                        </Group>
                                                    </Box>
                                                </Group>
                                            </Paper>
                                        ))}
                                    </Stack>
                                </Box>
                            )
                        }

                        {/* Action Buttons */}
                        <Box mt="xl" pt="md" style={{ borderTop: '1px solid var(--mantine-color-gray-2)' }}>
                            <Group gap="sm">
                                <Button
                                    onClick={() => {
                                        if (!googleDocs?.isConnected) {
                                            setModalOpen(true);
                                        } else {
                                            handleSaveSummaryToDoc();
                                        }
                                    }}
                                    loading={saving}
                                    disabled={docLink || disableSave}
                                    color="blue"
                                    variant="light"
                                    radius="md"
                                    leftSection={<i className="fas fa-file-word"></i>}
                                >
                                    Save to Google Doc
                                </Button>

                                {docLink && (
                                    <Button
                                        component="a"
                                        href={docLink}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        variant="outline"
                                        color="blue"
                                        radius="md"
                                        rightSection={<i className="fas fa-external-link-alt text-xs"></i>}
                                    >
                                        View Document
                                    </Button>
                                )}
                            </Group>

                            {/* Only show error if saveError exists and not due to missing docLink */}
                            {saveError && !(!docLink) && (
                                <Paper p="sm" mt="sm" radius="md" bg="red.0" style={{ border: '1px solid var(--mantine-color-red-2)' }}>
                                    <Group gap="xs">
                                        <i className="fas fa-exclamation-circle" style={{ color: 'var(--mantine-color-red-6)' }}></i>
                                        <Text size="sm" c="red.7">
                                            {saveError}
                                        </Text>
                                    </Group>
                                </Paper>
                            )}
                        </Box>
                    </Box >
                ) : summaryState.error ? (
                    <Paper p="lg" radius="md" bg="red.0" style={{ border: '1px solid var(--mantine-color-red-2)' }}>
                        <Group gap="sm" mb="xs">
                            <i className="fas fa-exclamation-triangle" style={{ color: 'var(--mantine-color-red-6)', fontSize: '20px' }}></i>
                            <Text size="md" fw={600} c="red.7">
                                Error Loading Summary
                            </Text>
                        </Group>
                        <Text size="sm" c="red.6">
                            {summaryState.error}
                        </Text>
                    </Paper>
                ) : (
                    <Paper p="lg" radius="md" bg="gray.0" style={{ border: '1px solid var(--mantine-color-gray-2)' }}>
                        <Stack align="center" gap="sm">
                            <i className="fas fa-info-circle" style={{ fontSize: '24px', color: 'var(--mantine-color-gray-5)' }}></i>
                            <Text size="sm" c="dimmed" ta="center">
                                No summary available. Click "Generate Summary" to create one.
                            </Text>
                        </Stack>
                    </Paper>
                )}
            </Paper >
        </>
    );
};

export default AIInsightsSection;