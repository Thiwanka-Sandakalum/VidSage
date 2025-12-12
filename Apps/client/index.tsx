import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ClerkProvider } from '@clerk/clerk-react';
import './globals.css';

declare global {
  interface Window {
    appConfig?: {
      CLERK_PUBLISHABLE_KEY: string;
      API_BASE_URL: string;
      ENABLE_DEBUG_MODE: boolean;
      ENABLE_ANALYTICS: boolean;
    };
  }
}

const PUBLISHABLE_KEY = window.appConfig?.CLERK_PUBLISHABLE_KEY;

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <ClerkProvider
      publishableKey={PUBLISHABLE_KEY}
      afterSignOutUrl="/"
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
    >
      <App />
    </ClerkProvider>
  </React.StrictMode>
);