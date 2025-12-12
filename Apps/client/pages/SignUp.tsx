import React from 'react';
import { SignUp as ClerkSignUp } from '@clerk/clerk-react';
import { useApp } from '../context/AppContext';
import { Youtube, Sparkles, Zap, Globe, CheckCircle } from 'lucide-react';

export const SignUp: React.FC = () => {
    const { darkMode } = useApp();

    return (
        <div className={`min-h-screen w-full flex ${darkMode ? 'bg-[#1A1B1E]' : 'bg-gray-50'}`}>
            {/* Left Side - Sign Up Form */}
            <div className={`flex-1 flex items-center justify-center p-8 ${darkMode ? 'bg-[#1A1B1E]' : 'bg-white'}`}>
                <div className="w-full max-w-md">
                    {/* Mobile Logo */}
                    <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
                        <div className="bg-red-600 p-2 rounded-xl text-white shadow-lg">
                            <Youtube size={28} />
                        </div>
                        <span className={`font-bold text-2xl tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                            YT Genius
                        </span>
                    </div>

                    <ClerkSignUp
                        appearance={{
                            layout: {
                                socialButtonsPlacement: 'bottom',
                                socialButtonsVariant: 'iconButton',
                                termsPageUrl: 'https://yourapp.com/terms',
                                privacyPageUrl: 'https://yourapp.com/privacy',
                                logoPlacement: 'none'
                            },
                            variables: {
                                colorPrimary: '#2563eb',
                                colorBackground: darkMode ? '#1A1B1E' : '#ffffff',
                                colorText: darkMode ? '#ffffff' : '#111827',
                                colorTextSecondary: darkMode ? '#9ca3af' : '#6b7280',
                                colorInputBackground: darkMode ? '#25262B' : '#f9fafb',
                                colorInputText: darkMode ? '#ffffff' : '#111827',
                                colorDanger: darkMode ? '#f87171' : '#dc2626',
                                borderRadius: '0.75rem',
                                fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                                fontSize: '0.9375rem',
                                spacingUnit: '1rem'
                            },
                            elements: {
                                rootBox: 'w-full',
                                card: `shadow-2xl ${darkMode ? 'bg-[#25262B] border border-gray-800' : 'bg-white border border-gray-100'} rounded-2xl overflow-hidden`,

                                // Header
                                headerTitle: `text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-2`,
                                headerSubtitle: `text-base ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-6`,

                                // Form Elements
                                formButtonPrimary: 'bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-[1.02] rounded-xl',
                                formFieldInput: `${darkMode ? 'bg-[#1A1B1E] border-gray-700 text-white placeholder:text-gray-500' : 'bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400'} focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all rounded-xl py-3`,
                                formFieldLabel: `${darkMode ? 'text-gray-300' : 'text-gray-700'} font-medium text-sm mb-2`,
                                formFieldInputShowPasswordButton: darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-700',

                                // Social Buttons
                                socialButtonsBlockButton: `${darkMode ? 'bg-[#1A1B1E] border-gray-700 hover:bg-gray-800 text-white' : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-900'} rounded-xl transition-all`,
                                socialButtonsIconButton: `${darkMode ? 'bg-[#1A1B1E] border-gray-700 hover:bg-gray-800' : 'bg-white border-gray-200 hover:bg-gray-50'} rounded-xl w-12 h-12 transition-all hover:scale-105`,
                                socialButtonsProviderIcon: 'w-5 h-5',

                                // Divider
                                dividerLine: darkMode ? 'bg-gray-700' : 'bg-gray-200',
                                dividerText: `${darkMode ? 'text-gray-500' : 'text-gray-500'} text-sm`,

                                // Footer
                                footer: `${darkMode ? 'bg-[#25262B]' : 'bg-white'} pt-6`,
                                footerAction: `${darkMode ? 'bg-[#25262B]' : 'bg-gray-50'} px-6 py-4 rounded-xl mt-4`,
                                footerActionText: `${darkMode ? 'text-gray-400' : 'text-gray-600'} text-sm`,
                                footerActionLink: 'text-blue-600 hover:text-blue-700 font-semibold hover:underline ml-1',
                                footerPages: `${darkMode ? 'bg-[#25262B]' : 'bg-white'}`,
                                footerPagesLink: 'text-blue-600 hover:text-blue-700 text-sm',
                                footer__termsLinks: 'text-xs',
                                footer__privacyLinks: 'text-xs',

                                // Additional Elements
                                identityPreviewText: darkMode ? 'text-gray-300' : 'text-gray-700',
                                identityPreviewEditButton: 'text-blue-600 hover:text-blue-700 text-sm font-medium',
                                formResendCodeLink: 'text-blue-600 hover:text-blue-700 font-medium text-sm',
                                formButtonReset: `${darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`,
                                otpCodeFieldInput: `${darkMode ? 'bg-[#1A1B1E] border-gray-700 text-white' : 'bg-gray-50 border-gray-200 text-gray-900'} focus:ring-2 focus:ring-blue-500 rounded-lg text-center font-semibold`,

                                // Error & Success States
                                alertText: `${darkMode ? 'text-red-400' : 'text-red-600'} text-sm`,
                                formFieldErrorText: `${darkMode ? 'text-red-400' : 'text-red-600'} text-sm mt-1`,
                                formFieldSuccessText: `${darkMode ? 'text-green-400' : 'text-green-600'} text-sm mt-1`,
                                formFieldHintText: `${darkMode ? 'text-gray-500' : 'text-gray-500'} text-sm mt-1`
                            }
                        }}
                        path="/sign-up"
                        routing="path"
                        signInUrl="/sign-in"
                        afterSignInUrl="/home"
                        afterSignUpUrl="/home"
                        forceRedirectUrl="/home"
                    />
                </div>
            </div>

            {/* Right Side - Benefits & Features */}
            <div className={`hidden lg:flex lg:w-1/2 relative overflow-hidden ${darkMode ? 'bg-gradient-to-br from-indigo-900/20 via-blue-900/20 to-cyan-900/20' : 'bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50'}`}>
                {/* Background Glows */}
                <div className={`absolute top-0 right-0 w-96 h-96 rounded-full blur-[120px] ${darkMode ? 'bg-indigo-600/20' : 'bg-indigo-400/30'}`} />
                <div className={`absolute bottom-0 left-0 w-96 h-96 rounded-full blur-[120px] ${darkMode ? 'bg-cyan-600/20' : 'bg-cyan-400/30'}`} />

                <div className="relative z-10 flex flex-col justify-between p-12 w-full">
                    {/* Logo & Brand */}
                    <div className="flex items-center gap-3">
                        <div className="bg-red-600 p-2 rounded-xl text-white shadow-lg">
                            <Youtube size={32} />
                        </div>
                        <span className={`font-bold text-2xl tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                            YT Genius
                        </span>
                    </div>

                    {/* Main Content */}
                    <div className="space-y-8">
                        <div className="space-y-4">
                            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${darkMode ? 'bg-blue-900/30 text-blue-400' : 'bg-blue-100 text-blue-700'}`}>
                                <Sparkles size={16} />
                                <span className="text-sm font-semibold">Start Free Today</span>
                            </div>

                            <h1 className={`text-5xl font-bold leading-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                                Transform how you
                                <br />
                                <span className="bg-gradient-to-r from-indigo-600 via-blue-500 to-cyan-600 bg-clip-text text-transparent">
                                    learn from videos
                                </span>
                            </h1>
                            <p className={`text-lg ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                Join thousands of learners who are accelerating their education
                            </p>
                        </div>

                        {/* Benefits List */}
                        <div className="space-y-4 pt-8">
                            {[
                                {
                                    icon: Zap,
                                    title: 'Lightning Fast Processing',
                                    description: 'Analyze hours of content in seconds with advanced AI'
                                },
                                {
                                    icon: Globe,
                                    title: 'Multi-Language Support',
                                    description: 'Break language barriers with 50+ supported languages'
                                },
                                {
                                    icon: CheckCircle,
                                    title: 'Always Free to Start',
                                    description: 'No credit card required. Upgrade when you\'re ready'
                                }
                            ].map((benefit, index) => (
                                <div key={index} className="flex items-start gap-4 group">
                                    <div className={`p-2 rounded-lg transition-all duration-300 group-hover:scale-110 ${darkMode ? 'bg-indigo-900/30 text-indigo-400' : 'bg-indigo-100 text-indigo-600'}`}>
                                        <benefit.icon size={20} />
                                    </div>
                                    <div>
                                        <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                                            {benefit.title}
                                        </h3>
                                        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                            {benefit.description}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Stats */}
                        <div className="pt-8 grid grid-cols-3 gap-6">
                            {[
                                { value: '10K+', label: 'Active Users' },
                                { value: '1M+', label: 'Videos Analyzed' },
                                { value: '50+', label: 'Languages' }
                            ].map((stat, index) => (
                                <div key={index} className={`text-center p-4 rounded-xl ${darkMode ? 'bg-[#1A1B1E]/50' : 'bg-white/50'} backdrop-blur-sm`}>
                                    <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                                        {stat.value}
                                    </div>
                                    <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                        {stat.label}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Footer Trust Badge */}
                    <div className={`flex items-center gap-3 p-4 rounded-xl ${darkMode ? 'bg-[#1A1B1E]/50' : 'bg-white/50'} backdrop-blur-sm`}>
                        <CheckCircle className="text-green-500" size={24} />
                        <div>
                            <p className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                                Trusted & Secure
                            </p>
                            <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                Enterprise-grade security for your data
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
