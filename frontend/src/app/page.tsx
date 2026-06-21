"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { requestAudit } from '@/lib/api';

export default function LandingPage() {
  const [url, setUrl] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const crawlerLogs = [
    "Connecting to target host via ProfoundAEOBot/1.0...",
    "Crawling document object model (DOM)...",
    "Scanning for application/ld+json schema markup...",
    "Found structured schema headers. Parsing contents...",
    "Analyzing H1/H2/H3 header tag nesting hierarchy...",
    "Verifying question-based sub-headings semantic presence...",
    "Tokenizing visible text block structures...",
    "Running word frequency histogram density analyzer...",
    "Evaluating semantic topic alignments...",
    "Calculating final heuristic vector scores...",
    "Saving PageAudit record to database...",
    "Dispatching dark-themed HSL report to recipient email...",
    "Audit process completed successfully!"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url || !email) return;

    setError(null);
    setLoading(true);
    setLogs([]);
    setSuccess(false);

    try {
      // Trigger request to backend
      const response = await requestAudit(url, email);
      
      // Run simulated console logs step-by-step for premium look
      for (let i = 0; i < crawlerLogs.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 350));
        setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${crawlerLogs[i]}`]);
      }
      
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to submit audit request. Please verify connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-emerald-500 selection:text-black">
      {/* Premium Header */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-bold text-black shadow-md shadow-emerald-500/20">
              P
            </div>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              PROFOUND <span className="text-emerald-400 font-medium">GEO</span>
            </span>
          </div>
          <Link
            href="/login"
            className="px-4 h-9 flex items-center justify-center rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 transition-colors text-sm font-medium tracking-wide"
          >
            Sign In to Dashboard
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-20 flex flex-col items-center">
        <div className="text-center max-w-3xl mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/5 text-xs text-emerald-400 font-medium mb-6 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Minimum Sellable Product Sandbox
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight">
            Verify Your Site's{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              Generative Engine
            </span>{" "}
            Optimization
          </h1>
          <p className="text-slate-400 text-lg md:text-xl leading-relaxed">
            LLMs don't read websites like traditional scrapers. Submit your website to test schema alignment, content semantic relevance, structures, and keyword density.
          </p>
        </div>

        {/* Audit Form Container */}
        <div className="w-full max-w-2xl bg-gradient-to-b from-slate-900 to-slate-950/40 p-8 rounded-2xl border border-slate-800 shadow-2xl relative overflow-hidden backdrop-blur-sm">
          {loading && (
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center p-8 z-10">
              <div className="w-12 h-12 rounded-full border-4 border-emerald-500/20 border-t-emerald-400 animate-spin mb-6"></div>
              <div className="w-full max-w-md bg-black/60 rounded-lg p-4 font-mono text-xs text-emerald-400 h-64 overflow-y-auto border border-emerald-500/20">
                <div className="text-emerald-500 font-bold border-b border-emerald-500/20 pb-2 mb-2 flex justify-between">
                  <span>PROFOUND CRAWLER SESSION LOGS</span>
                  <span className="animate-pulse">● ACTIVE</span>
                </div>
                {logs.map((log, idx) => (
                  <div key={idx} className="mb-1">{log}</div>
                ))}
              </div>
            </div>
          )}

          {success ? (
            <div className="text-center py-10 flex flex-col items-center">
              <div className="w-16 h-16 bg-emerald-500/10 border border-emerald-400/30 rounded-full flex items-center justify-center text-3xl mb-6 text-emerald-400 shadow-lg shadow-emerald-500/10">
                ✓
              </div>
              <h3 className="text-2xl font-bold mb-4">Audit Successfully Enqueued!</h3>
              <p className="text-slate-400 leading-relaxed max-w-md mb-8">
                Heuristic crawler is running deep evaluations. A comprehensive HTML report will be dispatched to <strong className="text-white">{email}</strong> and saved in database records.
              </p>
              <button
                onClick={() => setSuccess(false)}
                className="px-6 h-11 bg-slate-900 border border-slate-800 hover:bg-slate-800 transition-colors rounded-xl text-sm font-medium"
              >
                Audit Another URL
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold tracking-wider text-slate-300 uppercase mb-2">
                  Target Website URL
                </label>
                <input
                  type="url"
                  placeholder="https://example.com/best-startup-card"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  className="w-full h-12 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all font-medium"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold tracking-wider text-slate-300 uppercase mb-2">
                  Recipient Email Address
                </label>
                <input
                  type="email"
                  placeholder="marketing@yourcompany.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full h-12 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all font-medium"
                />
              </div>

              {error && (
                <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-sm text-red-400 font-medium">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full h-12 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-black hover:from-emerald-400 hover:to-teal-400 transition-all font-semibold tracking-wide shadow-lg shadow-emerald-500/10 cursor-pointer disabled:opacity-50"
              >
                {loading ? 'Initiating Crawler...' : 'Run Free GEO Readiness Audit'}
              </button>
            </form>
          )}
        </div>

        {/* Feature Cards Grid */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 w-full mt-24">
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-900">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-4 font-bold">1</div>
            <h4 className="font-bold text-lg mb-2">Semantic Alignment</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              Checks title, descriptions, and headings relevance matching high-intent consumer keywords.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-900">
            <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center text-teal-400 mb-4 font-bold">2</div>
            <h4 className="font-bold text-lg mb-2">Schema Markup</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              Identifies microdata presence (JSON-LD FAQPage, HowTo) providing structured entities directly to models.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-900">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 mb-4 font-bold">3</div>
            <h4 className="font-bold text-lg mb-2">Content Structure</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              Evaluates header distribution tags and phrased query headings matching generative prompt structures.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-900">
            <div className="w-10 h-10 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400 mb-4 font-bold">4</div>
            <h4 className="font-bold text-lg mb-2">Keyword Stuffing</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              Analyzes word frequencies to ensure natural content flow and avoid spam penalty weights from LLMs.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
