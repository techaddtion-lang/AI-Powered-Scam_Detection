import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function RiskGauge({ score = 0, classification = 'Safe', confidence = 0.95 }) {
  // Determine color scheme based on score & classification
  let theme = {
    color: 'text-emerald-400',
    stroke: '#10b981',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    glow: 'shadow-emerald-500/20',
    labelBg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    icon: ShieldCheck,
    title: 'Safe',
    desc: 'Low probability of malicious intent'
  };

  if (score >= 65 || classification === 'High Risk Scam') {
    theme = {
      color: 'text-rose-500',
      stroke: '#f43f5e',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/40',
      glow: 'shadow-rose-500/30',
      labelBg: 'bg-rose-500/20 text-rose-300 border-rose-500/50',
      icon: ShieldAlert,
      title: 'High Risk Scam',
      desc: 'Severe threats or fraudulent signals identified'
    };
  } else if (score >= 30 || classification === 'Suspicious') {
    theme = {
      color: 'text-amber-400',
      stroke: '#f59e0b',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
      glow: 'shadow-amber-500/20',
      labelBg: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      icon: AlertTriangle,
      title: 'Suspicious',
      desc: 'Moderate risk indicators or aggressive marketing'
    };
  }

  const IconComponent = theme.icon;

  // Arc calculation for SVG circular gauge
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  // Use a 270 degree arc
  const arcLength = circumference * 0.75;
  const strokeDashoffset = arcLength - (arcLength * Math.min(Math.max(score, 0), 100)) / 100;

  return (
    <div className={`p-6 rounded-2xl ${theme.bgColor} border ${theme.borderColor} shadow-xl ${theme.glow} flex flex-col items-center text-center relative overflow-hidden transition-all duration-300`}>
      {/* Background subtle radial gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />

      {/* Header Pill */}
      <div className="flex items-center space-x-2 mb-3">
        <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${theme.labelBg}`}>
          <IconComponent className="w-3.5 h-3.5" />
          <span>{theme.title}</span>
        </span>
        <span className="text-xs text-slate-400 font-mono">
          Conf: {Math.round(confidence * 100)}%
        </span>
      </div>

      {/* Circular SVG Gauge */}
      <div className="relative w-44 h-44 my-2 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-135" viewBox="0 0 160 160">
          {/* Background Track Arc */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="transparent"
            stroke="#1e293b"
            strokeWidth="14"
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeLinecap="round"
          />
          {/* Value Progress Arc */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="transparent"
            stroke={theme.stroke}
            strokeWidth="14"
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Inner Content Display */}
        <div className="absolute flex flex-col items-center justify-center">
          <div className="flex items-baseline">
            <span className={`text-5xl font-black tracking-tight ${theme.color}`}>
              {Math.round(score)}
            </span>
            <span className="text-sm font-semibold text-slate-400 ml-0.5">/100</span>
          </div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mt-1">
            Threat Score
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="text-xs text-slate-300 max-w-xs mt-1">
        {theme.desc}
      </p>

      {/* Score Tier Scale Visualizer */}
      <div className="w-full mt-4 pt-3 border-t border-slate-700/50 flex items-center justify-between text-[11px] font-medium text-slate-400">
        <div className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>0-29 Safe</span>
        </div>
        <div className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-amber-500" />
          <span>30-64 Warning</span>
        </div>
        <div className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-rose-500" />
          <span>65+ Scam</span>
        </div>
      </div>
    </div>
  );
}
