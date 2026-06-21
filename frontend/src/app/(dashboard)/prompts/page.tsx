"use client";

import React, { useEffect, useState } from 'react';
import { Search, ChevronDown, Check, HelpCircle, Loader2, Sparkles, MessageSquare, Play, Tag, Globe, Calendar } from 'lucide-react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { fetchPrompts, createPrompts, triggerRun, type PromptWithRuns } from '@/lib/api';

export default function PromptsPage() {
  const { currentProjectId } = useWorkspaceStore();
  const [prompts, setPrompts] = useState<PromptWithRuns[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Create prompt inputs
  const [newPromptText, setNewPromptText] = useState('');
  const [newPromptLocale, setNewPromptLocale] = useState('en-US');
  const [newPromptTags, setNewPromptTags] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Run prompts inputs
  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt-4o', 'claude-3-haiku']);
  const [running, setRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  // Search filter
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = async () => {
    const pid = currentProjectId || 'demo-project';
    try {
      setLoading(true);
      const data = await fetchPrompts(pid);
      setPrompts(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load prompts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentProjectId]);

  const handleAddPrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPromptText.trim()) return;

    const pid = currentProjectId || 'demo-project';
    setSubmitting(true);
    setError(null);

    try {
      const tagsArray = newPromptTags
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);

      await createPrompts(pid, [{
        text: newPromptText.trim(),
        locale: newPromptLocale,
        tags: tagsArray
      }]);

      setNewPromptText('');
      setNewPromptTags('');
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to add prompt. It might exceed the workspace limit.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTriggerRun = async () => {
    if (selectedModels.length === 0) return;
    const pid = currentProjectId || 'demo-project';
    setRunning(true);
    setRunMessage(null);
    try {
      const res = await triggerRun(pid, selectedModels);
      setRunMessage(res.message || 'Prompt run successfully enqueued!');
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to run prompts.');
    } finally {
      setRunning(false);
    }
  };

  const toggleModel = (model: string) => {
    setSelectedModels(prev =>
      prev.includes(model)
        ? prev.filter(m => m !== model)
        : [...prev, model]
    );
  };

  const filteredPrompts = prompts.filter(p =>
    p.text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Compute used capacity
  const maxCapacity = 40;
  const usedCapacity = prompts.length;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      {/* Top Header */}
      <div className="flex justify-between items-center mb-8 pb-4 border-b border-[#27272a]/40">
        <div>
          <h1 className="text-3xl font-medium tracking-tight">Prompts</h1>
          <p className="text-sm text-[#a1a1aa] mt-1">Manage tracking prompts and configure generative engine executions</p>
        </div>
        
        <div className="flex items-center gap-2 text-sm text-[#a1a1aa] hover:text-white cursor-pointer transition-colors">
          <HelpCircle className="w-4 h-4" />
          <span>Documentation</span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-sm text-red-400 font-medium mb-6">
          {error}
        </div>
      )}

      {runMessage && (
        <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 text-sm text-emerald-400 font-medium mb-6">
          {runMessage}
        </div>
      )}

      {/* Main Grid split: left 8 cols for table, right 4 cols for operations */}
      <div className="grid grid-cols-12 gap-8">
        
        {/* Left Column (Prompts Table) */}
        <div className="col-span-8 space-y-6">
          {/* Capacity and Filters info */}
          <div className="bg-[#18181b] border border-[#27272a] rounded-xl p-5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex gap-[2px]">
                 {[...Array(maxCapacity)].map((_, i) => (
                   <div 
                     key={i} 
                     className={`w-1.5 h-3 rounded-sm ${
                       i < usedCapacity ? 'bg-emerald-500' : 'bg-[#27272a]'
                     }`}
                   />
                 ))}
              </div>
              <span className="text-sm font-medium">{usedCapacity} of {maxCapacity} prompts used</span>
            </div>
            <div className="text-xs text-[#a1a1aa]">
              Quota resets at standard billing interval.
            </div>
          </div>

          {/* Search bar */}
          <div className="relative">
            <Search className="w-4 h-4 text-[#52525b] absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search by prompt name..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#09090b] border border-[#27272a] text-white rounded-md text-sm focus:outline-none focus:border-[#52525b]"
            />
          </div>

          {/* Table Container */}
          <div className="bg-[#09090b] border border-[#27272a] rounded-xl overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center p-12">
                <Loader2 className="w-8 h-8 rounded-full text-emerald-500 animate-spin" />
              </div>
            ) : filteredPrompts.length === 0 ? (
              <div className="text-center py-12 text-[#a1a1aa]">
                No active prompts found. Add one on the right to start tracking.
              </div>
            ) : (
              <table className="w-full text-sm text-left">
                <thead className="bg-[#18181b]/55 text-[#a1a1aa] border-b border-[#27272a]">
                  <tr>
                    <th className="py-3 px-4 font-normal">Prompt Text</th>
                    <th className="py-3 px-4 font-normal w-24">Locale</th>
                    <th className="py-3 px-4 font-normal">Tags</th>
                    <th className="py-3 px-4 font-normal w-32">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#27272a]/30">
                  {filteredPrompts.map((row) => (
                    <tr key={row.id} className="hover:bg-[#18181b]/20 transition-colors">
                      <td className="py-3.5 px-4 font-medium text-white max-w-xs truncate">{row.text}</td>
                      <td className="py-3.5 px-4 text-[#a1a1aa]">
                        <span className="flex items-center gap-1">
                          <Globe className="w-3 h-3 text-[#52525b]" />
                          {row.locale}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {row.tags.length === 0 ? (
                            <span className="text-xs text-[#52525b] italic">None</span>
                          ) : (
                            row.tags.map((tag, idx) => (
                              <span 
                                key={idx} 
                                className="px-2 py-0.5 rounded border border-[#27272a] bg-[#18181b] text-emerald-400 text-xs font-medium"
                              >
                                {tag}
                              </span>
                            ))
                          )}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        {row.prompt_runs.length === 0 ? (
                          <span className="text-[#a1a1aa] bg-[#18181b] px-2 py-0.5 rounded-full">Not Evaluated</span>
                        ) : (
                          <span className="flex flex-col gap-1">
                            <span className="text-[#10b981] font-semibold">
                              {row.prompt_runs.filter(r => r.status === 'COMPLETED').length} Runs Ok
                            </span>
                            {row.prompt_runs.filter(r => r.status === 'PENDING').length > 0 && (
                              <span className="text-amber-500 animate-pulse text-[10px]">
                                {row.prompt_runs.filter(r => r.status === 'PENDING').length} Pending
                              </span>
                            )}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Right Column (Controls/Add Prompt Form) */}
        <div className="col-span-4 space-y-6">
          {/* Add Prompt Card */}
          <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-emerald-500" />
              Add Tracking Prompt
            </h3>
            
            <form onSubmit={handleAddPrompt} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#a1a1aa] uppercase tracking-wider mb-2">Prompt Text</label>
                <textarea 
                  rows={3}
                  placeholder="e.g. What are the top startups in Seattle?"
                  value={newPromptText}
                  onChange={(e) => setNewPromptText(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-[#18181b] border border-[#27272a] rounded-lg text-white text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#a1a1aa] uppercase tracking-wider mb-2">Locale</label>
                  <select
                    value={newPromptLocale}
                    onChange={(e) => setNewPromptLocale(e.target.value)}
                    className="w-full px-3 py-2 bg-[#18181b] border border-[#27272a] rounded-lg text-white text-sm focus:outline-none focus:border-emerald-500"
                  >
                    <option value="en-US">en-US</option>
                    <option value="de-DE">de-DE</option>
                    <option value="ja-JP">ja-JP</option>
                    <option value="zh-CN">zh-CN</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#a1a1aa] uppercase tracking-wider mb-2">Tags</label>
                  <input
                    type="text"
                    placeholder="comma-separated"
                    value={newPromptTags}
                    onChange={(e) => setNewPromptTags(e.target.value)}
                    className="w-full px-3 py-2 bg-[#18181b] border border-[#27272a] rounded-lg text-white text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2 bg-[#18181b] border border-[#27272a] hover:bg-[#27272a] text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Adding...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-emerald-400" /> Save Prompt
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Trigger Scan Card */}
          <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
              <Play className="w-4 h-4 text-violet-500" />
              Evaluate Prompts
            </h3>
            
            <p className="text-xs text-[#a1a1aa] mb-4">
              Trigger instant generative engine scanning for all active prompts in this project.
            </p>

            <div className="space-y-3 mb-6">
              <div className="text-xs font-semibold text-[#a1a1aa] uppercase tracking-wider mb-1">Select Models</div>
              {['gpt-4o', 'claude-3-haiku', 'gemini-pro'].map((model) => (
                <label key={model} className="flex items-center gap-3 cursor-pointer group">
                  <input 
                    type="checkbox"
                    checked={selectedModels.includes(model)}
                    onChange={() => toggleModel(model)}
                    className="rounded border-[#27272a] text-[#8b5cf6] focus:ring-0 focus:ring-offset-0 bg-[#18181b]"
                  />
                  <span className="text-sm text-slate-300 group-hover:text-white transition-colors">{model.toUpperCase()}</span>
                </label>
              ))}
            </div>

            <button
              onClick={handleTriggerRun}
              disabled={running || prompts.length === 0 || selectedModels.length === 0}
              className="w-full py-2.5 bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {running ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Queuing...
                </>
              ) : (
                <>
                  ⚡ Trigger Scan
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
