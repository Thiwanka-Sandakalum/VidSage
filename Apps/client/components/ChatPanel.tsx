import React, { useRef, useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { Send, Bot, User, Sparkles, Loader2, Maximize2, X, ChevronDown, ChevronUp } from 'lucide-react';
import { MessageRenderer } from './MessageRenderer';

export const ChatPanel: React.FC = () => {
  const { messages, isChatLoading, askQuestion, darkMode, videoId, suggestedQuestions, loadSuggestedQuestions } = useApp();
  const [input, setInput] = useState('');
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isChatLoading]);

  useEffect(() => {
    if (videoId && suggestedQuestions.length === 0) {
      setLoadingQuestions(true);
      loadSuggestedQuestions(videoId).finally(() => setLoadingQuestions(false));
    }
  }, [videoId]);

  useEffect(() => {
    if (isMaximized) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMaximized]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isChatLoading) return;

    const question = input;
    setInput('');
    await askQuestion(question);
  };

  const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';
  const chatAreaBg = darkMode ? 'bg-[#1A1B1E]' : 'bg-gray-50';
  const inputBg = darkMode ? 'bg-[#1A1B1E] border-gray-700 text-white' : 'bg-white border-gray-300 text-gray-900';

  const ChatContent = () => (
    <>
      <div className={`p-4 border-b flex items-center justify-between flex-shrink-0 ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
        <div className="flex items-center gap-2">
          <Sparkles className="text-blue-500" size={18} />
          <h3 className="font-bold text-lg">AI Assistant</h3>
        </div>
        <button
          onClick={() => setIsMaximized(!isMaximized)}
          className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          title={isMaximized ? 'Close' : 'Maximize'}
        >
          {isMaximized ? <X size={20} /> : <Maximize2 size={18} />}
        </button>
      </div>

      <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${chatAreaBg}`}>
        {messages.map((msg) => {
          const isAI = msg.role === 'ai';
          return (
            <div key={msg.id} className={`flex gap-3 ${isAI ? 'justify-start' : 'justify-end'}`}>
              {isAI && (
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${darkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-100 text-blue-600'}`}>
                  <Bot size={16} />
                </div>
              )}

              <div className="max-w-[80%] flex flex-col gap-2">
                <div className={`p-4 rounded-2xl text-sm leading-relaxed ${isAI
                  ? (darkMode ? 'bg-[#2C2E33] text-gray-100 rounded-tl-none' : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none shadow-sm')
                  : 'bg-blue-600 text-white rounded-tr-none shadow-sm'
                  }`}>
                  {isAI ? (
                    <MessageRenderer content={msg.content} darkMode={darkMode} />
                  ) : (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  )}
                </div>

                {msg.timestamp && (
                  <div className={`text-[10px] px-2 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                )}
              </div>

              {!isAI && (
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'}`}>
                  <User size={16} />
                </div>
              )}
            </div>
          );
        })}

        {isChatLoading && (
          <div className="flex gap-3 justify-start">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${darkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-100 text-blue-600'}`}>
              <Bot size={16} />
            </div>
            <div className={`p-3 rounded-2xl rounded-tl-none text-sm flex items-center gap-1 ${darkMode ? 'bg-[#2C2E33]' : 'bg-white border border-gray-200'}`}>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={`p-4 border-t flex-shrink-0 ${darkMode ? 'border-gray-800 bg-[#25262B]' : 'border-gray-200 bg-white'}`}>
        {suggestedQuestions.length > 0 && (
          <div className="mb-3">
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              className={`flex items-center gap-2 text-sm font-medium mb-2 ${darkMode ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}
            >
              <Sparkles size={14} />
              <span>Suggested Questions</span>
              {showSuggestions ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showSuggestions && (
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {loadingQuestions ? (
                  <div className="flex items-center gap-2 text-sm text-gray-500 py-2">
                    <Loader2 size={14} className="animate-spin" />
                    <span>Generating questions...</span>
                  </div>
                ) : (
                  suggestedQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        askQuestion(q);
                        setShowSuggestions(false);
                      }}
                      disabled={isChatLoading}
                      className={`w-full text-left text-xs px-3 py-2 rounded-lg border transition-all ${darkMode
                        ? 'border-gray-700 bg-gray-800 hover:bg-gray-700 text-gray-300'
                        : 'border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-700'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      {q}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about the video..."
            className={`w-full pl-4 pr-12 py-3 text-sm rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
          />
          <button
            type="submit"
            disabled={!input.trim() || isChatLoading}
            className="absolute right-2 top-2 p-1.5 rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </>
  );

  if (isMaximized) {
    return (
      <>
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity"
          onClick={() => setIsMaximized(false)}
        />
        <div className={`fixed inset-4 md:inset-8 lg:inset-16 z-50 flex flex-col rounded-2xl shadow-2xl overflow-hidden ${cardBg}`}>
          <ChatContent />
        </div>
      </>
    );
  }

  return (
    <div className={`flex flex-col h-[500px] lg:h-[600px] rounded-xl shadow-md border overflow-hidden ${cardBg}`}>
      <ChatContent />
    </div>
  );
};