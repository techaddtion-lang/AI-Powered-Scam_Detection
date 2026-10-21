import React, { useState } from 'react';
import { 
  Send, 
  Trash2, 
  AlertCircle, 
  Sparkles, 
  CheckCircle, 
  Layers, 
  Sliders, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink 
} from 'lucide-react';
import RiskGauge from './RiskGauge';
import IndicatorBadge from './IndicatorBadge';
import RecommendationsList from './RecommendationsList';
import UrlResultsCard from './UrlResultsCard';
import SampleSelector from './SampleSelector';
import apiService from '../services/api';

export default function MessageAnalyzer({ samples = [], onAnalysisComplete }) {
  const [text, setText] = useState('');
  const [senderId, setSenderId] = useState('');
  const [channel, setChannel] = useState('sms');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  const handleSelectSample = (sample) => {
    setText(sample.content);
    setSenderId(sample.sender_or_caller || '');
    setError(null);
  };

  const handleClear = () => {
    setText('');
    setSenderId('');
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async (e) => {
    if (e) e.preventDefault();
    if (!text.trim()) {
      setError('Please enter a message or select a preset sample.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await apiService.analyzeMessage(text, senderId || null, channel);
      setResult(data);
      if (onAnalysisComplete) {
        onAnalysisComplete({ type: 'message', data });
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to analyze message. Ensure the FastAPI backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Input Section */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
              <span>Analyze Text, SMS or Email</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Paste suspicious messages to detect smishing, financial extortion, urgent traps, and credential theft.
            </p>
          </div>

          {/* Channel selector */}
          <div className="flex items-center space-x-2">
            <label className="text-xs text-slate-400 font-medium">Channel:</label>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="sms">SMS / Text</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="email">Email Body</option>
              <option value="telegram">Telegram</option>
              <option value="other">Other / Social Media</option>
            </select>
          </div>
        </div>

        {/* Quick Test Presets */}
        <SampleSelector
          samples={samples}
          onSelectSample={handleSelectSample}
          activeType="sms"
        />

        {/* Form Controls */}
        <form onSubmit={handleAnalyze} className="space-y-4">
          {/* Sender ID / Phone Number (Optional) */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Sender ID / Originating Phone / Email (Optional)
            </label>
            <input
              type="text"
              value={senderId}
              onChange={(e) => setSenderId(e.target.value)}
              placeholder="e.g. +1 (800) 242-7338 or support@chase-verify.com"
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          {/* Message Textarea */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Message Content <span className="text-rose-400">*</span>
            </label>
            <textarea
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste the SMS, WhatsApp message, or email body here... (e.g. 'URGENT: Chase Bank alert. Your debit card has been blocked...')"
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono resize-y"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Actions Bar */}
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
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-lg shadow-indigo-500/25 transition-all flex items-center space-x-2 disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Analyzing Threat Vector...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>Analyze Message</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Analysis Results Section */}
      {result && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-2xl space-y-6 animate-fade-in">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs uppercase font-bold text-cyan-400 tracking-wider">
                Analysis Report
              </span>
              <h3 className="text-lg font-bold text-white tracking-tight">
                Threat Classification & Risk Assessment
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              ID: {result.id?.slice(0, 8)}...
            </span>
          </div>

          {/* Main Top Overview Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Visual Risk Gauge */}
            <div className="lg:col-span-1">
              <RiskGauge
                score={result.risk_score}
                classification={result.classification}
                confidence={result.confidence}
              />
            </div>

            {/* Verdict Summary & Quick Actions */}
            <div className="lg:col-span-2 space-y-4">
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Executive Verdict
                </span>
                <p className="text-sm font-medium text-slate-200 leading-relaxed">
                  {result.summary}
                </p>

                {/* MySQL Analyst Feedback Actions */}
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between flex-wrap gap-2 text-xs">
                  <span className="text-slate-400 font-mono text-[11px]">
                    Logged to MySQL <strong className="text-cyan-400">scan_logs</strong>
                  </span>
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={async () => {
                        await apiService.submitFeedback(result.id, 'CONFIRMED_SCAM');
                        alert('Feedback saved to MySQL user_feedback table: Confirmed Threat.');
                      }}
                      className="px-2.5 py-1 rounded bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/50 text-[11px] font-semibold transition-colors cursor-pointer"
                    >
                      Confirm Scam Threat
                    </button>
                    <button
                      type="button"
                      onClick={async () => {
                        await apiService.submitFeedback(result.id, 'FALSE_POSITIVE');
                        alert('Feedback saved to MySQL user_feedback table: False Positive recorded.');
                      }}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] font-semibold transition-colors cursor-pointer"
                    >
                      Flag False Alarm
                    </button>
                  </div>
                </div>
              </div>

              {/* Safety Recommendations */}
              <RecommendationsList
                recommendations={result.recommendations}
                isScam={result.classification === 'High Risk Scam'}
              />
            </div>
          </div>

          {/* Extracted URLs Analysis */}
          {result.urls_analyzed && result.urls_analyzed.length > 0 && (
            <UrlResultsCard urls={result.urls_analyzed} />
          )}

          {/* Detected Threat Indicators */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
                <span>Detected Threat Indicators ({result.indicators?.length || 0})</span>
              </h4>
              <span className="text-xs text-slate-400">
                Identified via NLP Pattern Heuristics
              </span>
            </div>

            {result.indicators && result.indicators.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.indicators.map((ind, idx) => (
                  <IndicatorBadge key={idx} indicator={ind} />
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-400 flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>No hostile pressure keywords, malicious links, or credential extortion patterns detected.</span>
              </div>
            )}
          </div>

          {/* Category Breakdown Bar */}
          {result.category_breakdown && Object.keys(result.category_breakdown).length > 0 && (
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <span className="text-xs font-bold text-slate-300">
                Threat Vector Breakdown
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-1">
                {Object.entries(result.category_breakdown).map(([cat, val], idx) => (
                  <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 text-[11px]">
                    <span className="text-slate-400 block truncate">{cat}</span>
                    <span className="font-bold text-cyan-400 font-mono">+{val} pts</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Technical ML & Pipeline Details Toggle */}
          <div className="border-t border-slate-800 pt-3">
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="flex items-center justify-between w-full text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors py-1 cursor-pointer"
            >
              <div className="flex items-center space-x-1.5">
                <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                <span>Explainable AI & ML Pipeline Confidence Details</span>
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

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                  <span>Heuristic Rule Score: <strong className="text-slate-200">{result.rule_score}</strong>/100</span>
                  <span>Composite Blended Risk: <strong className="text-cyan-400">{result.risk_score}</strong>/100</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
