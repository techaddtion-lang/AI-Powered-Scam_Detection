import React from 'react';
import { ExternalLink, Globe, AlertTriangle, ShieldCheck, Server, AlertCircle } from 'lucide-react';

export default function UrlResultsCard({ urls = [] }) {
  if (!urls || urls.length === 0) return null;

  return (
    <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white tracking-tight">
            Extracted Links Security Inspection ({urls.length})
          </h3>
        </div>
      </div>

      <div className="space-y-3">
        {urls.map((item, idx) => {
          const isHighRisk = item.risk_score >= 60;
          const isSuspicious = item.risk_score >= 35;

          return (
            <div
              key={idx}
              className={`p-3.5 rounded-lg border text-xs space-y-2 ${
                isHighRisk
                  ? 'bg-rose-950/30 border-rose-800/40'
                  : isSuspicious
                  ? 'bg-amber-950/30 border-amber-800/40'
                  : 'bg-slate-800/40 border-slate-700/60'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="space-y-0.5 overflow-hidden">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-white truncate max-w-xs sm:max-w-md font-mono text-[11px]">
                      {item.url}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                    <span>Domain: <strong className="text-slate-300">{item.domain}</strong></span>
                    {item.tld && (
                      <span>TLD: <code className="text-cyan-300 font-mono">.{item.tld}</code></span>
                    )}
                  </div>
                </div>

                <div className="flex flex-col items-end shrink-0">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      isHighRisk
                        ? 'bg-rose-500 text-white'
                        : isSuspicious
                        ? 'bg-amber-500 text-slate-950'
                        : 'bg-emerald-500 text-white'
                    }`}
                  >
                    Risk: {Math.round(item.risk_score)}%
                  </span>
                </div>
              </div>

              {/* Badges / flags */}
              <div className="flex flex-wrap gap-1.5 pt-1">
                {item.has_ip_hostname && (
                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] font-medium">
                    <Server className="w-3 h-3" />
                    <span>Raw IP Hostname</span>
                  </span>
                )}

                {item.is_shortener && (
                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-medium">
                    <AlertTriangle className="w-3 h-3" />
                    <span>URL Shortener Mask</span>
                  </span>
                )}

                {item.targeted_brand && (
                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] font-medium">
                    <AlertCircle className="w-3 h-3" />
                    <span>Impersonates {item.targeted_brand.toUpperCase()}</span>
                  </span>
                )}
              </div>

              {/* Reasons list */}
              {item.reasons && item.reasons.length > 0 && (
                <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px] pt-1">
                  {item.reasons.map((r, rIdx) => (
                    <li key={rIdx}>{r}</li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
