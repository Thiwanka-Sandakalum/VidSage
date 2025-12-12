import React, { useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, Youtube, Github, Home, Library, BarChart3, User } from 'lucide-react';
import { SignedIn, SignedOut, SignInButton, UserButton, useAuth } from '@clerk/clerk-react';


export const LayoutFrame: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isSignedIn, isLoaded } = useAuth();
  const navigate = useNavigate();
  const { darkMode, resetApp, toggleDarkMode } = useApp();

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'bg-[#1A1B1E] text-white' : 'bg-[#f8f9fa] text-gray-900'}`}>
      {/* Header */}
      <header className={`sticky top-0 z-50 border-b ${darkMode ? 'bg-[#1A1B1E]/95 border-gray-800' : 'bg-white/95 border-gray-200'} backdrop-blur-sm`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div
            className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={resetApp}
          >
            <div className="bg-red-600 p-1.5 rounded-lg text-white">
              <Youtube size={24} />
            </div>
            <span className="font-bold text-xl tracking-tight">YT Genius</span>
          </div>

          {/* Navigation */}
          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => navigate('/home')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${window.location.pathname === '/home'
                ? darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'
                : darkMode ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
            >
              <Home size={18} />
              <span className="text-sm font-medium">Home</span>
            </button>

            <button
              onClick={() => navigate('/library')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${window.location.pathname === '/library'
                ? darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'
                : darkMode ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
            >
              <Library size={18} />
              <span className="text-sm font-medium">Library</span>
            </button>

            <button
              onClick={() => navigate('/dashboard')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${window.location.pathname.startsWith('/dashboard')
                ? darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'
                : darkMode ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
            >
              <BarChart3 size={18} />
              <span className="text-sm font-medium">Dashboard</span>
            </button>

            <button
              onClick={() => navigate('/profile')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${window.location.pathname === '/profile'
                ? darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'
                : darkMode ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
            >
              <User size={18} />
              <span className="text-sm font-medium">Profile</span>
            </button>
          </nav>

          <div className="flex items-center gap-4">
            {/* Authentication Buttons */}
            <SignedOut>
              <SignInButton mode="modal">
                <button
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${darkMode
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                    }`}
                >
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>

            <SignedIn>
              <UserButton
                afterSignOutUrl="/"
                appearance={{
                  elements: {
                    avatarBox: 'w-9 h-9'
                  }
                }}
              />
            </SignedIn>

            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-full transition-colors ${darkMode ? 'bg-gray-800 hover:bg-gray-700 text-yellow-400' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              aria-label="Toggle Dark Mode"
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className={`hidden sm:flex p-2 rounded-full transition-colors ${darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-gray-100 hover:bg-gray-200'}`}
            >
              <Github size={18} />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};