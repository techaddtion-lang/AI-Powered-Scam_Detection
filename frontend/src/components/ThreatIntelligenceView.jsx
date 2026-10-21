import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  PhoneCall, 
  Globe, 
  PlusCircle, 
  Search, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Database 
} from 'lucide-react';
import apiService from '../services/api';

export default function ThreatIntelligenceView() {
  const [intel, setIntel] = useState({ phones: [], domains: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('phones');
  const [search, setSearch] = useState('');
  const [showReportModal, setShowReportModal] = useState(false);

  // Report Form State
  const [reportType, setReportType] = useState('phone');
  const [identifier, setIdentifier] = useState('');
  const [entityName, setEntityName] = useState('');
  const [category, setCategory] = useState('Bank Vishing');
  const [notes, setNotes] = useState('');
  const [reportStatus, setReportStatus] = useState(null);

  const fetchThreatData = async () => {
    setLoading(true);
    try {
      const data = await apiService.getThreatBlacklist();
      setIntel(data);
    } catch (err) {
      console.error('Error fetching MySQL threat intel:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchThreatData();
  }, []);

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    if (!identifier.trim() || !entityName.trim()) return;

    try {
      await apiService.reportThreat({
        threat_type: reportType,
        identifier: identifier.trim(),
        entity_name: entityName.trim(),
        category,
        notes: notes.trim() || 'Reported via SOC Dashboard'
      });
      setReportStatus({ success: true, message: 'Threat successfully saved to MySQL blacklist registry!' });
      setIdentifier('');
      setEntityName('');
      setNotes('');
      fetchThreatData();
      setTimeout(() => setShowReportModal(false), 1500);
    } catch (err) {
      setReportStatus({ success: false, message: 'Failed to record threat in MySQL.' });
    }
  };

  const filteredPhones = (intel.phones || []).filter(p => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return p.phone_number.toLowerCase().includes(q) || p.entity_name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q);
  });

  const filteredDomains = (intel.domains || []).filter(d => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return d.domain_name.toLowerCase().includes(q) || (d.targeted_brand && d.targeted_brand.toLowerCase().includes(q));
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-7 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center space-x-1">
                <Database className="w-3 h-3 text-cyan-400" />
                <span>MySQL Threat Intelligence Registry</span>
              </span>
            </div>
            <h2 className="text-xl font-extrabold text-white tracking-tight mt-1">
              Blacklisted Callers & Phishing Domains
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Live threat database storing verified malicious numbers and domains. Incoming scans are automatically cross-referenced against this registry.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowReportModal(true)}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 text-white text-xs font-bold shadow-lg shadow-rose-600/25 flex items-center space-x-1.5 transition-all cursor-pointer"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Report New Threat</span>
            </button>

            <button
              onClick={fetchThreatData}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors cursor-pointer"
              title="Refresh from MySQL"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Toggle between Phones and Domains */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('phones')}
              className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-2 transition-all cursor-pointer ${
                activeTab === 'phones'
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <PhoneCall className="w-3.5 h-3.5" />
              <span>Blacklisted Numbers ({intel.phones?.length || 0})</span>
            </button>

            <button
              onClick={() => setActiveTab('domains')}
              className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-2 transition-all cursor-pointer ${
                activeTab === 'domains'
                  ? 'bg-purple-500 text-white shadow-md shadow-purple-500/20'
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
              <span>Phishing Domains ({intel.domains?.length || 0})</span>
            </button>
          </div>

          <div className="relative w-full sm:w-72">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter threats..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2" />
          </div>
        </div>
      </div>

      {/* Table: Phones */}
      {activeTab === 'phones' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Caller Number</th>
                  <th className="py-3 px-4">Impostor / Entity Identity</th>
                  <th className="py-3 px-4">Threat Category</th>
                  <th className="py-3 px-4">Reports Logged</th>
                  <th className="py-3 px-4">Risk Severity</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filteredPhones.map((phone) => {
                  const isBlacklist = phone.status === 'BLACKLISTED_SCAM';
                  const isOfficial = phone.status === 'VERIFIED_OFFICIAL';

                  return (
                    <tr key={phone.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-bold text-white whitespace-nowrap">
                        {phone.phone_number}
                      </td>
                      <td className="py-3 px-4 text-slate-200 font-sans whitespace-nowrap">
                        {phone.entity_name}
                      </td>
                      <td className="py-3 px-4 text-cyan-300 font-sans whitespace-nowrap">
                        {phone.category}
                      </td>
                      <td className="py-3 px-4 text-slate-300">
                        {phone.reports_count} reports
                      </td>
                      <td className="py-3 px-4 font-bold">
                        <span className={isBlacklist ? 'text-rose-400' : isOfficial ? 'text-emerald-400' : 'text-amber-400'}>
                          {phone.risk_score}%
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                            isBlacklist
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                              : isOfficial
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          }`}
                        >
                          {phone.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Table: Domains */}
      {activeTab === 'domains' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Domain / IP Host</th>
                  <th className="py-3 px-4">Threat Type</th>
                  <th className="py-3 px-4">Targeted Brand</th>
                  <th className="py-3 px-4">Incident Reports</th>
                  <th className="py-3 px-4">Risk Level</th>
                  <th className="py-3 px-4">Threat Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filteredDomains.map((dom) => {
                  const isMalicious = dom.status === 'ACTIVE_THREAT';
                  return (
                    <tr key={dom.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-bold text-white whitespace-nowrap">
                        {dom.domain_name}
                      </td>
                      <td className="py-3 px-4 text-purple-300 whitespace-nowrap">
                        {dom.threat_type}
                      </td>
                      <td className="py-3 px-4 text-slate-200 font-sans whitespace-nowrap">
                        {dom.targeted_brand || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-slate-300">
                        {dom.reports_count} reports
                      </td>
                      <td className="py-3 px-4 font-bold text-rose-400">
                        {dom.risk_score}%
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                            isMalicious
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                              : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          }`}
                        >
                          {dom.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Report Threat Modal */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                <span>Report Threat to MySQL Intelligence</span>
              </h3>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-slate-400 hover:text-white font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleReportSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Threat Type</label>
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200"
                  >
                    <option value="phone">Scam Phone Number</option>
                    <option value="domain">Phishing Domain / URL</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200"
                  >
                    <option value="Bank Vishing">Bank Fraud / Vishing</option>
                    <option value="IRS Extortion">IRS / Government Extortion</option>
                    <option value="Package Phishing">Package / Customs Smishing</option>
                    <option value="Tech Support">Tech Support Scareware</option>
                    <option value="Crypto Scam">Crypto / Job Scam</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">
                  {reportType === 'phone' ? 'Phone Number or Caller ID' : 'Domain Name / URL'}
                </label>
                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder={reportType === 'phone' ? '+1 (800) 555-0199' : 'chase-security-fake.net'}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-100 font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">
                  Impersonated Brand or Scam Title
                </label>
                <input
                  type="text"
                  required
                  value={entityName}
                  onChange={(e) => setEntityName(e.target.value)}
                  placeholder="e.g. Fake Wells Fargo Security Team"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-100"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Incident Notes (Optional)</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Details of the interaction, audio transcription snippet, etc."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono"
                />
              </div>

              {reportStatus && (
                <div className={`p-3 rounded-xl border flex items-center space-x-2 text-xs ${reportStatus.success ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800' : 'bg-rose-950/40 text-rose-300 border-rose-800'}`}>
                  {reportStatus.success ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
                  <span>{reportStatus.message}</span>
                </div>
              )}

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 text-white text-xs font-bold shadow-lg shadow-rose-600/25 cursor-pointer"
                >
                  Save to MySQL Blacklist
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
