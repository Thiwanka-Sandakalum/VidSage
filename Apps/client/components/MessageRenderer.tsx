import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';

interface MessageRendererProps {
    content: string;
    darkMode: boolean;
}

export const MessageRenderer: React.FC<MessageRendererProps> = ({ content, darkMode }) => {
    return (
        <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
                code(props: any) {
                    const { node, inline, className, children, ...rest } = props;
                    const match = /language-(\w+)/.exec(className || '');
                    const language = match ? match[1] : '';

                    return !inline && language ? (
                        <div className="my-3">
                            <div className={`text-xs px-3 py-1 rounded-t-lg font-mono ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-700'
                                }`}>
                                {language}
                            </div>
                            <SyntaxHighlighter
                                style={darkMode ? (vscDarkPlus as any) : (vs as any)}
                                language={language}
                                PreTag="div"
                                className="rounded-b-lg !mt-0"
                                customStyle={{
                                    margin: 0,
                                    borderTopLeftRadius: 0,
                                    borderTopRightRadius: 0,
                                }}
                                {...rest}
                            >
                                {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                        </div>
                    ) : (
                        <code
                            className={`px-1.5 py-0.5 rounded text-xs font-mono ${darkMode ? 'bg-gray-700 text-blue-300' : 'bg-gray-100 text-blue-600'
                                }`}
                            {...rest}
                        >
                            {children}
                        </code>
                    );
                },
                pre({ children }) {
                    return <>{children}</>;
                },
                h1({ children }) {
                    return <h1 className="text-2xl font-bold mt-4 mb-2">{children}</h1>;
                },
                h2({ children }) {
                    return <h2 className="text-xl font-bold mt-3 mb-2">{children}</h2>;
                },
                h3({ children }) {
                    return <h3 className="text-lg font-semibold mt-2 mb-1">{children}</h3>;
                },
                ul({ children }) {
                    return <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>;
                },
                ol({ children }) {
                    return <ol className="list-decimal list-inside my-2 space-y-1">{children}</ol>;
                },
                blockquote({ children }) {
                    return (
                        <blockquote className={`border-l-4 pl-4 my-2 italic ${darkMode ? 'border-gray-600' : 'border-gray-300'
                            }`}>
                            {children}
                        </blockquote>
                    );
                },
                a({ href, children }) {
                    return (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-500 hover:underline"
                        >
                            {children}
                        </a>
                    );
                },
                table({ children }) {
                    return (
                        <div className="overflow-x-auto my-3">
                            <table className={`min-w-full border ${darkMode ? 'border-gray-700' : 'border-gray-300'
                                }`}>
                                {children}
                            </table>
                        </div>
                    );
                },
                th({ children }) {
                    return (
                        <th className={`px-4 py-2 border font-semibold ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-300 bg-gray-100'
                            }`}>
                            {children}
                        </th>
                    );
                },
                td({ children }) {
                    return (
                        <td className={`px-4 py-2 border ${darkMode ? 'border-gray-700' : 'border-gray-300'
                            }`}>
                            {children}
                        </td>
                    );
                },
            }}
        >
            {content}
        </ReactMarkdown>
    );
};
