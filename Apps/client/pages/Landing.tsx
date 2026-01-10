import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import {
  ArrowRight, Zap, FileText, MessageSquare,
  CheckCircle, PlayCircle, Globe,
  Clock, Shield, Star,
  Check,
  ExternalLink
} from 'lucide-react';

export const Landing: React.FC = () => {
  const { darkMode } = useApp();
  const navigate = useNavigate();

  const textColorMain = darkMode ? 'text-white' : 'text-gray-900';
  const textColorSub = darkMode ? 'text-gray-400' : 'text-gray-600';
  const bgCard = darkMode ? 'bg-[#25262B] border-gray-800' : 'bg-white border-gray-200';

  return (
    <div className="relative flex flex-col items-center animate-fade-in overflow-hidden">
      {/* Background Glows */}
      <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-[600px] md:w-[1000px] h-[600px] rounded-full blur-[120px] -z-10 pointer-events-none ${darkMode ? 'bg-blue-900/20' : 'bg-blue-200/50'}`} />
      <div className={`absolute bottom-0 right-0 w-[800px] h-[600px] rounded-full blur-[120px] -z-10 pointer-events-none ${darkMode ? 'bg-purple-900/10' : 'bg-purple-100/40'}`} />

      {/* ================= HERO SECTION ================= */}
      <div className="w-full max-w-7xl mx-auto pt-20 md:pt-32 pb-20 px-6 text-center relative z-10">
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-8 border backdrop-blur-sm shadow-sm ${darkMode ? 'bg-blue-900/20 border-blue-800 text-blue-300' : 'bg-white border-blue-100 text-blue-700'}`}>
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-500"></span>
          </span>
          <span>New: GPT-4o Integration Live</span>
        </div>

        <h1 className="text-5xl md:text-7xl lg:text-8xl font-extrabold tracking-tight mb-8 leading-[1.1]">
          <span className={textColorMain}>Video intelligence,</span>
          <br />
          <span className="bg-gradient-to-r from-blue-600 via-indigo-500 to-cyan-500 bg-clip-text text-transparent animate-gradient bg-300%">
            simplified.
          </span>
        </h1>

        <p className={`text-xl md:text-2xl max-w-3xl mx-auto mb-12 leading-relaxed ${textColorSub}`}>
          Transform hour-long content into minute-long insights. Chat with videos, extract summaries, and learn 10x faster.
        </p>

        <div className="flex flex-col sm:flex-row gap-5 justify-center items-center mb-20">
          <button
            onClick={() => navigate('/sign-up')}
            className="group relative px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white text-lg font-bold rounded-xl shadow-xl hover:shadow-2xl hover:shadow-blue-500/20 transition-all duration-300 transform hover:-translate-y-1 w-full sm:w-auto"
          >
            Start Analyzing for Free
            <ArrowRight className="inline ml-2 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={() => navigate('/sign-in')}
            className={`px-8 py-4 rounded-xl font-semibold transition-all border w-full sm:w-auto flex items-center justify-center gap-2 ${darkMode ? 'border-gray-700 text-gray-300 hover:bg-white/5' : 'border-gray-200 text-gray-700 hover:bg-gray-50'}`}
          >
            <PlayCircle size={20} />
            See How It Works
          </button>
        </div>
      </div>


      {/* ================= SOCIAL PROOF ================= */}
      <div className={`w-full py-12 border-y ${darkMode ? 'bg-black/20 border-gray-800' : 'bg-gray-50/50 border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-6">
          <p className={`text-center text-sm font-semibold uppercase tracking-wider mb-8 ${textColorSub}`}>Trusted by learners at top organizations</p>
          <div className={`flex flex-wrap justify-center gap-8 md:gap-16 opacity-60 grayscale hover:grayscale-0 transition-all duration-500 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            {/* Simple text logos for demo purposes */}
            <span className="text-xl font-bold">ACME Corp</span>
            <span className="text-xl font-bold">TechStart</span>
            <span className="text-xl font-bold">EduGlobal</span>
            <span className="text-xl font-bold">FutureScale</span>
            <span className="text-xl font-bold">DevPoint</span>
          </div>
        </div>
      </div>

      {/* ================= PROBLEM / SOLUTION (ZIG ZAG) ================= */}
      <div className="w-full max-w-7xl mx-auto px-6 py-24 space-y-32">

        {/* Section 1: Image Left, Text Right */}
        <div className="flex flex-col lg:flex-row items-center gap-16">
          <div className="flex-1 relative group">
            <div className={`absolute -inset-4 rounded-3xl blur-2xl opacity-30 transition-opacity duration-500 group-hover:opacity-50 ${darkMode ? 'bg-blue-600' : 'bg-blue-400'}`} />
            <img
              src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=1200&auto=format&fit=crop"
              alt="Analyzing data"
              className="relative rounded-2xl shadow-2xl w-full object-cover h-[400px]"
            />
          </div>
          <div className="flex-1 space-y-6">
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${darkMode ? 'bg-blue-900/30 text-blue-400' : 'bg-blue-100 text-blue-700'}`}>
              <Zap size={14} /> Smart Analysis
            </div>
            <h2 className={`text-4xl md:text-5xl font-bold ${textColorMain}`}>Don't just watch.<br />Understand.</h2>
            <p className={`text-lg leading-relaxed ${textColorSub}`}>
              The average educational video is 22 minutes long. Finding the one specific answer you need takes time.
              <br /><br />
              YT Genius processes the audio, visual, and semantic context of videos to create a searchable, interactive knowledge base instantly.
            </p>
            <ul className="space-y-4 pt-4">
              {[
                "Semantic search across hours of content",
                "Automatic chapter detection",
                "Key concept extraction"
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-3">
                  <CheckCircle className="text-green-500 flex-shrink-0" size={20} />
                  <span className={textColorMain}>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Section 2: Text Left, Image Right */}
        <div className="flex flex-col-reverse lg:flex-row items-center gap-16">
          <div className="flex-1 space-y-6">
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${darkMode ? 'bg-purple-900/30 text-purple-400' : 'bg-purple-100 text-purple-700'}`}>
              <Globe size={14} /> Universal Access
            </div>
            <h2 className={`text-4xl md:text-5xl font-bold ${textColorMain}`}>Break language barriers instantly.</h2>
            <p className={`text-lg leading-relaxed ${textColorSub}`}>
              Found a great tutorial but it's in a language you don't speak? No problem.
              <br /><br />
              Our AI translates concepts and answers questions in your native language, regardless of the video's original audio. It's like having a personal interpreter for the entire internet.
            </p>
            <div className="pt-6 flex gap-4">
              <div className={`flex flex-col gap-1 p-4 rounded-xl border ${bgCard}`}>
                <span className="text-2xl font-bold text-blue-500">50+</span>
                <span className={`text-sm ${textColorSub}`}>Languages</span>
              </div>
              <div className={`flex flex-col gap-1 p-4 rounded-xl border ${bgCard}`}>
                <span className="text-2xl font-bold text-purple-500">0.2s</span>
                <span className={`text-sm ${textColorSub}`}>Latency</span>
              </div>
            </div>
          </div>
          <div className="flex-1 relative group">
            <div className={`absolute -inset-4 rounded-3xl blur-2xl opacity-30 transition-opacity duration-500 group-hover:opacity-50 ${darkMode ? 'bg-purple-600' : 'bg-purple-400'}`} />
            <img
              src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=1200&auto=format&fit=crop"
              alt="Collaboration"
              className="relative rounded-2xl shadow-2xl w-full object-cover h-[400px]"
            />
          </div>
        </div>
      </div>

      {/* ================= FEATURES GRID ================= */}
      <div className={`w-full py-24 ${darkMode ? 'bg-[#1A1B1E]/50' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className={`text-3xl md:text-4xl font-bold mb-6 ${textColorMain}`}>Everything you need to learn faster</h2>
            <p className={`text-lg ${textColorSub}`}>Built for students, researchers, content creators, and lifelong learners.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Zap, color: 'text-blue-500', bg: 'bg-blue-500/10', title: 'Instant Summaries', desc: 'Get the gist without watching the fluff. AI-generated executive summaries.' },
              { icon: MessageSquare, color: 'text-purple-500', bg: 'bg-purple-500/10', title: 'Interactive Chat', desc: 'Ask specific questions and get answers cited with timestamps.' },
              { icon: FileText, color: 'text-green-500', bg: 'bg-green-500/10', title: 'Smart Transcripts', desc: 'Full-text search through the spoken words of any video.' },
              { icon: Clock, color: 'text-orange-500', bg: 'bg-orange-500/10', title: 'Time Saver', desc: 'Jump exactly to the moment a topic is discussed.' },
              { icon: Shield, color: 'text-red-500', bg: 'bg-red-500/10', title: 'Privacy First', desc: 'We do not store your personal data or watch history.' },
              { icon: Star, color: 'text-yellow-500', bg: 'bg-yellow-500/10', title: 'Premium Insights', desc: 'Advanced reasoning models for complex technical topics.' },
            ].map((feature, i) => (
              <div key={i} className={`p-8 rounded-3xl border transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${bgCard}`}>
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${feature.bg}`}>
                  <feature.icon className={feature.color} size={28} />
                </div>
                <h3 className={`text-xl font-bold mb-3 ${textColorMain}`}>{feature.title}</h3>
                <p className={`text-base leading-relaxed ${textColorSub}`}>
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ================= TESTIMONIALS ================= */}
      <div className="w-full max-w-7xl mx-auto px-6 py-24">
        <h2 className={`text-3xl md:text-4xl font-bold text-center mb-16 ${textColorMain}`}>Loved by the Community</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { name: "Sarah Jenkins", role: "Medical Student", text: "This tool literally saved my finals. I can search through 3-hour lecture videos for specific terms instantly.", img: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150" },
            { name: "David Chen", role: "Software Engineer", text: "The code extraction feature is a game changer. I don't have to type out what I see on screen anymore.", img: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150" },
            { name: "Emily Blunt", role: "Content Creator", text: "I use this to research competitors. It summarizes their key points so I can make better content.", img: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=150" }
          ].map((user, i) => (
            <div key={i} className={`p-8 rounded-2xl border relative ${bgCard}`}>
              <div className="flex items-center gap-4 mb-6">
                <img src={user.img} alt={user.name} className="w-12 h-12 rounded-full object-cover" />
                <div>
                  <div className={`font-bold ${textColorMain}`}>{user.name}</div>
                  <div className={`text-xs uppercase tracking-wide ${textColorSub}`}>{user.role}</div>
                </div>
              </div>
              <p className={`italic ${textColorSub}`}>"{user.text}"</p>
              <div className="absolute top-8 right-8 text-yellow-500 flex gap-1">
                {[1, 2, 3, 4, 5].map(s => <Star key={s} size={12} fill="currentColor" />)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ================= FAQ SECTION ================= */}
      <div className={`w-full py-24 ${darkMode ? 'bg-[#1A1B1E]/50' : 'bg-gray-50'}`}>
        <div className="max-w-3xl mx-auto px-6">
          <h2 className={`text-3xl font-bold text-center mb-12 ${textColorMain}`}>Frequently Asked Questions</h2>
          <div className="space-y-4">
            {[
              { q: "Is YT Genius free?", a: "Yes, our basic plan allows for unlimited video analysis for videos under 30 minutes." },
              { q: "Does it work with Private videos?", a: "No, we can only access public or unlisted YouTube videos due to API restrictions." },
              { q: "Can I export the transcript?", a: "Absolutely. You can copy the transcript or chat history to your clipboard with one click." },
              { q: "What languages are supported?", a: "We support over 50 languages for both transcription and chat interaction." }
            ].map((item, i) => (
              <div key={i} className={`p-6 rounded-xl border ${bgCard}`}>
                <h3 className={`font-bold text-lg mb-2 ${textColorMain}`}>{item.q}</h3>
                <p className={textColorSub}>{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ================= PRICING SECTION ================= */}
      <div className={`w-full py-24 ${darkMode ? 'bg-[#1A1B1E]/50' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className={`text-3xl md:text-4xl font-bold mb-6 ${textColorMain}`}>Choose your learning path</h2>
            <p className={`text-lg ${textColorSub}`}>Flexible options for casual viewers and power users alike.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">

            {/* Plan 1: Free Tier */}
            <div className={`p-8 rounded-3xl border flex flex-col relative ${bgCard} ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
              <div className="mb-6">
                <h3 className={`text-xl font-bold mb-2 ${textColorMain}`}>Casual</h3>
                <div className="flex items-baseline gap-1">
                  <span className={`text-4xl font-extrabold ${textColorMain}`}>Free</span>
                </div>
                <p className={`text-sm mt-2 ${textColorSub}`}>Perfect for occasional research.</p>
              </div>
              <ul className="space-y-4 mb-8 flex-1">
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>3 Videos per day</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>Standard Summary Model</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>Videos under 30 mins</span>
                </li>
              </ul>
              <button onClick={() => navigate('/sign-up')} className={`w-full py-3 rounded-xl font-bold border transition-colors ${darkMode ? 'border-gray-700 hover:bg-gray-800' : 'border-gray-200 hover:bg-gray-50'} ${textColorMain}`}>
                Start Browsing
              </button>
            </div>

            {/* Plan 2: BYO Key (Highlighted) */}
            <div className={`p-8 rounded-3xl border-2 flex flex-col relative transform md:-translate-y-4 shadow-2xl ${darkMode ? 'bg-blue-900/10 border-blue-500' : 'bg-blue-50/50 border-blue-500'}`}>
              <div className="absolute top-0 right-0 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-bl-xl rounded-tr-xl">
                MOST POPULAR
              </div>
              <div className="mb-6">
                <h3 className={`text-xl font-bold mb-2 ${textColorMain}`}>Power User</h3>
                <div className="flex items-baseline gap-1">
                  <span className={`text-4xl font-extrabold ${textColorMain}`}>Free</span>
                  <span className={`text-sm font-medium ${textColorSub}`}>/ forever</span>
                </div>
                <p className={`text-sm mt-2 flex flex-col gap-1 ${textColorSub}`}>
                  <span>Bring your own Gemini API Key.</span>
                  <a
                    href="https://aistudio.google.com/app/apikey"
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-500 hover:underline inline-flex items-center gap-1"
                  >
                    Get a free key here <ExternalLink size={12} />
                  </a>
                </p>
              </div>
              <ul className="space-y-4 mb-8 flex-1">
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={`font-bold ${textColorMain}`}>Unlimited Videos</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>Access Gemini 1.5 Pro</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>Private & Secure</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>No speed limits</span>
                </li>
              </ul>
              <button onClick={() => navigate('/sign-up')} className="w-full py-3 rounded-xl font-bold bg-blue-600 hover:bg-blue-700 text-white transition-colors shadow-lg shadow-blue-500/25">
                Connect API Key
              </button>
            </div>

            {/* Plan 3: Credit Based */}
            <div className={`p-8 rounded-3xl border flex flex-col relative ${bgCard} ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
              <div className="mb-6">
                <h3 className={`text-xl font-bold mb-2 ${textColorMain}`}>Pro Credits</h3>
                <div className="flex items-baseline gap-1">
                  <span className={`text-4xl font-extrabold ${textColorMain}`}>$10</span>
                  <span className={`text-sm font-medium ${textColorSub}`}>/ 50 credits</span>
                </div>
                <p className={`text-sm mt-2 ${textColorSub}`}>Pay as you go. No subscriptions.</p>
              </div>
              <ul className="space-y-4 mb-8 flex-1">
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>1 Credit = 1 Video Analysis</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>Priority Processing</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>Cloud History Storage</span>
                </li>
                <li className="flex items-center gap-3 text-sm">
                  <Check className="text-blue-500 flex-shrink-0" size={18} />
                  <span className={textColorSub}>No Setup Required</span>
                </li>
              </ul>
              <button onClick={() => navigate('/sign-up')} className={`w-full py-3 rounded-xl font-bold border transition-colors ${darkMode ? 'border-gray-700 hover:bg-gray-800' : 'border-gray-200 hover:bg-gray-50'} ${textColorMain}`}>
                Buy Credits
              </button>
            </div>

          </div>
        </div>
      </div>

      {/* ================= FINAL CTA ================= */}
      <div className="w-full px-6 py-20">
        <div className={`max-w-5xl mx-auto rounded-3xl p-12 text-center relative overflow-hidden ${darkMode ? 'bg-gradient-to-br from-blue-900 to-indigo-900' : 'bg-gradient-to-br from-blue-600 to-indigo-600'}`}>
          <div className="relative z-10">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Ready to upgrade your learning?</h2>
            <p className="text-blue-100 text-lg md:text-xl mb-8 max-w-2xl mx-auto">
              Join thousands of users who are saving hours every week. No credit card required.
            </p>
            <button
              onClick={() => navigate('/sign-up')}
              className="bg-white text-blue-600 hover:bg-blue-50 px-10 py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1"
            >
              Get Started Now
            </button>
          </div>

          {/* Decorative Circles */}
          <div className="absolute top-0 left-0 w-64 h-64 bg-white opacity-5 rounded-full -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-white opacity-10 rounded-full translate-x-1/3 translate-y-1/3" />
        </div>
      </div>

      {/* ================= FOOTER ================= */}
      <div className={`w-full py-12 text-center border-t text-sm ${darkMode ? 'border-gray-800 text-gray-600' : 'border-gray-200 text-gray-400'}`}>
        <div className="flex items-center justify-center gap-2 mb-4">
          <span className="font-bold text-lg">YT Genius</span>
        </div>
        <div className="flex justify-center gap-6 mb-8">
          <a href="#" className="hover:text-blue-500 transition-colors">Features</a>
          <a href="#" className="hover:text-blue-500 transition-colors">Pricing</a>
          <a href="#" className="hover:text-blue-500 transition-colors">Blog</a>
          <a href="#" className="hover:text-blue-500 transition-colors">Contact</a>
        </div>
        <p>© 2024 YT Genius AI. All rights reserved.</p>
      </div>
    </div>
  );
};