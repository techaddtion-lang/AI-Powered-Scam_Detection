import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Database, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  RefreshCw, 
  Eye, 
  Filter, 
  Search, 
  Clock, 
  ArrowUpRight 
} from 'lucide-react';
import apiService from '../services/api';

export default function AnalyticsDashboard({ onInspectScan }) {
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterClass, setFilterClass] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedScan, setSelectedScan] = useState(null);

  const fetchMySQLData = async () => {
    setLoading(true);
    try {
      const [overview, scanLogs] = await Promise.all([
        apiService.getAnalyticsOverview(),
        apiService.getScanHistory(50)
      ]);
      setAnalytics(overview);
      setHistory(scanLogs);
    } catch (err) {
      console.error('Error fetching MySQL analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMySQLData();
  }, []);

  const filteredHistory = history.filter((item) => {
    if (filterClass !== 'ALL' && item.classification !== filterClass) {
      return false;
    }
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const content = (item.raw_content || '').toLowerCase();
      const sender = (item.sender_or_caller || '').toLowerCase();
      return content.includes(query) || sender.includes(query);
    }
    return true;
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Banner with MySQL Database Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1">
              <Database className="w-3 h-3 text-emerald-400" />
              <span>MySQL 8.0 Live Telemetry</span>
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Database: <code className="text-cyan-400 font-bold">scamshield_db</code>
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-white tracking-tight">
            Enterprise Threat Operations Center & Audit Log
          </h2>
          <p className="text-xs text-slate-400">
            Real-time query metrics aggregated from persistent MySQL database tables (scan_logs, phone_reputation, domain_blacklist).
          </p>
        </div>

        <button
          onClick={fetchMySQLData}
          disabled={loading}
          className="self-start sm:self-center px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center space-x-2 transition-colors cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Sync from MySQL</span>
        </button>
      </div>

      {/* KPI Metric Cards */}
      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md">
            <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider block">
              Total Scans
            </span>
            <span className="text-2xl font-black text-white mt-1 block">
              {analytics.total_scans}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">in scan_logs</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-rose-900/40 shadow-md">
            <span className="text-[10px] font-bold uppercase text-rose-400 tracking-wider block">
              Scams Blocked
            </span>
            <span className="text-2xl font-black text-rose-400 mt-1 block">
              {analytics.scams_blocked}
            </span>
            <span className="text-[10px] text-rose-400/70 font-semibold">
              {analytics.total_scans > 0 ? Math.round((analytics.scams_blocked / analytics.total_scans) * 100) : 0}% of traffic
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-amber-900/40 shadow-md">
            <span className="text-[10px] font-bold uppercase text-amber-400 tracking-wider block">
              Suspicious
            </span>
            <span className="text-2xl font-black text-amber-400 mt-1 block">
              {analytics.suspicious_flagged}
            </span>
            <span className="text-[10px] text-amber-400/70 font-semibold">Flagged for review</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-900/40 shadow-md">
            <span className="text-[10px] font-bold uppercase text-emerald-400 tracking-wider block">
              Safe Verified
            </span>
            <span className="text-2xl font-black text-emerald-400 mt-1 block">
              {analytics.safe_verified}
            </span>
            <span className="text-[10px] text-emerald-400/70 font-semibold">Legitimate</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-900/40 shadow-md">
            <span className="text-[10px] font-bold uppercase text-cyan-400 tracking-wider block">
              Blacklisted Callers
            </span>
            <span className="text-2xl font-black text-cyan-400 mt-1 block">
              {analytics.threat_intel?.blacklisted_callers_count || 0}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">in phone_reputation</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-purple-900/40 shadow-md">
            <span className="text-[10px] font-bold uppercase text-purple-400 tracking-wider block">
              Phishing Domains
            </span>
            <span className="text-2xl font-black text-purple-400 mt-1 block">
              {analytics.threat_intel?.phishing_domains_count || 0}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">in domain_blacklist</span>
          </div>
        </div>
      )}

      {/* Real MySQL Scan Audit Log */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center space-x-2">
              <span>MySQL Live Audit Trail (scan_logs table)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Every message, phone call transcript, and URL evaluated by the system is persisted here with timestamps and indicators.
            </p>
          </div>

          {/* Classification Filters */}
          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 sm:pb-0">
            {['ALL', 'High Risk Scam', 'Suspicious', 'Safe'].map((label) => (
              <button
                key={label}
                onClick={() => setFilterClass(label)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                  filterClass === label
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                    : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
                }`}
              >
                {label === 'ALL' ? 'All Logs' : label}
              </button>
            ))}
          </div>
        </div>

        {/* Search bar */}
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search audit trail by phone number, message text, or sender ID..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
        </div>

        {/* Table View */}
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Status / Risk</th>
                <th className="py-3 px-4">Channel & Sender</th>
                <th className="py-3 px-4">Content Preview</th>
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredHistory.length > 0 ? (
                filteredHistory.map((item) => {
                  const isScam = item.classification === 'High Risk Scam';
                  const isSuspicious = item.classification === 'Suspicious';

                  return (
                    <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                      {/* Classification Badge & Score */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                              isScam
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : isSuspicious
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            }`}
                          >
                            {item.classification}
                          </span>
                          <span className="font-bold text-slate-200">
                            {Math.round(item.risk_score)}%
                          </span>
                        </div>
                      </td>

                      {/* Channel & Sender */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="text-cyan-400 block font-semibold">
                          {item.sender_or_caller || 'Unknown'}
                        </span>
                        <span className="text-[10px] text-slate-500 uppercase">
                          {item.channel || item.scan_type}
                        </span>
                      </td>

                      {/* Preview Content */}
                      <td className="py-3 px-4 max-w-xs sm:max-w-md truncate font-sans text-slate-300">
                        "{item.raw_content}"
                      </td>

                      {/* Created At */}
                      <td className="py-3 px-4 text-[11px] text-slate-400 whitespace-nowrap">
                        {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                      </td>

                      {/* Action */}
                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <button
                          onClick={() => setSelectedScan(item)}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-sans font-medium flex items-center space-x-1 ml-auto cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Inspect</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500 font-sans">
                    No matching audit records found in MySQL database.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal for detailed inspection of an audit record */}
      {selectedScan && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
                  Audit Incident Details
                </span>
                <h3 className="text-base font-bold text-white font-mono">
                  ID: {selectedScan.id}
                </h3>
              </div>
              <button
                onClick={() => setSelectedScan(null)}
                className="text-slate-400 hover:text-white text-sm font-bold px-2 py-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[10px]">Classification:</span>
                  <span className="font-bold text-rose-400">{selectedScan.classification}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Risk Score:</span>
                  <span className="font-bold text-white">{selectedScan.risk_score} / 100</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Channel / Sender:</span>
                  <span className="font-bold text-cyan-400">{selectedScan.sender_or_caller || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Logged At:</span>
                  <span className="font-mono text-slate-300">{selectedScan.created_at}</span>
                </div>
              </div>

              <div>
                <span className="text-slate-400 block font-semibold mb-1">Full Content:</span>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-slate-200 text-xs whitespace-pre-wrap">
                  {selectedScan.raw_content}
                </div>
              </div>

              <div>
                <span className="text-slate-400 block font-semibold mb-1">Verdict Summary:</span>
                <p className="text-slate-200 leading-relaxed">{selectedScan.summary}</p>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedScan(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer"
              >
                Close Audit Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
