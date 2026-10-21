import React from 'react';
import { Sparkles, PhoneCall, MessageSquare, AlertTriangle, ShieldCheck, Flame } from 'lucide-react';

export default function SampleSelector({ samples = [], onSelectSample, activeType = 'sms' }) {
  if (!samples || samples.length === 0) return null;

  // Filter samples relevant to the active tab type
  const relevantSamples = samples.filter((s) => s.type === activeType);
  if (relevantSamples.length === 0) return null;

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Quick Test Presets (Click to load):</span>
        </div>
        <span className="text-[11px] text-slate-500">
          Realistic test vectors
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {relevantSamples.map((sample) => {
          const isScam = sample.expected_classification === 'High Risk Scam';
          const isSuspicious = sample.expected_classification === 'Suspicious';

          let badgeColor = 'bg-slate-800 text-slate-300 hover:bg-slate-700/80 border-slate-700';
          if (isScam) {
            badgeColor = 'bg-rose-950/40 text-rose-300 hover:bg-rose-900/50 border-rose-800/40';
          } else if (isSuspicious) {
            badgeColor = 'bg-amber-950/40 text-amber-300 hover:bg-amber-900/50 border-amber-800/40';
          } else {
            badgeColor = 'bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/50 border-emerald-800/40';
          }

          return (
            <button
              key={sample.id}
              onClick={() => onSelectSample(sample)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all text-left flex items-center space-x-2 cursor-pointer ${badgeColor}`}
              title={sample.description}
            >
              {sample.type === 'call' ? (
                <PhoneCall className="w-3 h-3 shrink-0" />
              ) : (
                <MessageSquare className="w-3 h-3 shrink-0" />
              )}
              <span className="truncate max-w-[200px] sm:max-w-[280px]">
                {sample.title}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
