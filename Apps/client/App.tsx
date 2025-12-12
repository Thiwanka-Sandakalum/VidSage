import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LayoutFrame } from './components/LayoutFrame';
import { Home } from './pages/Home';
import { Dashboard } from './pages/Dashboard';
import { Landing } from './pages/Landing';
import { Library } from './pages/Library';
import { SignIn } from './pages/SignIn';
import { SignUp } from './pages/SignUp';
import { SignedIn, SignedOut, useAuth } from '@clerk/clerk-react';
import { Profile } from './pages/Profile';
import apiClient from './config/api.config';
import { AppProvider } from './context/AppContext';


function App() {
  const { isLoaded, getToken } = useAuth();

  useEffect(() => {
    apiClient.interceptors.request.use(
      async (config) => {
        const token = await getToken(); if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
  }, []);


  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#1A1B1E]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <AppProvider>
      <Router>
        <Routes>
          <Route path="/sign-in/*" element={<SignIn />} />
          <Route path="/sign-up/*" element={<SignUp />} />
          <Route
            path="/*"
            element={
              <LayoutFrame>
                <SignedOut>
                  <Landing />
                </SignedOut>

                <SignedIn>
                  <Routes>
                    <Route path="/" element={<Navigate to="/home" replace />} />
                    <Route path="/home" element={<Home />} />
                    <Route path="/dashboard/:videoId" element={<Dashboard />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/library" element={<Library />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="*" element={<Navigate to="/home" replace />} />
                  </Routes>
                </SignedIn>
              </LayoutFrame>
            }
          />
        </Routes>
      </Router>
    </AppProvider>
  );
}

export default App;