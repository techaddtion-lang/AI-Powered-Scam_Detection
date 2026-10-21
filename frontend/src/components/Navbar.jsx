import React from 'react';
import { Shield, Database, Activity, ExternalLink, Cpu, Radio } from 'lucide-react';

export default function Navbar({ isOnline, engineInfo }) {
  const isMysqlConnected = engineInfo?.mysql_connected;

  return (
    <header className="border-b border-slate-800/80 bg-slate-900/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Enterprise SOC Identifier */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-slate-900" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                ScamShield<span className="text-cyan-400 font-mono">.AI</span>
              </span>
              <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Enterprise SOC
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Real-time Scam Call & Phishing Threat Intelligence Center
            </p>
          </div>
        </div>

        {/* System Status & Database Telemetry Badges */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          
          {/* MySQL Database Status Indicator */}
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/90 border border-slate-700/80 text-xs">
            <Database className={`w-3.5 h-3.5 ${isMysqlConnected ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-slate-300 font-mono text-[11px] font-semibold">
              MySQL 8.0: <strong className={isMysqlConnected ? 'text-emerald-400' : 'text-amber-400'}>{isMysqlConnected ? 'scamshield_db' : 'Connecting...'}</strong>
            </span>
          </div>

          {/* Model Status Pill */}
          {engineInfo?.model_loaded && (
            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-indigo-950/50 text-indigo-300 border border-indigo-800/50 text-[11px] font-mono">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>TF-IDF + Calibrated ML</span>
            </div>
          )}

          {/* FastAPI Docs Link */}
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center space-x-1 text-xs text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 transition-colors border border-slate-700 font-medium"
            title="Open Interactive FastAPI Swagger Documentation"
          >
            <span>Swagger API</span>
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
        </div>
      </div>
    </header>
  );
}

