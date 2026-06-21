"use client";

import React, { useEffect, useState } from 'react';
import { HelpCircle, Rocket, Hourglass, Loader2, Globe, TrendingUp, RefreshCw } from 'lucide-react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { fetchCitations, type Citation } from '@/lib/api';

export default function CitationsPage() {
  const { currentProjectId } = useWorkspaceStore();
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    const pid = currentProjectId || 'demo-project';
    try {
      setLoading(true);
      const data = await fetchCitations(pid);
      setCitations(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load citations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentProjectId]);

  // Calculations
  const totalCitations = citations.length;
  const totalMentions = citations.reduce((acc, curr) => acc + (typeof curr.mentions_count === 'number' ? curr.mentions_count : 0), 0);
  const totalGain = citations.reduce((acc, curr) => acc + (typeof curr.visibility_gain === 'number' ? curr.visibility_gain : 0), 0);

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-8 pb-4 border-b border-[#27272a]/40">
        <div>
          <h1 className="text-3xl font-medium tracking-tight">Citations</h1>
          <p className="text-sm text-[#a1a1aa] mt-1">Track external citations, source mentions, and their impact on your generative visibility</p>
        </div>
        <button 
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-[#18181b] border border-[#27272a] hover:bg-[#27272a] rounded-lg text-sm text-[#a1a1aa] hover:text-white transition-colors cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-sm text-red-400 font-medium mb-8">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
          <div className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-2 font-medium">Observed Citations</div>
          <div className="text-3xl font-semibold text-white">{totalCitations}</div>
          <div className="text-xs text-[#52525b] mt-1">Unique domains or resource links cited</div>
        </div>

        <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
          <div className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-2 font-medium">Total Mentions Count</div>
          <div className="text-3xl font-semibold text-sky-400">{totalMentions}</div>
          <div className="text-xs text-[#52525b] mt-1">Sum of citation links across all runs</div>
        </div>

        <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
          <div className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-2 font-medium">Aggregated Visibility Gain</div>
          <div className="text-3xl font-semibold text-emerald-400">+{totalGain.toFixed(2)}%</div>
          <div className="text-xs text-[#52525b] mt-1">Combined authority and position weight increase</div>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-[#09090b] border border-[#27272a] rounded-xl overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-[#27272a]/55 flex items-center justify-between">
          <div className="text-sm font-medium text-slate-300">Observation Results</div>
          <div className="text-xs text-[#52525b]">Based on active AI models</div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="w-8 h-8 rounded-full text-emerald-500 animate-spin" />
          </div>
        ) : citations.length === 0 ? (
          <div className="border border-dashed border-[#27272a]/80 rounded-2xl flex flex-col items-center justify-center p-16 bg-slate-900/10 backdrop-blur-sm text-center">
            <div className="w-12 h-12 rounded-full bg-sky-500/10 text-sky-400 flex items-center justify-center mb-4">
              <Globe className="w-6 h-6 animate-pulse" />
            </div>
            <h3 className="text-base font-semibold text-white mb-1">No Citations Observed</h3>
            <p className="text-sm text-[#a1a1aa] max-w-md mb-6 leading-relaxed">
              We haven't found any citations referencing your brand domain or resources yet. Try running prompts across different AI models.
            </p>
            <a
              href="/prompts"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#18181b] border border-[#27272a] hover:bg-[#27272a] hover:text-white text-[#a1a1aa] rounded-xl text-xs font-semibold tracking-wide transition-colors cursor-pointer"
            >
              Go to Prompts
            </a>
          </div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="bg-[#18181b]/35 text-[#a1a1aa] border-b border-[#27272a]">
              <tr>
                <th className="py-3.5 px-6 font-normal">Cited Resource Page</th>
                <th className="py-3.5 px-6 font-normal text-center w-36">Mentions Count</th>
                <th className="py-3.5 px-6 font-normal w-36">Est. Gain</th>
                <th className="py-3.5 px-6 font-normal w-40">Last Observed</th>
                <th className="py-3.5 px-6 font-normal w-32">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#27272a]/30">
              {citations.map((row, idx) => (
                <tr key={idx} className="hover:bg-[#18181b]/20 transition-colors">
                  <td className="py-4 px-6">
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 mt-0.5 rounded bg-emerald-500/10 text-emerald-400 text-xs font-bold flex items-center justify-center flex-shrink-0">
                        {idx + 1}
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="text-slate-200 font-medium truncate max-w-lg">{row.url}</span>
                        <a 
                          href={row.url} 
                          target="_blank" 
                          rel="noreferrer" 
                          className="text-[#a1a1aa] text-xs hover:underline truncate max-w-sm mt-0.5"
                        >
                          {row.url}
                        </a>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-6 text-center text-sky-400 font-semibold">
                    {row.mentions_count}
                  </td>
                  <td className="py-4 px-6 font-medium text-emerald-400">
                    +{row.visibility_gain}%
                  </td>
                  <td className="py-4 px-6 text-[#a1a1aa] text-xs">
                    {row.last_observed ? new Date(row.last_observed).toLocaleString() : 'N/A'}
                  </td>
                  <td className="py-4 px-6">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-medium ${
                      row.status === 'Effective' 
                        ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400' 
                        : 'border-amber-500/20 bg-amber-500/5 text-amber-400'
                    }`}>
                      {row.status === 'Effective' ? (
                        <Rocket className="w-3 h-3" />
                      ) : (
                        <Hourglass className="w-3 h-3" />
                      )}
                      <span>{row.status}</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

    </div>
  );
}
