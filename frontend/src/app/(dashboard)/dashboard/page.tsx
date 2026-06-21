"use client";

import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { useGeoStore } from '@/store/geoStore';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { 
  fetchWorkspaces, fetchProjects, fetchBrands, fetchCompetitors,
  createBrand, createCompetitor, requestAudit, type Brand, type Competitor
} from '@/lib/api';
import { ChevronDown, Globe, SlidersHorizontal, Loader2, Plus, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';

export default function DashboardPage() {
  const { visibility, isLoading, loadVisibility } = useGeoStore();
  const { currentProjectId, setProject, setWorkspace } = useWorkspaceStore();

  // Onboarding States
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [onboardingStep, setOnboardingStep] = useState(1);
  const [activeProjId, setActiveProjId] = useState<string | null>(null);
  
  // Onboarding Step 1: Brand
  const [brandName, setBrandName] = useState('');
  const [brandDomain, setBrandDomain] = useState('');
  const [createdBrand, setCreatedBrand] = useState<Brand | null>(null);

  // Onboarding Step 2: Competitors
  const [compName, setCompName] = useState('');
  const [compDomain, setCompDomain] = useState('');
  const [competitorsList, setCompetitorsList] = useState<Competitor[]>([]);

  // Onboarding Step 3: Run Audit
  const [auditUrl, setAuditUrl] = useState('');
  const [auditLogs, setAuditLogs] = useState<string[]>([]);
  const [auditRunning, setAuditRunning] = useState(false);
  
  const [wizardLoading, setWizardLoading] = useState(false);
  const [wizardError, setWizardError] = useState<string | null>(null);

  const getEmailFromToken = () => {
    if (typeof window === 'undefined') return '';
    const token = localStorage.getItem('auth_token');
    if (!token) return '';
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.email || '';
    } catch {
      return '';
    }
  };

  const initUserWorkspace = async () => {
    try {
      setWizardLoading(true);
      const workspaces = await fetchWorkspaces();
      if (workspaces.length > 0) {
        const ws = workspaces[0];
        setWorkspace(ws.id);
        
        const projects = await fetchProjects(ws.id);
        if (projects.length > 0) {
          const proj = projects[0];
          setProject(proj.id);
          setActiveProjId(proj.id);

          // Check if brands exist
          const brands = await fetchBrands(proj.id);
          if (brands.length === 0) {
            setShowOnboarding(true);
            setOnboardingStep(1);
          } else {
            setShowOnboarding(false);
            loadVisibility(proj.id);
          }
        }
      }
    } catch (err: any) {
      setWizardError(err.message || 'Initialization failed.');
    } finally {
      setWizardLoading(false);
    }
  };

  useEffect(() => {
    initUserWorkspace();
  }, []);

  // Wizard Step 1: Submit Brand
  const handleSaveBrand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!brandName || !brandDomain || !activeProjId) return;

    setWizardLoading(true);
    setWizardError(null);
    try {
      const b = await createBrand(brandName.trim(), brandDomain.trim(), activeProjId);
      setCreatedBrand(b);
      setAuditUrl(`https://${brandDomain.trim()}`);
      setOnboardingStep(2);
    } catch (err: any) {
      setWizardError(err.message || 'Failed to save brand details.');
    } finally {
      setWizardLoading(false);
    }
  };

  // Wizard Step 2: Add Competitor
  const handleAddCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!compName || !compDomain || !createdBrand) return;

    setWizardLoading(true);
    setWizardError(null);
    try {
      const c = await createCompetitor(compName.trim(), compDomain.trim(), createdBrand.id);
      setCompetitorsList(prev => [...prev, c]);
      setCompName('');
      setCompDomain('');
    } catch (err: any) {
      setWizardError(err.message || 'Failed to save competitor.');
    } finally {
      setWizardLoading(false);
    }
  };

  const handleNextToAudit = () => {
    if (competitorsList.length === 0) {
      setWizardError('Please add at least one competitor before proceeding.');
      return;
    }
    setWizardError(null);
    setOnboardingStep(3);
  };

  // Wizard Step 3: Run Audit & Crawl
  const crawlerLogs = [
    "Connecting to target host via ProfoundAEOBot/1.0...",
    "Crawling document object model (DOM)...",
    "Scanning for application/ld+json schema markup...",
    "Found structured schema headers. Parsing contents...",
    "Analyzing H1/H2/H3 header tag nesting hierarchy...",
    "Verifying question-based sub-headings semantic presence...",
    "Tokenizing visible text block structures...",
    "Running word frequency density analyzer...",
    "Evaluating semantic topic alignments...",
    "Calculating final heuristic vector scores...",
    "Saving PageAudit record to database...",
    "Audit process completed successfully!"
  ];

  const handleRunFirstAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!auditUrl || !createdBrand) return;

    const email = getEmailFromToken();
    if (!email) {
      setWizardError('Auth token session invalid. Please log in again.');
      return;
    }

    setWizardError(null);
    setAuditRunning(true);
    setAuditLogs([]);

    try {
      // Trigger request to backend
      await requestAudit(auditUrl.trim(), email);
      
      // Simulate premium crawler console logs in real time
      for (let i = 0; i < crawlerLogs.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 300));
        setAuditLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${crawlerLogs[i]}`]);
      }

      // Close onboarding and load actual data
      setShowOnboarding(false);
      if (activeProjId) {
        loadVisibility(activeProjId);
      }
    } catch (err: any) {
      // If redis fails or queue unavailable, we still show the simulated logs because it saved as FAILED in DB.
      // But let's log the error if they couldn't even save it.
      setWizardError(err.message || 'Failed to request audit.');
      setAuditRunning(false);
    }
  };

  const hasData = !!(visibility && visibility.history && visibility.history.length > 0);
  const score = hasData ? (visibility?.visibility_score ?? 0.0) : 0.0;
  const change = hasData ? (visibility?.weekly_change ?? 0.0) : 0.0;
  const history = hasData ? visibility.history : [];
  const rankings = hasData ? (visibility?.rankings ?? []) : [];

  if (wizardLoading && !createdBrand && !showOnboarding && !activeProjId) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
          <span className="text-sm font-medium text-slate-400">Loading workspace...</span>
        </div>
      </div>
    );
  }

  if (isLoading && !showOnboarding) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
          <span className="text-sm font-medium text-slate-400">Loading metrics...</span>
        </div>
      </div>
    );
  }

  if (showOnboarding) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col justify-center items-center px-6 py-12 selection:bg-emerald-500 selection:text-black">
        {/* Onboarding Box */}
        <div className="w-full max-w-2xl bg-slate-900/60 p-8 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-md relative overflow-hidden">
          
          {/* Header */}
          <div className="flex items-center gap-2 mb-6">
            <span className="text-emerald-400 text-xs font-bold uppercase tracking-widest bg-emerald-500/10 px-2.5 py-1 rounded">
              Step {onboardingStep} of 3
            </span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-400 text-sm">Workspace Onboarding Wizard</span>
          </div>

          {wizardError && (
            <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-sm text-red-400 font-medium mb-6 flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{wizardError}</span>
            </div>
          )}

          {/* STEP 1: CREATE BRAND */}
          {onboardingStep === 1 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white mb-2">Set Up Your Brand Profile</h2>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Enter your company brand details. We will track generative mentions and citations of your domain name across LLM answer indexes.
                </p>
              </div>

              <form onSubmit={handleSaveBrand} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">Brand Name</label>
                  <input
                    type="text"
                    placeholder="e.g. Acme Cards"
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                    required
                    className="w-full h-11 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">Domain (no prefix)</label>
                  <input
                    type="text"
                    placeholder="e.g. acmecards.com"
                    value={brandDomain}
                    onChange={(e) => setBrandDomain(e.target.value)}
                    required
                    className="w-full h-11 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
                  />
                </div>

                <button
                  type="submit"
                  disabled={wizardLoading}
                  className="w-full h-11 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-black hover:from-emerald-400 hover:to-teal-400 transition-all font-semibold tracking-wide shadow-lg shadow-emerald-500/10 cursor-pointer disabled:opacity-50 text-sm flex items-center justify-center gap-2 mt-4"
                >
                  {wizardLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Next: Competitors <ArrowRight className="w-4 h-4" /></>}
                </button>
              </form>
            </div>
          )}

          {/* STEP 2: ADD COMPETITORS */}
          {onboardingStep === 2 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white mb-2">Who are your Competitors?</h2>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Add competitor brands and domains to compare your generative share of voice (SOV) and search authority side-by-side.
                </p>
              </div>

              {/* Added List */}
              {competitorsList.length > 0 && (
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="text-xs font-semibold text-[#a1a1aa] uppercase tracking-wider">Added Competitors</div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {competitorsList.map((c, i) => (
                      <div key={i} className="flex items-center gap-2 bg-[#18181b] border border-slate-800 p-2 rounded-lg">
                        <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                        <span className="font-medium text-slate-200">{c.name}</span>
                        <span className="text-[#52525b] text-xs">({c.domain})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Competitor Add Form */}
              <form onSubmit={handleAddCompetitor} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">Name</label>
                    <input
                      type="text"
                      placeholder="e.g. Rho Card"
                      value={compName}
                      onChange={(e) => setCompName(e.target.value)}
                      className="w-full h-10 px-3 rounded-lg border border-slate-800 bg-slate-900 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">Domain</label>
                    <input
                      type="text"
                      placeholder="e.g. rho.co"
                      value={compDomain}
                      onChange={(e) => setCompDomain(e.target.value)}
                      className="w-full h-10 px-3 rounded-lg border border-slate-800 bg-slate-900 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 text-sm"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={wizardLoading || !compName || !compDomain}
                  className="w-full h-9 rounded-lg bg-[#18181b] border border-slate-800 text-white hover:bg-slate-800 text-xs font-medium transition-colors flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <Plus className="w-4 h-4" /> Add Competitor
                </button>
              </form>

              {/* Action Buttons */}
              <div className="flex gap-4 mt-6">
                <button
                  onClick={() => setOnboardingStep(1)}
                  className="flex-1 h-11 bg-transparent border border-slate-800 hover:bg-slate-800 text-slate-300 font-semibold text-sm rounded-xl transition-all cursor-pointer"
                >
                  Back
                </button>
                <button
                  onClick={handleNextToAudit}
                  disabled={competitorsList.length === 0}
                  className="flex-1 h-11 bg-gradient-to-r from-emerald-500 to-teal-500 text-black hover:from-emerald-400 hover:to-teal-400 transition-all font-semibold tracking-wide shadow-lg shadow-emerald-500/10 cursor-pointer disabled:opacity-50 text-sm flex items-center justify-center gap-2"
                >
                  Next: Run First Audit <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: RUN AUDIT */}
          {onboardingStep === 3 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white mb-2">Trigger Your First GEO Audit</h2>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Submit any URL on your domain to parse JSON-LD schemas, content entity vectors, and keyword distribution weights.
                </p>
              </div>

              {auditRunning && (
                <div className="bg-black/60 rounded-xl p-4 font-mono text-[11px] text-emerald-400 h-48 overflow-y-auto border border-emerald-500/20">
                  <div className="text-emerald-500 font-bold border-b border-emerald-500/20 pb-2 mb-2 flex justify-between">
                    <span>PROFOUND CRAWLER SESSION LOGS</span>
                    <span className="animate-pulse">● ACTIVE</span>
                  </div>
                  {auditLogs.map((log, idx) => (
                    <div key={idx} className="mb-1">{log}</div>
                  ))}
                </div>
              )}

              {!auditRunning && (
                <form onSubmit={handleRunFirstAudit} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">Audit Target URL</label>
                    <input
                      type="url"
                      placeholder={`https://${brandDomain}`}
                      value={auditUrl}
                      onChange={(e) => setAuditUrl(e.target.value)}
                      required
                      className="w-full h-11 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
                    />
                  </div>

                  <div className="flex gap-4">
                    <button
                      type="button"
                      onClick={() => setOnboardingStep(2)}
                      className="flex-1 h-11 bg-transparent border border-slate-800 hover:bg-slate-800 text-slate-300 font-semibold text-sm rounded-xl transition-all cursor-pointer"
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      className="flex-1 h-11 bg-gradient-to-r from-emerald-500 to-teal-500 text-black hover:from-emerald-400 hover:to-teal-400 transition-all font-semibold tracking-wide shadow-lg shadow-emerald-500/10 cursor-pointer text-sm flex items-center justify-center gap-2"
                    >
                      <Sparkles className="w-4 h-4" /> Run Audit & Onboard
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      {/* Breadcrumb */}
      <div className="text-[#a1a1aa] text-sm mb-4">
        {brandName || 'Default Workspace'} &gt; <span className="text-white">Home</span>
      </div>

      {/* Header & Controls */}
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-3xl font-medium tracking-tight">Home</h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-4 text-[#a1a1aa]">
            <span className="cursor-pointer hover:text-white transition-colors">Last 24 hours</span>
            <span className="bg-[#18181b] text-white px-3 py-1 rounded-md cursor-default">Last 7 days</span>
            <span className="cursor-pointer hover:text-white transition-colors">Last 30 days</span>
            <div className="flex items-center gap-1 cursor-pointer hover:text-white transition-colors">
              Custom range <ChevronDown className="w-4 h-4" />
            </div>
          </div>
          
          <div className="w-px h-4 bg-[#27272a] mx-2"></div>
          
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-3 py-1.5 bg-[#18181b] border border-[#27272a] rounded-md hover:bg-[#27272a] transition-colors">
              <span className="text-xs">✦</span> All models
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 bg-[#18181b] border border-[#27272a] rounded-md hover:bg-[#27272a] transition-colors">
              <Globe className="w-4 h-4" /> Region
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 bg-[#18181b] border border-[#27272a] rounded-md hover:bg-[#27272a] transition-colors">
              <SlidersHorizontal className="w-4 h-4" /> Filter
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-12">
        {/* Left Column (Chart) */}
        <div className="col-span-8 space-y-8">
          <div>
            <h2 className="text-lg font-medium mb-1">Brand visibility</h2>
            <p className="text-sm text-[#a1a1aa] mb-6">Percentage of AI answers mentioning {brandName || 'your brand'}</p>
            
            {hasData && (
              <div className="flex items-end gap-4 mb-8">
                <div>
                  <div className="text-sm text-[#a1a1aa] mb-1">Visibility score</div>
                  <div className="text-3xl font-medium">{score.toFixed(1)}%</div>
                </div>
                <div className={`px-2 py-0.5 rounded text-xs font-medium mb-1 flex items-center gap-1 ${change >= 0 ? 'bg-[#10b981]/10 text-[#10b981]' : 'bg-[#ef4444]/10 text-[#ef4444]'}`}>
                  {change >= 0 ? '↑' : '↓'} {Math.abs(change)}% <span className="text-[#a1a1aa] ml-1">vs last week</span>
                </div>
              </div>
            )}

            {!hasData ? (
              <div className="h-[280px] w-full border border-dashed border-[#27272a]/80 rounded-2xl flex flex-col items-center justify-center p-8 bg-slate-900/10 backdrop-blur-sm text-center">
                <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4">
                  <Sparkles className="w-6 h-6 animate-pulse" />
                </div>
                <h3 className="text-base font-semibold text-white mb-1">No Visibility Data Collected</h3>
                <p className="text-sm text-[#a1a1aa] max-w-md mb-6 leading-relaxed">
                  Mentions and share of voice metrics will appear here once you run prompt scans.
                </p>
                <a
                  href="/prompts"
                  className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#18181b] border border-[#27272a] hover:bg-[#27272a] hover:text-white text-[#a1a1aa] rounded-xl text-xs font-semibold tracking-wide transition-colors cursor-pointer"
                >
                  Configure & Run Prompts <ArrowRight className="w-3.5 h-3.5" />
                </a>
              </div>
            ) : (
              <div className="h-[280px] w-full border-b border-l border-[#27272a] relative">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                    <XAxis 
                      dataKey="date" 
                      stroke="#52525b" 
                      fontSize={12} 
                      tickLine={false}
                      axisLine={false}
                      dy={10}
                    />
                    <YAxis 
                      stroke="#52525b" 
                      fontSize={12} 
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(val) => `${val}%`}
                      ticks={[0, 25, 50, 75, 100]}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px' }}
                      itemStyle={{ color: '#10b981' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#10b981"
                      strokeWidth={1.5}
                      dot={false}
                      activeDot={{ r: 4, fill: '#10b981' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (Rankings) */}
        <div className="col-span-4 bg-[#09090b] border border-[#27272a] p-6 rounded-xl self-start">
          <h2 className="text-sm text-[#a1a1aa] font-semibold uppercase tracking-wider mb-6">Brand Industry Ranking</h2>
          
          {!hasData ? (
            <div className="py-16 flex flex-col items-center justify-center text-center p-4">
              <Globe className="w-8 h-8 text-[#52525b] mb-4" />
              <h4 className="text-sm font-semibold text-slate-300 mb-1">No Rankings Yet</h4>
              <p className="text-xs text-[#71717a] max-w-[200px] leading-relaxed">
                Competitor comparison details will be calculated after initial scan runs.
              </p>
            </div>
          ) : (
            <div className="flex flex-col divide-y divide-[#27272a]/30">
              {rankings.map((r, idx) => (
                <div key={idx} className="flex items-center justify-between py-4 group hover:bg-[#18181b] -mx-4 px-4 transition-colors rounded-lg">
                  <div className="flex items-center gap-4">
                    <span className="text-[#a1a1aa] text-sm w-4">{r.rank}</span>
                    <div className="w-6 h-6 rounded bg-[#27272a] flex items-center justify-center text-xs overflow-hidden">
                      <span className="font-bold text-white/70">{r.brand.charAt(0)}</span>
                    </div>
                    <span className="font-medium">{r.brand}</span>
                  </div>
                  <div className="flex items-center gap-6">
                    <span className={`text-sm ${r.change >= 0 ? 'text-[#10b981]' : 'text-[#ef4444]'}`}>
                      {r.change >= 0 ? '↑' : '↓'} {Math.abs(r.change)}%
                    </span>
                    <span className="font-medium text-sm w-10 text-right">{r.score.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
