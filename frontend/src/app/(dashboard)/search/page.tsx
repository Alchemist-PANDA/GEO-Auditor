'use client';

import React from 'react';
import { Search as SearchIcon, Filter, ChevronDown, Plus, BarChart, ExternalLink, Network } from 'lucide-react';

const MiniTrendBar = ({ percentage }: { percentage: string }) => {
  return (
    <div className="w-16 h-4 bg-[#f3f4f6] rounded overflow-hidden flex items-end gap-0.5 pt-1">
      {[40, 60, 30, 80, parseInt(percentage, 10), 90].map((val, i) => (
        <div key={i} className="flex-1 bg-[#3b82f6] rounded-t-sm" style={{ height: `${val}%`, opacity: 0.5 + (val / 200) }}></div>
      ))}
    </div>
  );
};

export default function SearchPage() {
  const variations = [
    { query: 'best corporate cards for startups', vol: '14,500', comp: 'High', vis: '12%', opp: '88%' },
    { query: 'brex vs ramp vs rho', vol: '8,200', comp: 'Medium', vis: '45%', opp: '55%' },
    { corporate: 'corporate card no personal guarantee', vol: '6,400', comp: 'High', vis: '5%', opp: '95%' },
    { query: 'how to manage employee expenses', vol: '12,100', comp: 'Low', vis: '8%', opp: '92%' },
    { query: 'virtual cards for business', vol: '9,800', comp: 'Medium', vis: '22%', opp: '78%' },
    { query: 'software for expense tracking', vol: '22,400', comp: 'High', vis: '2%', opp: '98%' },
    { query: 'rho corporate card reviews', vol: '3,100', comp: 'Low', vis: '98%', opp: '2%' },
    { query: 'best banks for tech startups', vol: '18,600', comp: 'High', vis: '15%', opp: '85%' },
  ].map(item => ({...item, query: item.query || item.corporate})); // handle typo in static data safely

  return (
    <div className="min-h-screen bg-[#f8fafc] text-[#0f172a] p-8 font-sans">
      
      {/* Hero Search Section */}
      <div className="max-w-4xl mx-auto mb-10 text-center mt-4">
        <h1 className="text-3xl font-semibold tracking-tight text-[#0f172a] mb-2">Prompt Discovery</h1>
        <p className="text-[#64748b] mb-8">Discover what users are asking AI Answer Engines about your industry.</p>
        
        <div className="relative max-w-2xl mx-auto flex items-center bg-white border border-[#e2e8f0] rounded-xl shadow-sm overflow-hidden focus-within:ring-2 focus-within:ring-[#3b82f6]/20 focus-within:border-[#3b82f6]">
          <SearchIcon className="w-5 h-5 text-[#94a3b8] ml-4" />
          <input 
            type="text" 
            defaultValue="business credit cards"
            className="w-full px-4 py-4 text-lg outline-none bg-transparent placeholder-[#94a3b8]" 
            placeholder="Search topics, competitors, or questions..." 
          />
          <button className="bg-[#0f172a] text-white px-6 py-4 font-medium hover:bg-[#1e293b] transition-colors">
            Analyze
          </button>
        </div>
      </div>

      {/* Discovery Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white border border-[#e2e8f0] rounded-xl p-5 shadow-sm">
          <div className="text-sm text-[#64748b] mb-1">Monthly Prompt Volume (MPV)</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-[#0f172a]">128.5K</div>
            <div className="text-sm text-[#64748b] mb-1">Total est. queries</div>
          </div>
        </div>
        <div className="bg-white border border-[#e2e8f0] rounded-xl p-5 shadow-sm">
          <div className="text-sm text-[#64748b] mb-1">Topic Competition</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-[#ef4444]">High</div>
            <div className="text-sm text-[#64748b] mb-1">94/100 difficulty</div>
          </div>
        </div>
        <div className="bg-white border border-[#e2e8f0] rounded-xl p-5 shadow-sm">
          <div className="text-sm text-[#64748b] mb-1">Visibility Opportunity</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-semibold text-[#10b981]">88%</div>
            <div className="text-sm text-[#64748b] mb-1">Uncaptured SOV</div>
          </div>
        </div>
      </div>

      {/* Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Pane: Topic Hierarchy */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="bg-white border border-[#e2e8f0] rounded-xl p-5 shadow-sm flex-1">
            <h3 className="text-sm font-semibold text-[#0f172a] mb-4 flex items-center gap-2">
              <Network className="w-4 h-4 text-[#64748b]" />
              Topic Clusters
            </h3>
            
            <div className="space-y-1">
              {['Corporate Cards', 'Expense Management', 'Startups', 'Rewards Programs', 'Virtual Cards', 'No Personal Guarantee'].map((cluster, idx) => (
                <div key={idx} className={`px-3 py-2 rounded-md text-sm cursor-pointer flex justify-between items-center ${idx === 0 ? 'bg-[#f1f5f9] text-[#0f172a] font-medium' : 'text-[#64748b] hover:bg-[#f8fafc]'}`}>
                  <span className="truncate">{cluster}</span>
                  <span className="text-xs px-1.5 py-0.5 bg-white border border-[#e2e8f0] rounded text-[#94a3b8]">{Math.floor(Math.random() * 50) + 10}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Pane: Prompt Variations */}
        <div className="lg:col-span-3 bg-white border border-[#e2e8f0] rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-[#e2e8f0] flex items-center justify-between bg-[#f8fafc]/50">
            <h3 className="text-sm font-semibold text-[#0f172a]">Prompt Variations</h3>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#e2e8f0] rounded-md text-sm text-[#64748b] cursor-pointer hover:bg-[#f8fafc]">
                <Filter className="w-4 h-4" />
                <span>Intent: All</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#e2e8f0] rounded-md text-sm text-[#64748b] cursor-pointer hover:bg-[#f8fafc]">
                <span>Sort: Volume</span>
                <ChevronDown className="w-4 h-4" />
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-[#64748b] bg-white uppercase border-b border-[#e2e8f0]">
                <tr>
                  <th className="px-6 py-3 font-medium">Prompt Query</th>
                  <th className="px-6 py-3 font-medium">Est. Volume (30d)</th>
                  <th className="px-6 py-3 font-medium">Competition</th>
                  <th className="px-6 py-3 font-medium">Current Vis</th>
                  <th className="px-6 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e2e8f0]">
                {variations.map((v, idx) => (
                  <tr key={idx} className="hover:bg-[#f8fafc] transition-colors group">
                    <td className="px-6 py-4 text-[#0f172a] font-medium max-w-[250px] truncate">
                      "{v.query}"
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-[#64748b]">
                      <div className="flex items-center gap-3">
                        {v.vol}
                        <MiniTrendBar percentage={v.opp} />
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        v.comp === 'High' ? 'bg-[#fef2f2] text-[#ef4444]' :
                        v.comp === 'Medium' ? 'bg-[#fffbeb] text-[#f59e0b]' :
                        'bg-[#ecfdf5] text-[#10b981]'
                      }`}>
                        {v.comp}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-[#64748b]">
                      <div className="flex items-center gap-2">
                        <div className="w-12 h-1.5 bg-[#f1f5f9] rounded-full overflow-hidden">
                          <div className="h-full bg-[#3b82f6]" style={{ width: v.vis }}></div>
                        </div>
                        {v.vis}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-[#e2e8f0] rounded-md text-xs font-medium text-[#0f172a] hover:bg-[#f8fafc] transition-colors shadow-sm">
                        <Plus className="w-3 h-3 text-[#64748b]" />
                        Track Topic
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="px-6 py-4 border-t border-[#e2e8f0] bg-[#f8fafc]/50 flex justify-center">
            <button className="text-sm font-medium text-[#3b82f6] hover:text-[#2563eb] transition-colors">
              Load more variations...
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
