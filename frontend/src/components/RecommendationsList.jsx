import React from 'react';
import { CheckCircle2, ShieldCheck, AlertOctagon } from 'lucide-react';

export default function RecommendationsList({ recommendations = [], isScam = false }) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
      <div className="flex items-center space-x-2">
        {isScam ? (
          <AlertOctagon className="w-4 h-4 text-rose-400" />
        ) : (
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        )}
        <h3 className="text-sm font-bold text-white tracking-tight">
          Recommended Safety Actions
        </h3>
      </div>

      <ul className="space-y-2">
        {recommendations.map((rec, index) => (
          <li key={index} className="flex items-start space-x-2.5 text-xs text-slate-300 leading-relaxed">
            <CheckCircle2 className={`w-4 h-4 mt-0.5 shrink-0 ${isScam ? 'text-rose-400' : 'text-cyan-400'}`} />
            <span>{rec}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
