import '../assets/styles/index.css';
import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store/store';
import { useAuth, ClerkProvider } from '@clerk/clerk-react';
import { Notifications } from '@mantine/notifications';
import { MantineProvider } from '@mantine/core';
import { OpenAPI } from '../services';
import { clerkAppearance } from '../utils/clerkAppearance';
import App from './App';

const configs = (window as any).config || {};
const AppWithAPI = () => {
  const { getToken } = useAuth();
  OpenAPI.BASE = configs.API_BASE_URL;
  useEffect(() => {
    OpenAPI.TOKEN = (async () => {
      try {
        const token = await getToken();
        return token;
      } catch (error) {
        console.error('Failed to get auth token:', error);
        return null;
      }
    });
  }, [getToken]);

  return <App />;
};

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <ClerkProvider
      publishableKey={configs.CLERK_PUBLISHABLE_KEY}
      signInUrl="/login"
      signUpUrl="/sign-up"
      appearance={clerkAppearance}
    >
      <Provider store={store}>
        <MantineProvider defaultColorScheme="light">
          <Notifications position="top-right" zIndex={2000} />
          <AppWithAPI />
        </MantineProvider>
      </Provider>
    </ClerkProvider>
  </React.StrictMode>
);
