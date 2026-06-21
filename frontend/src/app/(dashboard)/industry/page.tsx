'use client';

import React from 'react';
import { BarChart2, ChevronRight, Filter, ChevronDown, ArrowUpRight, ArrowDownRight, Search } from 'lucide-react';

const AreaChart = () => {
  return (
    <div className="w-full h-[300px] mt-6 relative">
      <svg viewBox="0 0 1000 300" preserveAspectRatio="none" className="w-full h-full overflow-visible">
        {/* Grid */}
        {[0, 75, 150, 225, 300].map((y) => (
          <line key={y} x1="0" y1={y} x2="1000" y2={y} stroke="#222" strokeWidth="1" strokeDasharray="4 4" />
        ))}
        {/* Stacked Areas (Bottom to top) */}
        <path d="M0,300 L0,250 C200,240 400,260 600,220 S800,200 1000,180 L1000,300 Z" fill="rgba(16, 185, 129, 0.4)" />
        <path d="M0,250 C200,240 400,260 600,220 S800,200 1000,180 L1000,100 C800,120 600,80 400,110 S200,80 0,90 Z" fill="rgba(59, 130, 246, 0.4)" />
        <path d="M0,90 C200,80 400,110 600,80 S800,120 1000,100 L1000,20 C800,40 600,10 400,30 S200,10 0,20 Z" fill="rgba(139, 92, 246, 0.4)" />
        
        {/* Lines */}
        <path d="M0,250 C200,240 400,260 600,220 S800,200 1000,180" fill="none" stroke="#10b981" strokeWidth="2" />
        <path d="M0,90 C200,80 400,110 600,80 S800,120 1000,100" fill="none" stroke="#3b82f6" strokeWidth="2" />
        <path d="M0,20 C200,10 400,30 600,10 S800,40 1000,20" fill="none" stroke="#8b5cf6" strokeWidth="2" />
      </svg>
      {/* Legend inside SVG area physically */}
      <div className="absolute top-2 right-2 flex gap-4 text-xs text-[#888]">
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#8b5cf6]"></span> Chase</div>
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#3b82f6]"></span> Amex</div>
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#10b981]"></span> Rho</div>
      </div>
    </div>
  );
};

export default function IndustryPage() {
  const competitors = [
    { rank: 1, brand: 'Chase', vis: '92.0%', sov: '45.1%', cit: '12,450', trend: '+2.4%', up: true, color: 'bg-[#8b5cf6]' },
    { rank: 2, brand: 'American Express', vis: '85.2%', sov: '28.4%', cit: '8,210', trend: '-1.1%', up: false, color: 'bg-[#3b82f6]' },
    { rank: 3, brand: 'Rho', vis: '64.8%', sov: '12.5%', cit: '3,420', trend: '+5.8%', up: true, color: 'bg-[#10b981]' },
    { rank: 4, brand: 'Capital on Tap', vis: '52.1%', sov: '8.2%', cit: '2,104', trend: '+1.2%', up: true, color: 'bg-[#f59e0b]' },
    { rank: 5, brand: 'Brex', vis: '41.5%', sov: '3.1%', cit: '890', trend: '-3.4%', up: false, color: 'bg-[#ef4444]' },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      
      {/* Header & Breadcrumbs */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-2 text-sm text-[#888] mb-2">
            <span>Industries</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-white font-medium">Business Credit Cards</span>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-white">Competitive Landscape</h1>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#111] border border-[#222] rounded-md text-sm text-[#ccc] cursor-pointer hover:bg-[#1a1a1a]">
            <span>Last 90 Days</span>
            <ChevronDown className="w-4 h-4" />
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#111] border border-[#222] rounded-md text-sm text-[#ccc] cursor-pointer hover:bg-[#1a1a1a]">
            <Filter className="w-4 h-4" />
            <span>Top 5 Competitors</span>
          </div>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-[#111] border border-[#222] rounded-xl p-5 relative overflow-hidden">
          <div className="text-sm text-[#888] mb-1">Total Category Volume</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-white">45.2M</div>
            <div className="text-sm text-[#888] mb-1">Monthly Prompts</div>
          </div>
        </div>
        <div className="bg-[#111] border border-[#222] rounded-xl p-5 relative overflow-hidden">
          <div className="text-sm text-[#888] mb-1">Your Industry Rank</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-white">#3</div>
            <div className="flex items-center text-xs text-[#10b981] mb-1 bg-[#10b981]/10 px-1.5 py-0.5 rounded">
              <ArrowUpRight className="w-3 h-3 mr-0.5" />
              Up 1 Spot
            </div>
          </div>
        </div>
        <div className="bg-[#111] border border-[#222] rounded-xl p-5 relative overflow-hidden">
          <div className="text-sm text-[#888] mb-1">Fastest Growing Competitor</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-white text-[#10b981]">Rho</div>
            <div className="text-sm text-[#888] mb-1">+5.8% SOV</div>
          </div>
        </div>
      </div>

      {/* Main Chart */}
      <div className="bg-[#111] border border-[#222] rounded-xl p-6 mb-8">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-white">Share of Voice Dynamics</h3>
          <div className="flex items-center gap-2 px-2 py-1 bg-[#222] rounded text-xs text-[#ccc]">
            <span>Monthly</span>
            <ChevronDown className="w-3 h-3" />
          </div>
        </div>
        <p className="text-xs text-[#888] mb-4">Tracking market share across all major Answer Engines</p>
        <AreaChart />
      </div>

      {/* Leaderboard Table */}
      <div className="bg-[#111] border border-[#222] rounded-xl overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-[#222] flex items-center justify-between">
          <h3 className="text-sm font-medium text-white">Industry Leaderboard</h3>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#0a0a0a] border border-[#222] rounded-md text-sm text-[#ccc]">
            <Search className="w-4 h-4 text-[#666]" />
            <input type="text" placeholder="Search brands..." className="bg-transparent border-none outline-none text-white w-48 text-sm" />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-[#888] bg-[#0a0a0a] uppercase border-b border-[#222]">
              <tr>
                <th className="px-6 py-3 font-medium w-24">Rank</th>
                <th className="px-6 py-3 font-medium">Brand Name</th>
                <th className="px-6 py-3 font-medium">Global Visibility</th>
                <th className="px-6 py-3 font-medium">Share of Voice</th>
                <th className="px-6 py-3 font-medium">Total Citations</th>
                <th className="px-6 py-3 font-medium text-right">MoM Trend</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222]">
              {competitors.map((c) => (
                <tr key={c.rank} className={`hover:bg-[#1a1a1a] transition-colors group ${c.brand === 'Rho' ? 'bg-[#1a1a1a]/50' : ''}`}>
                  <td className="px-6 py-4 whitespace-nowrap text-[#888] font-medium">
                    #{c.rank}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-white font-medium flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${c.color}`}></div>
                    <div className="flex items-center justify-center w-6 h-6 rounded bg-[#222] text-[10px] text-white">
                      {c.brand.charAt(0)}
                    </div>
                    {c.brand}
                    {c.brand === 'Rho' && <span className="ml-2 px-1.5 py-0.5 rounded bg-[#222] text-[10px] text-[#ccc]">You</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-[#ccc]">{c.vis}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-[#ccc]">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-[#222] rounded-full overflow-hidden">
                        <div className={`h-full ${c.color}`} style={{ width: c.sov }}></div>
                      </div>
                      {c.sov}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-[#ccc]">{c.cit}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className={`inline-flex items-center ${c.up ? 'text-[#10b981]' : 'text-[#ef4444]'}`}>
                      {c.up ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                      {c.trend}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
