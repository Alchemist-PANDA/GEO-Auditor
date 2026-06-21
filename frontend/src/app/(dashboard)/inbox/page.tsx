'use client';

import React, { useState } from 'react';
import { Bell, Filter, ChevronDown, TrendingDown, TrendingUp, AlertCircle, CheckCircle2, ChevronRight, Activity, Zap, BarChart2 } from 'lucide-react';

export default function InboxPage() {
  const [selectedAlert, setSelectedAlert] = useState(1);

  const alerts = [
    { 
      id: 1, 
      type: 'Visibility Drop', 
      title: 'Sudden drop in ChatGPT for "corporate cards"',
      desc: 'Visibility decreased by 15% in the last 24h across OpenAI models.',
      time: '2 hours ago',
      priority: 'High',
      icon: TrendingDown,
      color: 'text-[#ef4444]',
      bg: 'bg-[#fef2f2]',
      unread: true
    },
    { 
      id: 2, 
      type: 'Competitor Surge', 
      title: 'Ramp gaining Share of Voice',
      desc: 'Competitor Ramp has captured 8% new SOV for expense management topics.',
      time: '5 hours ago',
      priority: 'Medium',
      icon: Activity,
      color: 'text-[#f59e0b]',
      bg: 'bg-[#fffbeb]',
      unread: true
    },
    { 
      id: 3, 
      type: 'New Citation', 
      title: 'New high-authority backlink cited in Perplexity',
      desc: 'Forbes article newly indexed by Perplexity Pro.',
      time: '1 day ago',
      priority: 'Low',
      icon: CheckCircle2,
      color: 'text-[#10b981]',
      bg: 'bg-[#ecfdf5]',
      unread: false
    },
    { 
      id: 4, 
      type: 'Recommendation Generated', 
      title: 'New AEO optimization strategy ready',
      desc: 'Profound has generated 3 new content suggestions to reclaim SOV.',
      time: '2 days ago',
      priority: 'Medium',
      icon: Zap,
      color: 'text-[#3b82f6]',
      bg: 'bg-[#eff6ff]',
      unread: false
    },
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-[#0f172a] p-8 font-sans">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-[#0f172a] flex items-center gap-3">
            <Bell className="w-8 h-8 text-[#64748b]" />
            Inbox & Alerts
          </h1>
          <p className="text-[#64748b] mt-1">Real-time monitoring and anomaly detection across all Answer Engines.</p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#e2e8f0] rounded-md text-sm text-[#64748b] cursor-pointer hover:bg-[#f8fafc] shadow-sm">
            <span>Status: Unread</span>
            <ChevronDown className="w-4 h-4" />
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#e2e8f0] rounded-md text-sm text-[#64748b] cursor-pointer hover:bg-[#f8fafc] shadow-sm">
            <span>Priority: All</span>
            <ChevronDown className="w-4 h-4" />
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#e2e8f0] rounded-md text-sm text-[#64748b] cursor-pointer hover:bg-[#f8fafc] shadow-sm">
            <Filter className="w-4 h-4" />
            <span>Alert Type</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
        
        {/* Left Pane: Alert Feed */}
        <div className="lg:col-span-1 bg-white border border-[#e2e8f0] rounded-xl shadow-sm flex flex-col overflow-hidden">
          <div className="px-5 py-4 border-b border-[#e2e8f0] bg-[#f8fafc] flex justify-between items-center">
            <h3 className="font-semibold text-[#0f172a]">Alert Feed</h3>
            <span className="text-xs bg-[#e2e8f0] text-[#475569] px-2 py-0.5 rounded-full font-medium">4 Total</span>
          </div>
          <div className="flex-1 overflow-y-auto">
            {alerts.map((alert) => {
              const Icon = alert.icon;
              const isSelected = selectedAlert === alert.id;
              
              return (
                <div 
                  key={alert.id}
                  onClick={() => setSelectedAlert(alert.id)}
                  className={`p-4 border-b border-[#e2e8f0] cursor-pointer transition-colors relative ${isSelected ? 'bg-[#f1f5f9]' : 'hover:bg-[#f8fafc]'}`}
                >
                  {isSelected && <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#3b82f6]"></div>}
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded-lg ${alert.bg}`}>
                        <Icon className={`w-4 h-4 ${alert.color}`} />
                      </div>
                      <span className="text-xs font-medium text-[#64748b] uppercase tracking-wider">{alert.type}</span>
                    </div>
                    <span className="text-xs text-[#94a3b8]">{alert.time}</span>
                  </div>
                  <h4 className={`text-sm mb-1 ${alert.unread ? 'font-semibold text-[#0f172a]' : 'font-medium text-[#334155]'}`}>
                    {alert.title}
                  </h4>
                  <p className="text-sm text-[#64748b] line-clamp-2">{alert.desc}</p>
                  
                  {alert.unread && <div className="w-2 h-2 rounded-full bg-[#3b82f6] absolute right-4 top-1/2 -translate-y-1/2"></div>}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Pane: Detail Panel */}
        <div className="lg:col-span-2 bg-white border border-[#e2e8f0] rounded-xl shadow-sm flex flex-col overflow-hidden">
          {selectedAlert === 1 ? (
            <div className="p-8 h-full flex flex-col">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 rounded-xl bg-[#fef2f2]">
                  <TrendingDown className="w-6 h-6 text-[#ef4444]" />
                </div>
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-[#fef2f2] text-[#ef4444] border border-[#fecaca]">HIGH PRIORITY</span>
                    <span className="text-sm text-[#64748b]">2 hours ago</span>
                  </div>
                  <h2 className="text-2xl font-semibold text-[#0f172a]">Sudden drop in ChatGPT for "corporate cards"</h2>
                </div>
              </div>

              <div className="flex-1">
                <p className="text-[#334155] mb-8 text-lg">
                  We detected a significant visibility decrease of 15% in the last 24 hours specifically across OpenAI's GPT-4o models for the exact match query <code className="bg-[#f1f5f9] px-2 py-0.5 rounded text-[#0f172a] text-sm">corporate cards</code>.
                </p>

                <div className="grid grid-cols-2 gap-4 mb-8">
                  <div className="border border-[#e2e8f0] rounded-xl p-5 bg-[#f8fafc]">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-[#64748b]">Previous Visibility</span>
                      <BarChart2 className="w-4 h-4 text-[#94a3b8]" />
                    </div>
                    <div className="text-2xl font-semibold text-[#0f172a]">82.4%</div>
                    <span className="text-xs text-[#64748b]">Prior 7-day average</span>
                  </div>
                  <div className="border border-[#fecaca] rounded-xl p-5 bg-[#fef2f2]">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-[#ef4444]">Current Visibility</span>
                      <TrendingDown className="w-4 h-4 text-[#ef4444]" />
                    </div>
                    <div className="text-2xl font-semibold text-[#ef4444]">67.4%</div>
                    <span className="text-xs text-[#ef4444]">-15.0% absolute drop</span>
                  </div>
                </div>

                <div className="border border-[#e2e8f0] rounded-xl overflow-hidden mb-8">
                  <div className="px-5 py-3 bg-[#f8fafc] border-b border-[#e2e8f0]">
                    <h3 className="text-sm font-semibold text-[#0f172a]">Root Cause Analysis</h3>
                  </div>
                  <div className="p-5">
                    <p className="text-sm text-[#475569] mb-4">
                      Our engines identified that ChatGPT has started favoring a newly published comparison guide from Nerdwallet, pushing your brand's primary landing page out of the top 3 citations.
                    </p>
                    <div className="flex items-center gap-2 p-3 rounded-lg bg-[#f1f5f9] border border-[#e2e8f0]">
                      <AlertCircle className="w-4 h-4 text-[#f59e0b]" />
                      <span className="text-sm text-[#334155]">Competitor <strong className="font-semibold text-[#0f172a]">Ramp</strong> was cited alongside Nerdwallet in 80% of these new responses.</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-[#0f172a] mb-3">Suggested Actions</h3>
                  <div className="space-y-3">
                    <button className="w-full flex items-center justify-between p-4 border border-[#e2e8f0] rounded-xl hover:border-[#3b82f6] hover:bg-[#eff6ff] transition-all group shadow-sm">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-[#e0e7ff] flex items-center justify-center">
                          <Zap className="w-4 h-4 text-[#4f46e5]" />
                        </div>
                        <div className="text-left">
                          <div className="text-sm font-semibold text-[#0f172a] group-hover:text-[#2563eb]">Generate AEO Optimization Plan</div>
                          <div className="text-xs text-[#64748b]">Create tailored content recommendations to counter Nerdwallet's narrative.</div>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-[#94a3b8] group-hover:text-[#2563eb]" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-[#94a3b8]">
              <Bell className="w-12 h-12 mb-4 opacity-20" />
              <p>Select an alert to view details and suggested actions.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
