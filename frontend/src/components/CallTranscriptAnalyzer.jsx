import React, { useState } from 'react';
import { 
  PhoneCall, 
  Trash2, 
  AlertCircle, 
  ShieldAlert, 
  CheckCircle, 
  Radio, 
  Sliders, 
  ChevronDown, 
  ChevronUp, 
  Volume2 
} from 'lucide-react';
import RiskGauge from './RiskGauge';
import IndicatorBadge from './IndicatorBadge';
import RecommendationsList from './RecommendationsList';
import SampleSelector from './SampleSelector';
import apiService from '../services/api';

export default function CallTranscriptAnalyzer({ samples = [], onAnalysisComplete }) {
  const [transcript, setTranscript] = useState('');
  const [callerNumber, setCallerNumber] = useState('');
  const [duration, setDuration] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  const handleSelectSample = (sample) => {
    setTranscript(sample.content);
    setCallerNumber(sample.sender_or_caller || '');
    setError(null);
  };

  const handleClear = () => {
    setTranscript('');
    setCallerNumber('');
    setDuration('');
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async (e) => {
    if (e) e.preventDefault();
    if (!transcript.trim()) {
      setError('Please provide a phone call transcript or select a preset.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await apiService.analyzeCall(
        transcript,
        callerNumber || null,
        duration ? parseInt(duration, 10) : null
      );
      setResult(data);
      if (onAnalysisComplete) {
        onAnalysisComplete({ type: 'call', data });
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to analyze call transcript.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Call Input Section */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
              <PhoneCall className="w-5 h-5 text-indigo-400" />
              <span>Voice Call & Audio Transcript (Vishing) Analyzer</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Analyze audio transcripts from robocalls, bank impostors, IRS extortionists, and family emergency voice clones.
            </p>
          </div>
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-indigo-950/40 text-indigo-300 border border-indigo-800/40 text-xs font-mono">
            <Radio className="w-3.5 h-3.5 animate-pulse text-indigo-400" />
            <span>Vishing Engine</span>
          </div>
        </div>

        {/* Quick Test Presets for Calls */}
        <SampleSelector
          samples={samples}
          onSelectSample={handleSelectSample}
          activeType="call"
        />

        {/* Input Form */}
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Caller Phone Number / Caller ID (Optional)
              </label>
              <input
                type="text"
                value={callerNumber}
                onChange={(e) => setCallerNumber(e.target.value)}
                placeholder="e.g. +1 (800) 555-0199 or Unknown"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Call Duration (seconds, optional)
              </label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                placeholder="e.g. 120"
                min="0"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Call Transcript / Audio Speech-to-Text <span className="text-rose-400">*</span>
            </label>
            <textarea
              rows={5}
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste what the caller said... (e.g. 'This is Officer James from the IRS Department. There is an arrest warrant against your Social Security Number...')"
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors font-mono resize-y"
            />
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={handleClear}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors flex items-center space-x-1.5 cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 hover:from-indigo-500 hover:to-pink-400 text-white shadow-lg shadow-purple-500/25 transition-all flex items-center space-x-2 disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Scanning Voice Transcript...</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-3.5 h-3.5" />
                  <span>Analyze Call Transcript</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-2xl space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs uppercase font-bold text-indigo-400 tracking-wider">
                Vishing Threat Report
              </span>
              <h3 className="text-lg font-bold text-white tracking-tight">
                Phone Call Behavioral & Linguistic Analysis
              </h3>
            </div>
            {result.caller_number && (
              <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Caller: {result.caller_number}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            <div className="lg:col-span-1">
              <RiskGauge
                score={result.risk_score}
                classification={result.classification}
                confidence={result.confidence}
              />
            </div>

            <div className="lg:col-span-2 space-y-4">
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Call Verdict Summary
                </span>
                <p className="text-sm font-medium text-slate-200 leading-relaxed">
                  {result.summary}
                </p>

                {/* MySQL Analyst Feedback Actions */}
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between flex-wrap gap-2 text-xs">
                  <span className="text-slate-400 font-mono text-[11px]">
                    Saved to MySQL <strong className="text-indigo-400">scan_logs</strong>
                  </span>
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={async () => {
                        await apiService.submitFeedback(result.id, 'CONFIRMED_SCAM');
                        alert('Vishing incident confirmed & logged to MySQL user_feedback.');
                      }}
                      className="px-2.5 py-1 rounded bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/50 text-[11px] font-semibold transition-colors cursor-pointer"
                    >
                      Confirm Vishing Scam
                    </button>
                    <button
                      type="button"
                      onClick={async () => {
                        await apiService.submitFeedback(result.id, 'FALSE_POSITIVE');
                        alert('Logged as benign to MySQL user_feedback.');
                      }}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] font-semibold transition-colors cursor-pointer"
                    >
                      Flag False Alarm
                    </button>
                  </div>
                </div>
              </div>

              {/* Vishing Specific Tactics Flagged */}
              {result.vishing_tactics_detected && result.vishing_tactics_detected.length > 0 && (
                <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/40 space-y-2">
                  <span className="text-xs font-bold text-rose-300 flex items-center space-x-1.5">
                    <ShieldAlert className="w-4 h-4 text-rose-400" />
                    <span>Specialized Vishing Social Engineering Vectors</span>
                  </span>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {result.vishing_tactics_detected.map((tactic, tIdx) => (
                      <span
                        key={tIdx}
                        className="px-2.5 py-1 rounded-md bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold"
                      >
                        {tactic}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <RecommendationsList
                recommendations={result.recommendations}
                isScam={result.classification === 'High Risk Scam'}
              />
            </div>
          </div>

          {/* Detected Indicators */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white tracking-tight">
              Detected Acoustic & Coercion Indicators ({result.indicators?.length || 0})
            </h4>

            {result.indicators && result.indicators.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.indicators.map((ind, idx) => (
                  <IndicatorBadge key={idx} indicator={ind} />
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-400 flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>No voice coercion or vishing vectors detected in transcript.</span>
              </div>
            )}
          </div>

          {/* Technical ML Details */}
          <div className="border-t border-slate-800 pt-3">
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="flex items-center justify-between w-full text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors py-1 cursor-pointer"
            >
              <div className="flex items-center space-x-1.5">
                <Sliders className="w-3.5 h-3.5 text-indigo-400" />
                <span>NLP Model Probability Metrics</span>
              </div>
              {showTechnicalDetails ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {showTechnicalDetails && (
              <div className="mt-3 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3 text-xs font-mono">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Safe Prob:</span>
                    <span className="text-emerald-400 font-bold text-sm">
                      {(result.ml_confidence_scores?.['Safe'] * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Suspicious Prob:</span>
                    <span className="text-amber-400 font-bold text-sm">
                      {(result.ml_confidence_scores?.['Suspicious'] * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">High Scam Prob:</span>
                    <span className="text-rose-400 font-bold text-sm">
                      {(result.ml_confidence_scores?.['High Risk Scam'] * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
