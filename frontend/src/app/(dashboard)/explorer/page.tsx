"use client";

import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Globe, Search, Loader2 } from 'lucide-react';
import { fetchExplorerData, type VolumeOverview } from '@/lib/api';

const COLORS: Record<string, string> = {
  SearchGPT: '#f97316',   // Orange
  Copilot: '#22c55e',     // Green
  Perplexity: '#06b6d4',  // Cyan
  Other: '#a855f7',       // Purple
};

export default function ExplorerPage() {
  const [keyword, setKeyword] = useState('credit cards');
  const [searchInput, setSearchInput] = useState('credit cards');
  const [data, setData] = useState<VolumeOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (searchKw: string) => {
    try {
      setLoading(true);
      const res = await fetchExplorerData(searchKw);
      setData(res);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load explorer data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(keyword);
  }, [keyword]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setKeyword(searchInput.trim());
    }
  };

  // Convert platforms to pie data
  const pieData = data?.platforms 
    ? Object.entries(data.platforms).map(([name, val]) => ({
        name,
        value: parseInt(val, 10) || 0
      }))
    : [];

  const totalPieVal = pieData.reduce((acc, curr) => acc + curr.value, 0);

  // Convert geos to array
  const geoList = data?.geos
    ? Object.entries(data.geos).map(([country, volume]) => {
        const flagMap: Record<string, string> = { US: '🇺🇸', UK: '🇬🇧', DE: '🇩🇪', JP: '🇯🇵', CN: '🇨🇳', CA: '🇨🇦', AU: '🇦🇺' };
        return {
          country,
          flag: flagMap[country] || '🌍',
          volume: parseInt(volume, 10) ? `${(parseInt(volume, 10) / 1000).toFixed(1)}k` : volume,
          percent: 100
        };
      })
    : [];

  // Generate dynamic nodes coordinates around center node
  const variations = data?.variations || [];
  const centerNode = { id: 'center', text: keyword, x: 250, y: 150, r: 42, main: true };
  
  const outerNodes = variations.map((v, idx) => {
    const angle = (idx * 2 * Math.PI) / Math.max(1, variations.length);
    const radius = 100;
    return {
      id: `n-${idx}`,
      text: v.text,
      x: 250 + radius * Math.cos(angle),
      y: 150 + radius * Math.sin(angle),
      r: 30,
      main: false
    };
  });

  const nodes = [centerNode, ...outerNodes];
  const edges = outerNodes.map(n => ({ from: 'center', to: n.id }));

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      
      {/* Search Header Row */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10 pb-4 border-b border-[#27272a]/40">
        <div>
          <h1 className="text-3xl font-medium tracking-tight">Topic Explorer</h1>
          <p className="text-sm text-[#a1a1aa] mt-1">Explore LLM prompt volume and related variations for keywords</p>
        </div>
        
        <form onSubmit={handleSearchSubmit} className="flex gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 text-[#52525b] absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search keyword..." 
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#09090b] border border-[#27272a] text-white rounded-md text-sm focus:outline-none focus:border-emerald-500"
            />
          </div>
          <button 
            type="submit"
            className="px-4 py-2 bg-emerald-500 text-black hover:bg-emerald-400 font-medium text-sm rounded-md transition-colors cursor-pointer"
          >
            Explore
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-sm text-red-400 font-medium mb-8">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center p-24">
          <Loader2 className="w-8 h-8 rounded-full text-emerald-500 animate-spin" />
        </div>
      ) : !data ? (
        <div className="border border-dashed border-[#27272a]/80 rounded-2xl flex flex-col items-center justify-center p-16 bg-slate-900/10 backdrop-blur-sm text-center">
          <div className="w-12 h-12 rounded-full bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-4">
            <Search className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-white mb-1">No Explorer Data Available</h3>
          <p className="text-sm text-[#a1a1aa] max-w-sm mb-6 leading-relaxed">
            Search for a keyword above to analyze LLM prompt search volume and semantic cluster variations.
          </p>
        </div>
      ) : (
        <>
          {/* Top Section: Estimates & Global Splits */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            
            {/* Column 1: Volume Estimates */}
            <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[#a1a1aa] mb-6">Volume Estimates</h3>
              
              <div className="mb-8">
                <div className="flex items-center gap-2 text-[#a1a1aa] text-sm mb-1">
                  <span className="text-xs">📊</span> Total volume
                </div>
                <div className="text-xs text-[#52525b] mb-3">Estimated total monthly prompts using this keyword</div>
                <div className="text-4xl font-semibold tracking-tight text-white">{data.total_volume}</div>
              </div>

              <div>
                <div className="flex items-center gap-2 text-[#a1a1aa] text-sm mb-1">
                  <span className="text-xs">🎯</span> Frequency Rank
                </div>
                <div className="text-xs text-[#52525b] mb-3">Usage tier classification in public indexes</div>
                <div className="text-2xl font-medium text-emerald-400">{data.frequency_rank}</div>
              </div>
            </div>

            {/* Column 2: Platform Volume */}
            <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl flex flex-col justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[#a1a1aa] mb-4">Platform Splits</h3>
              
              <div className="relative w-full h-[160px] flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={65}
                      stroke="none"
                      dataKey="value"
                      paddingAngle={2}
                      cornerRadius={4}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#52525b'} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-semibold text-white">{data.total_volume}</span>
                  <span className="text-[10px] text-[#a1a1aa] uppercase">Total</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-y-2 gap-x-4 mt-4 px-2 text-xs">
                {pieData.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[item.name] || '#52525b' }}></div>
                      <span className="text-[#a1a1aa]">{item.name}</span>
                    </div>
                    <span className="font-semibold">{item.value.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Column 3: Global Volume */}
            <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[#a1a1aa] mb-6">Global Distributions</h3>
              <div className="space-y-3.5">
                {geoList.map((item, idx) => (
                  <div key={idx} className="flex items-center relative">
                    <div className="flex items-center gap-2 w-14">
                      <span>{item.flag}</span>
                      <span className="text-xs font-semibold">{item.country}</span>
                    </div>
                    {/* Background bar */}
                    <div className="flex-1 h-[2px] bg-[#27272a] rounded-full mx-3 relative overflow-hidden">
                       <div 
                         className="absolute top-0 left-0 h-full bg-slate-500 rounded-full"
                         style={{ width: `${item.percent}%` }}
                       />
                    </div>
                    <div className="text-xs text-[#a1a1aa] text-right w-12">{item.volume}</div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Bottom Section: Keyword Variations & Semantic Node Graph */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Variations List */}
            <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[#a1a1aa] mb-6">Keyword Variations</h3>
              <div className="flex flex-col divide-y divide-[#27272a]/30">
                {variations.map((k, idx) => (
                  <div key={idx} className="flex items-center justify-between py-3.5 group hover:bg-[#18181b]/35 -mx-4 px-4 transition-colors rounded-lg">
                    <span className="text-sm font-medium text-slate-200">{k.text}</span>
                    <span className="text-xs text-[#a1a1aa] bg-[#18181b] px-2 py-0.5 rounded-full font-semibold">{k.weight} index score</span>
                  </div>
                ))}
              </div>
            </div>

            {/* SVG Node Graph */}
            <div className="bg-[#09090b] border border-[#27272a] p-6 rounded-xl">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[#a1a1aa] mb-6">Semantic Clustering Graph</h3>
              <div className="w-full h-[320px] relative overflow-hidden rounded-lg bg-black/40 border border-[#27272a]/55">
                <svg width="100%" height="100%" viewBox="0 0 500 300" preserveAspectRatio="xMidYMid meet">
                  {/* Edges */}
                  {edges.map((edge, i) => {
                    const fromNode = nodes.find(n => n.id === edge.from)!;
                    const toNode = nodes.find(n => n.id === edge.to)!;
                    return (
                      <line 
                        key={`e-${i}`}
                        x1={fromNode.x} y1={fromNode.y}
                        x2={toNode.x} y2={toNode.y}
                        stroke="#27272a"
                        strokeWidth={1.5}
                        strokeDasharray="2 2"
                      />
                    );
                  })}
                  
                  {/* Nodes */}
                  {nodes.map((node, i) => (
                    <g key={`n-${i}`} transform={`translate(${node.x},${node.y})`}>
                      <circle 
                        r={node.r} 
                        fill={node.main ? "#10b981/10" : "#18181b"}
                        stroke={node.main ? "#10b981" : "#27272a"}
                        strokeWidth={1.5}
                        className={node.main ? "animate-pulse" : ""}
                      />
                      <text 
                        textAnchor="middle" 
                        dominantBaseline="middle" 
                        fill={node.main ? "#10b981" : "#e4e4e7"} 
                        fontSize={node.main ? "11px" : "9px"}
                        fontWeight={node.main ? "600" : "500"}
                      >
                        {node.text.split(' ').slice(0, 2).map((word, j) => (
                          <tspan key={j} x="0" dy={j === 0 ? "-0.2em" : "1.1em"}>
                            {word}
                          </tspan>
                        ))}
                      </text>
                    </g>
                  ))}
                </svg>
              </div>
            </div>
          </div>
        </>
      )}

    </div>
  );
}
