import React from 'react';
import { useApp } from '../context/AppContext';
import { Loader2, CheckCircle2, Circle } from 'lucide-react';
import { ProcessingStep } from '../types';

export const ProcessingStatusPanel: React.FC = () => {
  const { processingStep, darkMode } = useApp();

  const steps: { key: ProcessingStep; label: string }[] = [
    { key: 'fetching', label: 'Fetching video metadata & transcript' },
    { key: 'chunking', label: 'Chunking text for analysis' },
    { key: 'embedding', label: 'Generating vector embeddings' },
    { key: 'saving', label: 'Finalizing knowledge base' },
  ];

  const getCurrentIndex = () => {
    if (processingStep === 'complete') return steps.length;
    return steps.findIndex(s => s.key === processingStep);
  };

  const activeIndex = getCurrentIndex();
  const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';

  return (
    <div className={`max-w-md mx-auto mt-20 p-8 rounded-xl shadow-lg border ${cardBg}`}>
      <div className="text-center mb-8">
        <h2 className="text-xl font-bold mb-2">Processing Video...</h2>
        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          Please wait while we analyze the content.
        </p>
      </div>

      <div className="space-y-6">
        {steps.map((step, index) => {
          const isCompleted = index < activeIndex;
          const isCurrent = index === activeIndex;

          return (
            <div key={step.key} className="flex items-center gap-4">
              <div className="flex-shrink-0">
                {isCompleted ? (
                  <CheckCircle2 className="text-green-500 w-6 h-6" />
                ) : isCurrent ? (
                  <Loader2 className="animate-spin text-blue-500 w-6 h-6" />
                ) : (
                  <Circle className={`w-6 h-6 ${darkMode ? 'text-gray-700' : 'text-gray-300'}`} />
                )}
              </div>
              <div className={`flex-1 text-sm font-medium ${isCompleted ? (darkMode ? 'text-gray-300' : 'text-gray-700') :
                  isCurrent ? 'text-blue-500' :
                    (darkMode ? 'text-gray-600' : 'text-gray-400')
                }`}>
                {step.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};