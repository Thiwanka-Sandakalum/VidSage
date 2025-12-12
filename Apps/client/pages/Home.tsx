import React from 'react';
import { UrlInputCard } from '../components/UrlInputCard';
import { ProcessingStatusPanel } from '../components/ProcessingStatusPanel';
import { useApp } from '../context/AppContext';

export const Home: React.FC = () => {
  const { processingStep } = useApp();

  return (
    <div className="animate-fade-in">
      {processingStep === 'idle' && <UrlInputCard />}
      {processingStep !== 'idle' && <ProcessingStatusPanel />}
    </div>
  );
};