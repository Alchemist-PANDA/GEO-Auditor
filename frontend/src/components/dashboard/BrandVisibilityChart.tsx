import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export interface HistoryPoint {
  date: string;
  score: number;
}

export const BrandVisibilityChart = ({ data }: { data: HistoryPoint[] }) => {
  return (
    <div className="w-full h-80 bg-card rounded-xl border border-border p-6 shadow-glow flex flex-col">
      <div className="mb-4">
        <h3 className="text-sm font-medium text-brand-muted">Brand visibility score</h3>
        <p className="text-2xl font-bold text-foreground mt-1">42% <span className="text-sm font-medium text-green-500">+5%</span></p>
      </div>
      <div className="flex-1 min-h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="gradientColor" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis dataKey="date" stroke="#4b5563" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#4b5563" fontSize={11} tickLine={false} axisLine={false} domain={[0, 100]} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#050505', borderColor: '#222', borderRadius: '8px' }} 
              labelStyle={{ color: '#9ca3af' }}
              itemStyle={{ color: '#fff' }}
            />
            <Area 
              type="monotone" 
              dataKey="score" 
              stroke="#22c55e" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#gradientColor)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
