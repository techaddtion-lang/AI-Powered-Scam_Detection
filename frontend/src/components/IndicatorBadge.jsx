import React from 'react';
import { 
  AlertCircle, 
  Flame, 
  Lock, 
  DollarSign, 
  Link2, 
  Headphones, 
  Scale, 
  Gift, 
  Truck, 
  Info 
} from 'lucide-react';

const CATEGORY_ICONS = {
  "Urgency & Intimidation": Flame,
  "Financial Bait / Crypto / Wire": DollarSign,
  "Credential & OTP Theft": Lock,
  "Brand & Authority Impersonation": AlertCircle,
  "Malicious / Phishing URL": Link2,
  "Tech Support / Remote Access": Headphones,
  "Legal & Law Enforcement Threat": Scale,
  "Lottery / Prize / Job Scam": Gift,
  "Delivery / Package Phishing": Truck,
  "General Anomaly": Info
};

const SEVERITY_STYLES = {
  critical: {
    bg: 'bg-rose-950/60 text-rose-200 border-rose-500/40',
    badge: 'bg-rose-500 text-white',
    dot: 'bg-rose-400'
  },
  high: {
    bg: 'bg-orange-950/50 text-orange-200 border-orange-500/40',
    badge: 'bg-orange-500 text-white',
    dot: 'bg-orange-400'
  },
  medium: {
    bg: 'bg-amber-950/40 text-amber-200 border-amber-500/30',
    badge: 'bg-amber-500/80 text-white',
    dot: 'bg-amber-400'
  },
  low: {
    bg: 'bg-slate-800/60 text-slate-200 border-slate-700',
    badge: 'bg-slate-600 text-white',
    dot: 'bg-slate-400'
  }
};

export default function IndicatorBadge({ indicator }) {
  const { title, description, category, severity, matched_text } = indicator;
  const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.medium;
  const IconComponent = CATEGORY_ICONS[category] || AlertCircle;

  return (
    <div className={`p-3.5 rounded-xl border ${style.bg} flex flex-col space-y-2 transition-all`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-black/30">
            <IconComponent className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white tracking-tight">{title}</h4>
            <span className="text-[11px] text-slate-400 block font-medium">{category}</span>
          </div>
        </div>

        {/* Severity Pill */}
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${style.badge}`}>
          {severity}
        </span>
      </div>

      <p className="text-xs text-slate-300 leading-relaxed">
        {description}
      </p>

      {/* Matched pattern trigger highlight */}
      {matched_text && (
        <div className="pt-1 flex items-center space-x-1.5 text-[11px]">
          <span className="text-slate-400 font-medium">Trigger text:</span>
          <code className="px-2 py-0.5 rounded bg-black/40 border border-white/10 text-rose-300 font-mono text-[11px]">
            "{matched_text}"
          </code>
        </div>
      )}
    </div>
  );
}
