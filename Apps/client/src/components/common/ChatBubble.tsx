import React from 'react';
import { Group, Avatar, Paper, Text, Box, Stack } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ChatMessage } from '../../types/types';
import './ChatBubble.css'; // Ensure ChatBubble.css is in the same directory as ChatBubble.tsx

interface ChatBubbleProps {
  message: ChatMessage;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const isAssistant = message.role === 'assistant';

  return (
    <Box mb="xl" style={{ display: 'flex', justifyContent: isAssistant ? 'flex-start' : 'flex-end' }}>
      <Group
        align="flex-start"
        gap="sm"
        style={{
          maxWidth: '92%',
          flexDirection: isAssistant ? 'row' : 'row-reverse'
        }}
      >
        <Avatar
          size="md"
          radius="xl"
          variant={isAssistant ? 'filled' : 'light'}
          color={isAssistant ? 'indigo' : 'gray'}
          style={{
            border: isAssistant ? 'none' : '2px solid var(--mantine-color-gray-2)',
            flexShrink: 0,
            background: isAssistant
              ? 'linear-gradient(135deg, #6366f1 0%, #a5b4fc 100%)'
              : undefined,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {isAssistant ? (
            // Bot logo: brain icon with sparkles, visually distinct
            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <i className="fas fa-brain" style={{ fontSize: 18, color: '#fff', marginRight: 2 }}></i>
              <i className="fas fa-sparkles" style={{ fontSize: 12, color: '#fbbf24' }}></i>
            </span>
          ) : (
            <i className="fas fa-user text-xs"></i>
          )}
        </Avatar>

        <Stack gap={4} align={isAssistant ? 'flex-start' : 'flex-end'} style={{ flex: 1, minWidth: 0 }}>
          <Paper
            p="md"
            radius="xl"
            bg={isAssistant ? 'white' : 'indigo.6'}
            c={isAssistant ? 'dark.8' : 'white'}
            withBorder={isAssistant}
            shadow={isAssistant ? 'xs' : 'none'}
            style={{
              borderRadius: isAssistant ? '0 20px 20px 20px' : '20px 0 20px 20px',
              border: isAssistant ? '1px solid var(--mantine-color-gray-2)' : 'none',
              lineHeight: 1.6,
              width: '100%',
              overflow: 'hidden'
            }}
          >
            {isAssistant ? (
              <div className={`markdown-content ${isAssistant ? 'assistant-markdown' : 'user-markdown'}`}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Headers
                    h1: ({ children }) => (
                      <Text component="h1" size="xl" fw={700} mb="sm" mt="md" c="indigo.8">
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
                      <Text component="p" size="sm" mb="sm" style={{ lineHeight: 1.6 }}>
                        {children}
                      </Text>
                    ),

                    // Lists
                    ul: ({ children }) => (
                      <Box component="ul" pl="md" mb="sm" style={{
                        listStyleType: 'disc',
                        listStylePosition: 'outside'
                      }}>
                        {children}
                      </Box>
                    ),
                    ol: ({ children }) => (
                      <Box component="ol" pl="md" mb="sm" style={{
                        listStyleType: 'decimal',
                        listStylePosition: 'outside'
                      }}>
                        {children}
                      </Box>
                    ),
                    li: ({ children }) => (
                      <Text component="li" size="sm" mb="xs" pl="xs" style={{ lineHeight: 1.6 }}>
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
                              fontSize: '13px'
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
                            color: 'var(--mantine-color-indigo-7)',
                            borderRadius: '4px',
                            fontFamily: 'monospace',
                            fontSize: '0.9em',
                            fontWeight: 500
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
                          fontStyle: 'italic'
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
                          fontWeight: 500
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
                          borderTop: '1px solid var(--mantine-color-gray-3)'
                        }}
                      />
                    ),

                    // Tables
                    table: ({ children }) => (
                      <Box style={{ overflowX: 'auto' }} mb="sm">
                        <table style={{
                          width: '100%',
                          borderCollapse: 'collapse',
                          fontSize: '0.875rem'
                        }}>
                          {children}
                        </table>
                      </Box>
                    ),
                    th: ({ children }) => (
                      <th style={{
                        padding: '8px 12px',
                        textAlign: 'left',
                        backgroundColor: 'var(--mantine-color-gray-1)',
                        fontWeight: 600,
                        borderBottom: '2px solid var(--mantine-color-gray-3)'
                      }}>
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td style={{
                        padding: '8px 12px',
                        borderBottom: '1px solid var(--mantine-color-gray-2)'
                      }}>
                        {children}
                      </td>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            ) : (
              <Text size="sm" fw={400} style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {message.content}
              </Text>
            )}
          </Paper>

          <Text
            size="10px"
            c="dimmed"
            fw={700}
            tt="uppercase"
            style={{ letterSpacing: '0.5px' }}
          >
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Text>
        </Stack>
      </Group>
    </Box>
  );
};

export default ChatBubble;