import React from 'react';
import { History, ShieldAlert, ShieldCheck, AlertTriangle, ArrowRight, Trash2 } from 'lucide-react';

export default function AnalysisHistory({ history = [], onSelectHistoryItem, onClearHistory }) {
  if (!history || history.length === 0) {
    return (
      <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-3">
        <History className="w-8 h-8 text-slate-600 mx-auto" />
        <h3 className="text-sm font-semibold text-slate-300">No Analysis History Yet</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Analyze any SMS, message, or call transcript above. Your session findings will appear here for side-by-side comparison.
        </p>
      </div>
    );
  }

  // Calculate session summary stats
  const total = history.length;
  const scams = history.filter(h => h.data.classification === 'High Risk Scam').length;
  const suspicious = history.filter(h => h.data.classification === 'Suspicious').length;
  const safe = history.filter(h => h.data.classification === 'Safe').length;
  const avgScore = Math.round(history.reduce((acc, h) => acc + (h.data.risk_score || 0), 0) / total);

  return (
    <div className="space-y-6">
      {/* Metrics Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 block uppercase">Total Scanned</span>
          <span className="text-2xl font-black text-white">{total}</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-rose-400 block uppercase">Scams Caught</span>
          <span className="text-2xl font-black text-rose-400">{scams}</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-amber-400 block uppercase">Suspicious</span>
          <span className="text-2xl font-black text-amber-400">{suspicious}</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-cyan-400 block uppercase">Avg Threat Score</span>
          <span className="text-2xl font-black text-cyan-400">{avgScore}/100</span>
        </div>
      </div>

      {/* History Items List */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <History className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white tracking-tight">
              Session Activity Log ({total})
            </h3>
          </div>
          <button
            onClick={onClearHistory}
            className="text-xs text-slate-400 hover:text-rose-400 flex items-center space-x-1 transition-colors cursor-pointer"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear Log</span>
          </button>
        </div>

        <div className="space-y-2.5">
          {history.map((item, idx) => {
            const data = item.data;
            const isScam = data.classification === 'High Risk Scam';
            const isSuspicious = data.classification === 'Suspicious';

            return (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1 overflow-hidden">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        isScam
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                          : isSuspicious
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                          : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                      }`}
                    >
                      {data.classification}
                    </span>
                    <span className="text-slate-400 font-mono text-[10px]">
                      Type: {item.type.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-slate-200 line-clamp-1 font-mono text-[11px]">
                    "{data.input_text || data.transcript}"
                  </p>
                </div>

                <div className="flex items-center space-x-4 shrink-0">
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block">Score</span>
                    <span
                      className={`font-black text-sm ${
                        isScam ? 'text-rose-400' : isSuspicious ? 'text-amber-400' : 'text-emerald-400'
                      }`}
                    >
                      {Math.round(data.risk_score)}/100
                    </span>
                  </div>

                  {onSelectHistoryItem && (
                    <button
                      onClick={() => onSelectHistoryItem(item)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center space-x-1 cursor-pointer"
                    >
                      <span>View</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
