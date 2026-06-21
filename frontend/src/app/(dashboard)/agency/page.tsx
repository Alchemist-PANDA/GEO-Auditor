'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function AgencyPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Agency Portal</h1>
          <p className="text-sm text-slate-400 mt-1">Manage clients and generate white-label reports</p>
        </div>
        <Badge className="bg-gradient-to-r from-violet-600 to-cyan-600 text-white border-0 px-4 py-1.5">
          Premium Feature
        </Badge>
      </div>

      {/* Coming Soon Card */}
      <Card className="bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 via-transparent to-cyan-500/5" />
        <CardContent className="relative py-24 text-center">
          <div className="relative">
            {/* Animated rings */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-32 h-32 rounded-full border border-violet-500/20 animate-ping" style={{ animationDuration: '3s' }} />
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-24 h-24 rounded-full border border-cyan-500/20 animate-ping" style={{ animationDuration: '2s', animationDelay: '0.5s' }} />
            </div>

            <div className="relative z-10">
              <div className="text-6xl mb-6">🏢</div>
              <h2 className="text-2xl font-bold text-white mb-3">Agency Dashboard</h2>
              <p className="text-slate-400 max-w-md mx-auto mb-8">
                Multi-client management, white-label reporting, and bulk GEO analysis.
                Available on the Agency tier.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                {[
                  { icon: '👥', title: 'Client Management', desc: 'Organize multiple brands and projects' },
                  { icon: '📊', title: 'White-Label Reports', desc: 'Export branded PDF reports' },
                  { icon: '🔔', title: 'Automated Alerts', desc: 'Real-time visibility notifications' },
                ].map((feature, idx) => (
                  <div key={idx} className="bg-white/5 rounded-xl p-4 border border-white/5">
                    <div className="text-2xl mb-2">{feature.icon}</div>
                    <div className="text-sm font-medium text-white mb-1">{feature.title}</div>
                    <div className="text-xs text-slate-500">{feature.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
