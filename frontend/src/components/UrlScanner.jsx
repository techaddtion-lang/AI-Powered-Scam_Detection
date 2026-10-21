import React, { useState } from 'react';
import { Globe, Search, Trash2, AlertCircle, ShieldAlert, CheckCircle, ShieldCheck } from 'lucide-react';
import apiService from '../services/api';

export default function UrlScanner() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const sampleUrls = [
    'http://192.168.1.120/chase/verify.php',
    'http://usps-tracking-redelivery.buzz/claim',
    'http://bit.ly/paypal-security-update',
    'https://www.amazon.com/orders',
    'http://apple-security-support.top/unlock'
  ];

  const handleScan = async (e) => {
    if (e) e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a URL or web domain to analyze.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await apiService.analyzeUrl(url);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to inspect URL.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-xl space-y-5">
        <div className="border-b border-slate-800 pb-4">
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
            <Globe className="w-5 h-5 text-cyan-400" />
            <span>Standalone URL & Phishing Link Scanner</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Test any link from suspicious SMS or emails to inspect domain age, IP masking, brand spoofing, and sneaky redirects.
          </p>
        </div>

        {/* Quick sample chips */}
        <div className="space-y-1.5">
          <span className="text-xs font-semibold text-slate-300">Test quick examples:</span>
          <div className="flex flex-wrap gap-2">
            {sampleUrls.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setUrl(sample);
                  setError(null);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-mono transition-colors cursor-pointer"
              >
                {sample}
              </button>
            ))}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleScan} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              URL or Domain Name
            </label>
            <div className="relative">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="e.g. http://bofa-kyc-update.xyz/login or http://192.168.1.120/auth"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-3.5 pr-10 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
              />
              {url && (
                <button
                  type="button"
                  onClick={() => {
                    setUrl('');
                    setResult(null);
                  }}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-white"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex justify-end pt-1">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 transition-all flex items-center space-x-2 disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Inspecting URL Heuristics...</span>
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5" />
                  <span>Scan Link Safety</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Result Card */}
      {result && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-2xl space-y-5 animate-fade-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs uppercase font-bold text-cyan-400 tracking-wider">
                URL Safety Diagnostic
              </span>
              <h3 className="text-lg font-bold text-white tracking-tight font-mono truncate max-w-lg">
                {result.url}
              </h3>
            </div>

            <span
              className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider ${
                result.is_suspicious
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}
            >
              {result.is_suspicious ? 'Malicious / Suspicious' : 'Clean / Low Risk'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-medium">Domain & Host:</span>
              <span className="text-sm font-bold text-white font-mono">{result.domain || 'N/A'}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-medium">Top Level Domain (TLD):</span>
              <span className="text-sm font-bold text-cyan-400 font-mono">
                {result.tld ? `.${result.tld}` : 'Standard'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-medium">Link Risk Score:</span>
              <span
                className={`text-lg font-black ${
                  result.risk_score >= 60
                    ? 'text-rose-400'
                    : result.risk_score >= 35
                    ? 'text-amber-400'
                    : 'text-emerald-400'
                }`}
              >
                {result.risk_score} / 100
              </span>
            </div>
          </div>

          {/* Reasons */}
          {result.reasons && result.reasons.length > 0 ? (
            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-800/40 space-y-2">
              <span className="text-xs font-bold text-rose-300 flex items-center space-x-1.5">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                <span>Identified Threat Factors</span>
              </span>
              <ul className="list-disc list-inside space-y-1.5 text-xs text-slate-200">
                {result.reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/30 text-xs text-emerald-300 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>No known malicious phishing indicators, deceptive TLDs, or IP hosts detected.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
