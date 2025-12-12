import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useApp } from '../context/AppContext';
import { useUser } from '@clerk/clerk-react';
import { Settings, Zap, Clock, MessageSquare, Brain, Key, EyeOff, Eye, Shield, User, Mail, LogOut } from 'lucide-react';

interface ProfileFormData {
    geminiApiKey: string;
    geminiModel: string;
    firstName: string;
    lastName: string;

}

export const Profile: React.FC = () => {
    const [showApiKey, setShowApiKey] = useState(false);
    const { darkMode, resetApp } = useApp();
    const { user: clerkUser } = useUser();
    const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

    const { register, handleSubmit, setValue } = useForm<ProfileFormData>({
        defaultValues: {
            geminiApiKey: '',
            geminiModel: 'gemini-2.5-flash',
            firstName: '',
            lastName: '',
        }
    });

    useEffect(() => {
        if (clerkUser) {
            setValue('firstName', clerkUser.firstName || '');
            setValue('lastName', clerkUser.lastName || '');
            setValue('geminiApiKey', (clerkUser.unsafeMetadata?.geminiApiKey as string) || '');
        }
    }, [clerkUser, setValue]);

    const stats = {
        videosAnalyzed: 42,
        minutesSaved: 123,
        questionsAsked: 17,
    };

    const [autoSummary, setAutoSummary] = useState(true);
    const [emailNotifications, setEmailNotifications] = useState(false);
    const [defaultLanguage, setDefaultLanguage] = useState('English');

    const onSubmit = async (data: ProfileFormData) => {
        console.log('Form submitted:', data);
        try {
            await clerkUser?.update({
                firstName: data.firstName,
                lastName: data.lastName,
                unsafeMetadata: {
                    geminiApiKey: data.geminiApiKey,
                    geminiModel: data.geminiModel
                }
            });
            setNotification({ type: 'success', message: 'Settings saved successfully!' });
        } catch (error) {
            console.error('Error saving settings:', error);
            setNotification({ type: 'error', message: 'Failed to save settings. Please try again.' });
        }
        setTimeout(() => setNotification(null), 3000);
    };
    const cardBg = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';
    const textMain = darkMode ? 'text-white' : 'text-gray-900';
    const textSub = darkMode ? 'text-gray-400' : 'text-gray-500';
    const inputBg = darkMode ? 'bg-[#1A1B1E] border-gray-700 text-white' : 'bg-white border-gray-300 text-gray-900';

    const userName = clerkUser ? `${clerkUser.firstName || ''} ${clerkUser.lastName || ''}`.trim() || 'User' : 'User';
    const userEmail = clerkUser?.primaryEmailAddress?.emailAddress || 'user@example.com';
    const userAvatar = clerkUser?.imageUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}`;

    return (
        <div className="max-w-5xl mx-auto animate-fade-in pb-12">
            <h1 className={`text-3xl font-bold mb-8 ${textMain}`}>Account Settings</h1>

            {/* Notification Banner */}
            {notification && (
                <div
                    className={`mb-6 px-4 py-3 rounded-lg flex items-center gap-2 shadow-md transition-all duration-300
                        ${notification.type === 'success'
                            ? 'bg-green-100 border border-green-300 text-green-800'
                            : 'bg-red-100 border border-red-300 text-red-800'}
                    `}
                    role="alert"
                >
                    {notification.type === 'success' ? (
                        <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                    ) : (
                        <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                    )}
                    <span>{notification.message}</span>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                <div className="space-y-8">
                    <div className={`p-6 rounded-2xl border shadow-sm ${cardBg}`}>
                        <div className="flex flex-col items-center text-center">
                            <div className="relative mb-4 group">
                                <img
                                    src={userAvatar}
                                    alt={userName}
                                    className="w-24 h-24 rounded-full border-4 border-blue-500/20 object-cover"
                                />
                                <button className="absolute bottom-0 right-0 p-1.5 bg-blue-600 rounded-full text-white hover:bg-blue-700 transition-colors">
                                    <Settings size={14} />
                                </button>
                            </div>
                            <h2 className={`text-xl font-bold mb-1 ${textMain}`}>{userName}</h2>
                            <p className={`text-sm mb-4 ${textSub}`}>{userEmail}</p>

                            <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-purple-500 to-blue-500 text-white`}>
                                Pro Plan
                            </div>
                        </div>
                    </div>

                    {/* Stats Summary - Vertical on Desktop Left */}
                    <div className={`p-6 rounded-2xl border shadow-sm ${cardBg}`}>
                        <h3 className={`text-sm font-bold uppercase tracking-wider mb-6 ${textSub}`}>Lifetime Stats</h3>
                        <div className="space-y-6">
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-xl bg-blue-500/10 text-blue-500">
                                    <Zap size={20} />
                                </div>
                                <div>
                                    <div className={`text-2xl font-bold ${textMain}`}>{stats.videosAnalyzed}</div>
                                    <div className={`text-xs ${textSub}`}>Videos Analyzed</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-xl bg-green-500/10 text-green-500">
                                    <Clock size={20} />
                                </div>
                                <div>
                                    <div className={`text-2xl font-bold ${textMain}`}>{Math.round(stats.minutesSaved / 60)}h {stats.minutesSaved % 60}m</div>
                                    <div className={`text-xs ${textSub}`}>Time Saved</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-xl bg-purple-500/10 text-purple-500">
                                    <MessageSquare size={20} />
                                </div>
                                <div>
                                    <div className={`text-2xl font-bold ${textMain}`}>{stats.questionsAsked}</div>
                                    <div className={`text-xs ${textSub}`}>Questions Asked</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="lg:col-span-2 space-y-8">
                    <div className={`p-8 rounded-2xl border shadow-sm relative overflow-hidden ${cardBg}`}>
                        <div className={`absolute top-0 right-0 w-64 h-64 opacity-5 pointer-events-none rounded-full blur-3xl -mr-16 -mt-16 ${darkMode ? 'bg-blue-400' : 'bg-blue-600'}`} />

                        <div className="flex items-center gap-3 mb-6 relative z-10">
                            <Brain className="text-blue-500" size={24} />
                            <h2 className={`text-xl font-bold ${textMain}`}>AI Configuration</h2>
                        </div>

                        <div className="space-y-6 relative z-10">
                            <div className={`p-4 rounded-lg border flex gap-3 ${darkMode ? 'bg-blue-900/10 border-blue-900/30' : 'bg-blue-50 border-blue-100'}`}>
                                <Zap className="text-blue-500 flex-shrink-0 mt-0.5" size={18} />
                                <p className={`text-sm ${textSub}`}>
                                    Bring your own API key to bypass rate limits and access advanced models for free.
                                    Your key is stored locally in your browser.
                                </p>
                            </div>

                            <div>
                                <label className={`block text-sm font-medium mb-2 ${textMain}`}>Gemini API Key</label>
                                <div className="relative">
                                    <Key className="absolute left-3 top-3 text-gray-400" size={18} />
                                    <input
                                        type={showApiKey ? "text" : "password"}
                                        {...register('geminiApiKey')}
                                        placeholder="AIzaSy..."
                                        className={`w-full pl-10 pr-10 p-3 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowApiKey(!showApiKey)}
                                        className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                                    >
                                        {showApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                                <div className="mt-2 text-xs text-gray-500 flex justify-between">
                                    <span>Don't have a key? <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">Get one here</a></span>
                                </div>
                            </div>

                            <div>
                                <label className={`block text-sm font-medium mb-2 ${textMain}`}>Preferred Model</label>
                                <select
                                    {...register('geminiModel')}
                                    className={`w-full p-3 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                                >
                                    <option value="gemini-2.5-flash">Gemini 2.5 Flash (Fastest)</option>
                                    <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                                    <option value="gemini-3-pro-preview">Gemini 3.0 Pro (Best Reasoning)</option>
                                </select>
                                <p className={`text-xs mt-2 ${textSub}`}>
                                    Flash models are recommended for summaries. Pro models are better for complex Q&A.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* App Preferences */}
                    <div className={`p-8 rounded-2xl border shadow-sm ${cardBg}`}>
                        <div className="flex items-center gap-3 mb-6">
                            <Settings className="text-gray-500" size={24} />
                            <h2 className={`text-xl font-bold ${textMain}`}>Application Preferences</h2>
                        </div>

                        <div className="space-y-6">
                            <div className="flex items-center justify-between pb-6 border-b border-gray-200 dark:border-gray-800">
                                <div>
                                    <h3 className={`font-medium ${textMain}`}>Auto-Generate Summaries</h3>
                                    <p className={`text-sm ${textSub}`}>Automatically create a summary when a video loads.</p>
                                </div>
                                <button
                                    onClick={() => setAutoSummary(!autoSummary)}
                                    className={`w-12 h-6 rounded-full transition-colors relative ${autoSummary ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'}`}
                                >
                                    <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${autoSummary ? 'translate-x-6' : ''}`} />
                                </button>
                            </div>

                            <div className="flex items-center justify-between pb-6 border-b border-gray-200 dark:border-gray-800">
                                <div>
                                    <h3 className={`font-medium ${textMain}`}>Email Notifications</h3>
                                    <p className={`text-sm ${textSub}`}>Receive weekly usage reports and product updates.</p>
                                </div>
                                <button
                                    onClick={() => setEmailNotifications(!emailNotifications)}
                                    className={`w-12 h-6 rounded-full transition-colors relative ${emailNotifications ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'}`}
                                >
                                    <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${emailNotifications ? 'translate-x-6' : ''}`} />
                                </button>
                            </div>

                            <div>
                                <label className={`block text-sm font-medium mb-2 ${textMain}`}>Default Language for Answers</label>
                                <select
                                    value={defaultLanguage}
                                    onChange={(e) => setDefaultLanguage(e.target.value)}
                                    className={`w-full p-3 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                                >
                                    <option>English</option>
                                    <option>Spanish</option>
                                    <option>French</option>
                                    <option>German</option>
                                    <option>Japanese</option>
                                </select>
                                <p className={`text-xs mt-2 ${textSub}`}>The AI will attempt to translate answers to this language.</p>
                            </div>
                        </div>
                    </div>

                    {/* Personal Information */}
                    <div className={`p-8 rounded-2xl border shadow-sm ${cardBg}`}>
                        <div className="flex items-center gap-3 mb-6">
                            <Shield className="text-green-500" size={24} />
                            <h2 className={`text-xl font-bold ${textMain}`}>Personal Information</h2>
                        </div>

                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <label className={`block text-sm font-medium mb-2 ${textMain}`}>First Name</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-3 text-gray-400" size={18} />
                                    <input
                                        type="text"
                                        {...register('firstName')}
                                        className={`w-full pl-10 p-3 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className={`block text-sm font-medium mb-2 ${textMain}`}>Last Name</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-3 text-gray-400" size={18} />
                                    <input
                                        type="text"
                                        {...register('lastName')}
                                        className={`w-full pl-10 p-3 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className={`block text-sm font-medium mb-2 ${textMain}`}>Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-3 text-gray-400" size={18} />
                                    <input
                                        type="email"
                                        value={userEmail}
                                        readOnly
                                        className={`w-full pl-10 p-3 rounded-lg border outline-none focus:ring-2 focus:ring-blue-500 opacity-60 cursor-not-allowed ${inputBg}`}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={handleSubmit(onSubmit)}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/20">
                                Save Changes
                            </button>
                        </div>
                    </div>

                    <div className="pt-8 border-t border-gray-200 dark:border-gray-800">
                        <button
                            onClick={resetApp}
                            className="flex items-center gap-2 text-red-500 hover:text-red-600 font-medium transition-colors"
                        >
                            <LogOut size={18} />
                            Sign Out
                        </button>
                    </div>

                </div>
            </div>
        </div>
    );
}
