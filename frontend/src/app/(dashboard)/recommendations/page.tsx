'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { useGeoStore } from '@/store/geoStore';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { generateRecommendations, generateAdvancedRecommendations } from '@/lib/api';

const PRIORITY_CONFIG: Record<string, { color: string; bg: string; border: string }> = {
  CRITICAL: { color: 'text-red-400', bg: 'bg-red-500/20', border: 'border-red-500/30' },
  HIGH: { color: 'text-orange-400', bg: 'bg-orange-500/20', border: 'border-orange-500/30' },
  MEDIUM: { color: 'text-blue-400', bg: 'bg-blue-500/20', border: 'border-blue-500/30' },
  LOW: { color: 'text-slate-400', bg: 'bg-slate-500/20', border: 'border-slate-500/30' },
};

export default function RecommendationsPage() {
  const { recommendations, isLoading, loadRecommendations } = useGeoStore();
  const { currentProjectId } = useWorkspaceStore();
  const [filter, setFilter] = useState('All');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadRecommendations(currentProjectId || 'demo-project');
  }, [currentProjectId, loadRecommendations]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await generateRecommendations(currentProjectId || 'demo-project');
      loadRecommendations(currentProjectId || 'demo-project');
    } catch { /* silent */ }
    setGenerating(false);
  };

  const handleAdvanced = async () => {
    setGenerating(true);
    try {
      await generateAdvancedRecommendations(currentProjectId || 'demo-project');
      loadRecommendations(currentProjectId || 'demo-project');
    } catch { /* silent */ }
    setGenerating(false);
  };

  const filters = ['All', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const filtered = filter === 'All'
    ? recommendations
    : recommendations.filter(r => r.priority === filter);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Recommendations</h1>
          <p className="text-sm text-slate-400 mt-1">AI-powered GEO optimization suggestions</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={handleGenerate}
            disabled={generating}
            variant="outline"
            className="border-white/10 text-slate-300 hover:bg-white/5"
          >
            {generating ? '⟳ Generating...' : '🔄 Rule-Based'}
          </Button>
          <Button
            onClick={handleAdvanced}
            disabled={generating}
            className="bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white"
          >
            ✨ Advanced (LLM)
          </Button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {filters.map(f => (
          <Button
            key={f}
            variant={filter === f ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter(f)}
            className={filter === f
              ? 'bg-violet-600 text-white'
              : 'border-white/10 text-slate-400 hover:bg-white/5'}
          >
            {f}
            {f !== 'All' && (
              <span className="ml-1 text-xs opacity-60">
                ({recommendations.filter(r => r.priority === f).length})
              </span>
            )}
          </Button>
        ))}
      </div>

      {/* Recommendation Cards */}
      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-40 rounded-xl bg-white/5 border border-white/10" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="border border-dashed border-[#27272a]/80 rounded-2xl flex flex-col items-center justify-center p-16 bg-slate-900/10 backdrop-blur-sm text-center">
          <div className="w-12 h-12 rounded-full bg-violet-500/10 text-violet-400 flex items-center justify-center mb-4">
            <span className="text-2xl">💡</span>
          </div>
          <h3 className="text-base font-semibold text-white mb-1">No Recommendations Yet</h3>
          <p className="text-sm text-[#a1a1aa] max-w-sm mb-6 leading-relaxed">
            Click &ldquo;Rule-Based&rdquo; or &ldquo;Advanced (LLM)&rdquo; above to generate actionable optimization tasks.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map(rec => {
            const pri = PRIORITY_CONFIG[rec.priority] || PRIORITY_CONFIG.MEDIUM;
            return (
              <Card key={rec.id} className="bg-white/5 backdrop-blur-xl border border-white/10 hover:border-white/20 transition-all duration-300 group">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <Badge className={`${pri.bg} ${pri.color} ${pri.border}`}>
                        {rec.priority}
                      </Badge>
                      <Badge variant="outline" className="border-white/10 text-slate-400">
                        {rec.status}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-500">Est. Visibility Gain</div>
                      <div className="text-sm font-bold text-emerald-400">+{rec.estimated_visibility_gain}%</div>
                    </div>
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-violet-300 transition-colors">
                    {rec.title}
                  </h3>
                  <p className="text-sm text-slate-400 mb-4">{rec.description}</p>

                  {/* Visibility Gain Progress */}
                  <div className="mb-4">
                    <Progress
                      value={Math.min(rec.estimated_visibility_gain * 30, 100)}
                      className="h-1.5 bg-white/10"
                    />
                  </div>

                  {/* Action Items */}
                  {rec.actions && rec.actions.length > 0 && (
                    <div className="space-y-2 border-t border-white/5 pt-3">
                      <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Action Items</div>
                      {rec.actions.map(action => (
                        <div key={action.id} className="flex items-start gap-2">
                          <Checkbox
                            checked={action.is_completed}
                            className="mt-0.5 border-white/20"
                          />
                          <span className={`text-sm ${action.is_completed ? 'text-slate-500 line-through' : 'text-slate-300'}`}>
                            {action.action_text}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
