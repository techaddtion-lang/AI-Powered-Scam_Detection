import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, 
  PhoneCall, 
  Globe, 
  History, 
  ShieldCheck, 
  Zap, 
  Lock, 
  Sparkles, 
  Terminal, 
  FileText,
  BarChart3,
  Database,
  Radio
} from 'lucide-react';
import Navbar from './components/Navbar';
import MessageAnalyzer from './components/MessageAnalyzer';
import CallTranscriptAnalyzer from './components/CallTranscriptAnalyzer';
import UrlScanner from './components/UrlScanner';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import ThreatIntelligenceView from './components/ThreatIntelligenceView';
import apiService from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('analytics');
  const [samples, setSamples] = useState([]);
  const [isOnline, setIsOnline] = useState(false);
  const [engineInfo, setEngineInfo] = useState(null);

  // Load samples and check backend health on mount
  useEffect(() => {
    async function init() {
      try {
        const health = await apiService.checkHealth();
        setIsOnline(health.status === 'healthy' || health.status === 'degraded');
        setEngineInfo(health);
      } catch (err) {
        console.warn('API connection check failed:', err);
        setIsOnline(false);
      }

      try {
        const sampleData = await apiService.getSamples();
        setSamples(sampleData);
      } catch (err) {
        console.warn('Could not fetch preset samples:', err);
      }
    }

    init();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
      {/* Top Enterprise Navigation */}
      <Navbar isOnline={isOnline} engineInfo={engineInfo} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Enterprise Threat Detection Banner */}
        <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-6 sm:p-9 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-1/3 -mb-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 text-xs font-semibold">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>Connected to MySQL 8.0 (scamshield_db) Threat Registry</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white leading-tight">
              Enterprise Scam Call & <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-cyan-400 via-indigo-300 to-pink-400 bg-clip-text text-transparent">
                Phishing Threat Intelligence
              </span>
            </h1>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
              Professional fraud defense platform. Detects smishing, vishing (voice OTP theft), and brand spoofing using calibrated NLP machine learning, a 9-vector heuristic risk engine, and persistent MySQL threat registries.
            </p>

            {/* Micro Feature Badges */}
            <div className="pt-2 flex flex-wrap gap-3 text-xs text-slate-300">
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 font-mono">
                <Database className="w-3.5 h-3.5 text-emerald-400" />
                <span>MySQL Audit Trails</span>
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>Vishing & Live OTP Defense</span>
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
                <Globe className="w-3.5 h-3.5 text-cyan-400" />
                <span>Phishing Domain Intelligence</span>
              </div>
            </div>
          </div>
        </section>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800 space-x-1 sm:space-x-2 overflow-x-auto pb-0.5">
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center space-x-2 px-4 py-3 rounded-t-xl text-xs sm:text-sm font-bold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'analytics'
                ? 'border-emerald-400 text-emerald-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Threat Operations & MySQL Audit Log</span>
          </button>

          <button
            onClick={() => setActiveTab('message')}
            className={`flex items-center space-x-2 px-4 py-3 rounded-t-xl text-xs sm:text-sm font-bold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'message'
                ? 'border-cyan-400 text-cyan-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Message & SMS Scanner</span>
          </button>

          <button
            onClick={() => setActiveTab('call')}
            className={`flex items-center space-x-2 px-4 py-3 rounded-t-xl text-xs sm:text-sm font-bold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'call'
                ? 'border-indigo-400 text-indigo-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <PhoneCall className="w-4 h-4" />
            <span>Call Transcript (Vishing) Analyzer</span>
          </button>

          <button
            onClick={() => setActiveTab('url')}
            className={`flex items-center space-x-2 px-4 py-3 rounded-t-xl text-xs sm:text-sm font-bold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'url'
                ? 'border-cyan-400 text-cyan-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>Direct Phishing URL Scanner</span>
          </button>

          <button
            onClick={() => setActiveTab('intel')}
            className={`flex items-center space-x-2 px-4 py-3 rounded-t-xl text-xs sm:text-sm font-bold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'intel'
                ? 'border-rose-400 text-rose-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <Database className="w-4 h-4" />
            <span>Blacklist Threat Intel (MySQL)</span>
          </button>
        </div>

        {/* Tab Content Display */}
        <div className="pt-2">
          {activeTab === 'analytics' && <AnalyticsDashboard />}

          {activeTab === 'message' && <MessageAnalyzer samples={samples} />}

          {activeTab === 'call' && <CallTranscriptAnalyzer samples={samples} />}

          {activeTab === 'url' && <UrlScanner />}

          {activeTab === 'intel' && <ThreatIntelligenceView />}
        </div>
      </main>

      {/* Enterprise Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-8 mt-16 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold text-slate-400">
              ScamShield AI Enterprise
            </span>
            <span>—</span>
            <span className="font-mono text-cyan-400">FastAPI + MySQL 8.0 + Scikit-Learn + React</span>
          </div>

          <div className="flex items-center space-x-6 text-slate-400">
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-cyan-400 transition-colors flex items-center space-x-1"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Swagger API Docs</span>
            </a>
            <span className="text-slate-700">|</span>
            <span className="font-mono text-[11px] text-emerald-400">
              MySQL: scamshield_db (3306)
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

