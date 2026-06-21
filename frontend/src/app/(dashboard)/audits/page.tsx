"use client";

import React, { useEffect, useState } from 'react';
import { getAudits } from '@/lib/api';
import { profoundColors } from '@/lib/design-tokens';

export default function AuditsPage() {
  const [audits, setAudits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAudits();
  }, []);

  const loadAudits = async () => {
    try {
      setLoading(true);
      const data = await getAudits();
      setAudits(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load audits');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      <div className="flex justify-between items-center mb-10">
        <h1 className="text-3xl font-medium tracking-tight">Your Audits</h1>
        <button onClick={loadAudits} className="px-4 py-2 bg-[#18181b] border border-[#27272a] rounded-md hover:bg-[#27272a] text-sm">
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <div className="w-8 h-8 rounded-full border-2 border-emerald-500/20 border-t-emerald-400 animate-spin"></div>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-sm text-red-400 font-medium">
          {error}
        </div>
      ) : audits.length === 0 ? (
        <div className="border border-dashed border-[#27272a]/80 rounded-2xl flex flex-col items-center justify-center p-12 bg-slate-900/10 backdrop-blur-sm text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-white mb-1">No Page Audits Yet</h3>
          <p className="text-sm text-[#a1a1aa] max-w-md mb-6 leading-relaxed">
            Submit a page URL in your workspace dashboard onboarding wizard to generate a visual heuristic audit report.
          </p>
          <a
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#18181b] border border-[#27272a] hover:bg-[#27272a] hover:text-white text-[#a1a1aa] rounded-xl text-xs font-semibold tracking-wide transition-colors cursor-pointer"
          >
            Go to Dashboard Onboarding
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {audits.map((audit) => (
            <div key={audit.id} className="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-emerald-400 mb-1">{audit.url}</h3>
                  <div className="text-xs text-[#a1a1aa] font-mono">{audit.id}</div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  audit.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                  audit.status === 'FAILED' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                  'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {audit.status}
                </div>
              </div>

              {audit.status === 'COMPLETED' && (
                <div className="mt-6 pt-6 border-t border-[#27272a] grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="flex flex-col">
                    <span className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-1">Overall</span>
                    <span className="text-2xl font-medium">{audit.overall_score?.toFixed(1) ?? 'N/A'}%</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-1">Schema</span>
                    <span className="text-xl font-medium">{audit.schema_markup_score?.toFixed(1) ?? 'N/A'}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-1">Structure</span>
                    <span className="text-xl font-medium">{audit.content_structure_score?.toFixed(1) ?? 'N/A'}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-1">Stuffing</span>
                    <span className="text-xl font-medium">{audit.keyword_stuffing_score?.toFixed(1) ?? 'N/A'}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-[#a1a1aa] uppercase tracking-wider mb-1">Semantic</span>
                    <span className="text-xl font-medium">{audit.semantic_alignment_score?.toFixed(1) ?? 'N/A'}</span>
                  </div>
                </div>
              )}
              
              {audit.status === 'FAILED' && audit.error_message && (
                <div className="mt-6 pt-6 border-t border-red-500/20 bg-red-500/5 p-4 rounded-xl text-sm text-red-400 font-medium font-mono flex flex-col gap-1.5">
                  <span className="text-xs uppercase tracking-wider text-red-500 font-bold">Crawl Failure Log</span>
                  <span>{audit.error_message}</span>
                </div>
              )}

              {audit.recommendations && Object.keys(audit.recommendations).length > 0 && (
                <div className="mt-6 pt-6 border-t border-[#27272a]">
                  <h4 className="text-sm font-medium mb-3 text-slate-300">Recommendations</h4>
                  <ul className="space-y-2">
                    {Object.entries(audit.recommendations).map(([key, value]) => (
                      <li key={key} className="text-sm text-[#a1a1aa] flex gap-2">
                        <span className="text-emerald-500 mt-0.5">✦</span>
                        <span>{String(value)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
