'use client';

import React from 'react';
import { Sparkles, ChevronRight, Filter, ChevronDown, ArrowUpRight, ArrowDownRight, Globe } from 'lucide-react';

// Custom SVG Radar Chart
const RadarChart = () => {
  const points1 = "150,20 250,90 210,210 90,210 50,90"; // GPT-4 (Strong)
  const points2 = "150,50 220,100 190,190 110,190 80,100"; // Perplexity
  const points3 = "150,80 190,120 170,170 130,170 110,120"; // Gemini (Weak)
  
  return (
    <div className="w-full aspect-square max-w-sm mx-auto relative flex items-center justify-center">
      <svg viewBox="0 0 300 300" className="w-full h-full overflow-visible">
        {/* Grid Background */}
        {[0.2, 0.4, 0.6, 0.8, 1].map((scale, i) => (
          <polygon 
            key={i}
            points="150,20 280,110 230,260 70,260 20,110" 
            fill="none" 
            stroke="#333" 
            strokeWidth="1"
            className="origin-center"
            style={{ transform: `scale(${scale})` }}
          />
        ))}
        {/* Axis Lines */}
        <line x1="150" y1="150" x2="150" y2="20" stroke="#333" strokeWidth="1" />
        <line x1="150" y1="150" x2="280" y2="110" stroke="#333" strokeWidth="1" />
        <line x1="150" y1="150" x2="230" y2="260" stroke="#333" strokeWidth="1" />
        <line x1="150" y1="150" x2="70" y2="260" stroke="#333" strokeWidth="1" />
        <line x1="150" y1="150" x2="20" y2="110" stroke="#333" strokeWidth="1" />

        {/* Labels */}
        <text x="150" y="10" fill="#888" fontSize="12" textAnchor="middle">Visibility</text>
        <text x="290" y="115" fill="#888" fontSize="12" textAnchor="start">Citations</text>
        <text x="240" y="275" fill="#888" fontSize="12" textAnchor="middle">Accuracy</text>
        <text x="60" y="275" fill="#888" fontSize="12" textAnchor="middle">Sentiment</text>
        <text x="10" y="115" fill="#888" fontSize="12" textAnchor="end">SOV</text>

        {/* Data Polygons */}
        <polygon points={points1} fill="rgba(16, 185, 129, 0.2)" stroke="#10b981" strokeWidth="2" />
        <polygon points={points2} fill="rgba(59, 130, 246, 0.2)" stroke="#3b82f6" strokeWidth="2" />
        <polygon points={points3} fill="rgba(239, 68, 68, 0.2)" stroke="#ef4444" strokeWidth="2" />
      </svg>
    </div>
  );
};

// Custom SVG Line Chart
const LineChart = () => {
  return (
    <div className="w-full h-[200px] mt-6 relative">
      <svg viewBox="0 0 1000 200" preserveAspectRatio="none" className="w-full h-full overflow-visible">
        {/* Grid */}
        {[0, 50, 100, 150, 200].map((y) => (
          <line key={y} x1="0" y1={y} x2="1000" y2={y} stroke="#222" strokeWidth="1" strokeDasharray="4 4" />
        ))}
        {/* Lines */}
        <path d="M0,150 C200,120 400,160 600,80 S800,40 1000,20" fill="none" stroke="#10b981" strokeWidth="2" />
        <path d="M0,180 C200,190 400,150 600,170 S800,120 1000,100" fill="none" stroke="#3b82f6" strokeWidth="2" />
        <path d="M0,190 C200,195 400,180 600,190 S800,180 1000,170" fill="none" stroke="#ef4444" strokeWidth="2" />
      </svg>
      {/* Legend inside SVG area physically */}
      <div className="absolute top-2 right-2 flex gap-4 text-xs text-[#888]">
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#10b981]"></span> GPT-4o</div>
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#3b82f6]"></span> Claude 3.5</div>
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#ef4444]"></span> Gemini 1.5</div>
      </div>
    </div>
  );
};

export default function ModelPage() {
  const models = [
    { name: 'GPT-4o', vis: '92.4%', cit: '88.1%', sov: '45.2%', sent: '0.82', trend: '+2.1%', up: true },
    { name: 'Claude 3.5 Sonnet', vis: '89.1%', cit: '85.4%', sov: '38.7%', sent: '0.78', trend: '+1.5%', up: true },
    { name: 'Perplexity Pro', vis: '76.5%', cit: '94.2%', sov: '12.4%', sent: '0.65', trend: '-0.4%', up: false },
    { name: 'Gemini 1.5 Pro', vis: '42.8%', cit: '31.5%', sov: '3.1%', sent: '0.21', trend: '-5.2%', up: false },
    { name: 'Copilot', vis: '38.2%', cit: '40.1%', sov: '0.6%', sent: '0.45', trend: '+0.1%', up: true },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      
      {/* Header & Breadcrumbs */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-2 text-sm text-[#888] mb-2">
            <span>Topics</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-white">Business Credit Cards</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-white font-medium">Model Analytics</span>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-white">Model Analysis</h1>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#111] border border-[#222] rounded-md text-sm text-[#ccc] cursor-pointer hover:bg-[#1a1a1a]">
            <span>Last 30 Days</span>
            <ChevronDown className="w-4 h-4" />
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#111] border border-[#222] rounded-md text-sm text-[#ccc] cursor-pointer hover:bg-[#1a1a1a]">
            <Globe className="w-4 h-4" />
            <span>US Region</span>
            <ChevronDown className="w-4 h-4" />
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#111] border border-[#222] rounded-md text-sm text-[#ccc] cursor-pointer hover:bg-[#1a1a1a]">
            <Filter className="w-4 h-4" />
            <span>All Intents</span>
          </div>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-[#111] border border-[#222] rounded-xl p-5">
          <div className="text-sm text-[#888] mb-1">Overall Model Consensus</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-white">67.8%</div>
            <div className="flex items-center text-xs text-[#10b981] mb-1 bg-[#10b981]/10 px-1.5 py-0.5 rounded">
              <ArrowUpRight className="w-3 h-3 mr-0.5" />
              1.2%
            </div>
          </div>
        </div>
        <div className="bg-[#111] border border-[#222] rounded-xl p-5">
          <div className="text-sm text-[#888] mb-1">Best Performing Engine</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-white">GPT-4o</div>
            <div className="text-sm text-[#888] mb-1">92.4% Vis</div>
          </div>
        </div>
        <div className="bg-[#111] border border-[#222] rounded-xl p-5">
          <div className="text-sm text-[#888] mb-1">Lowest Performing Engine</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-white text-[#ef4444]">Copilot</div>
            <div className="text-sm text-[#888] mb-1">38.2% Vis</div>
          </div>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Radar */}
        <div className="bg-[#111] border border-[#222] rounded-xl p-6 lg:col-span-1 flex flex-col">
          <h3 className="text-sm font-medium text-white mb-6">Engine Performance Matrix</h3>
          <div className="flex-1 flex items-center justify-center">
            <RadarChart />
          </div>
        </div>
        
        {/* Trend */}
        <div className="bg-[#111] border border-[#222] rounded-xl p-6 lg:col-span-2 flex flex-col">
          <h3 className="text-sm font-medium text-white mb-2">Visibility Trend by Engine</h3>
          <p className="text-xs text-[#888] mb-4">Tracking historical presence across top 3 LLMs</p>
          <div className="flex-1">
            <LineChart />
          </div>
        </div>
      </div>

      {/* Dense Data Table */}
      <div className="bg-[#111] border border-[#222] rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-[#222]">
          <h3 className="text-sm font-medium text-white">Model Comparison Matrix</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-[#888] bg-[#0a0a0a] uppercase border-b border-[#222]">
              <tr>
                <th className="px-6 py-3 font-medium">Model Engine</th>
                <th className="px-6 py-3 font-medium">Visibility Score</th>
                <th className="px-6 py-3 font-medium">Citation Rate</th>
                <th className="px-6 py-3 font-medium">Share of Voice</th>
                <th className="px-6 py-3 font-medium">Avg Sentiment</th>
                <th className="px-6 py-3 font-medium text-right">30d Trend</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222]">
              {models.map((m, idx) => (
                <tr key={idx} className="hover:bg-[#1a1a1a] transition-colors group">
                  <td className="px-6 py-4 whitespace-nowrap text-white font-medium flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-[#666] group-hover:text-white transition-colors" />
                    {m.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-[#ccc]">{m.vis}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-[#ccc]">{m.cit}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-[#ccc]">{m.sov}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-[#ccc]">{m.sent}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className={`inline-flex items-center ${m.up ? 'text-[#10b981]' : 'text-[#ef4444]'}`}>
                      {m.up ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                      {m.trend}
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
