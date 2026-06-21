import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

export interface RankingItem {
  rank: number;
  brand: string;
  score: number;
  trend: 'up' | 'down' | 'flat';
  change: number;
}

export const BrandIndustryRankingTable = ({ data }: { data: RankingItem[] }) => {
  return (
    <div className="w-full bg-card rounded-xl border border-border p-6 shadow-glow">
      <h3 className="text-sm font-medium text-brand-muted mb-4">Industry Leaderboard</h3>
      <Table>
        <TableHeader>
          <TableRow className="border-border hover:bg-transparent">
            <TableHead className="w-16 text-brand-muted">Rank</TableHead>
            <TableHead className="text-brand-muted">Brand</TableHead>
            <TableHead className="text-right text-brand-muted">Score</TableHead>
            <TableHead className="text-right text-brand-muted">7d Change</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item) => (
            <TableRow key={item.brand} className="border-border hover:bg-[#111111]">
              <TableCell className="font-medium text-foreground">{item.rank}</TableCell>
              <TableCell className="font-medium text-foreground">{item.brand}</TableCell>
              <TableCell className="text-right font-bold text-foreground">{item.score}%</TableCell>
              <TableCell className="text-right">
                <Badge 
                  variant="outline" 
                  className={
                    item.trend === 'up' ? 'text-green-500 border-green-500/20 bg-green-500/10' : 
                    item.trend === 'down' ? 'text-red-500 border-red-500/20 bg-red-500/10' : 
                    'text-gray-500 border-gray-500/20 bg-gray-500/10'
                  }
                >
                  {item.trend === 'up' ? '+' : item.trend === 'down' ? '-' : ''}{Math.abs(item.change)}%
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
