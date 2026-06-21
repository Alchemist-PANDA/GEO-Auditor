'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, Tag, AtSign, TrendingUp,
  Globe, MessageSquare
} from 'lucide-react';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const pathname = usePathname();

  // Primary Navigation
  const mainNav = [
    { name: 'Home', href: '/dashboard', icon: Home },
    { name: 'Prompts', href: '/prompts', icon: MessageSquare },
    { name: 'Audits', href: '/audits', icon: Globe },
  ];

  // Metrics Navigation
  const metricsNav = [
    { name: 'Topic', href: '/explorer', icon: Tag },
    { name: 'Citation', href: '/citations', icon: AtSign },
    { name: 'Improve', href: '/recommendations', icon: TrendingUp },
  ];

  const renderLink = (item: any) => {
    const isActive = pathname === item.href;
    return (
      <Link
        key={item.name}
        href={item.href || '#'}
        className={cn(
          'group flex items-center gap-3 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
          isActive ? 'bg-[#18181b] text-white' : 'text-[#a1a1aa] hover:bg-[#18181b]/50 hover:text-white'
        )}
      >
        <item.icon className="w-4 h-4 flex-shrink-0" />
        <span className="truncate">{item.name}</span>
      </Link>
    );
  };

  return (
    <div className="flex h-full w-[240px] flex-col bg-[#09090b] border-r border-[#27272a]">
      {/* Header */}
      <div className="flex h-14 shrink-0 items-center justify-between px-4 mt-2">
        <div className="flex items-center gap-2 text-white font-medium cursor-pointer">
          <div className="w-5 h-5 bg-white text-black font-bold flex items-center justify-center text-xs rounded-sm">P</div>
          <span>Profound GEO</span>
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-3 py-2 custom-scrollbar">
        {/* Main Nav */}
        <div className="space-y-[2px]">
          {mainNav.map(item => renderLink(item))}
        </div>

        {/* Metrics */}
        <div className="mt-6 mb-2 px-3 text-[11px] font-semibold tracking-wider text-[#52525b] uppercase">Metrics</div>
        <div className="space-y-[2px]">
          {metricsNav.map(item => renderLink(item))}
        </div>
      </div>
    </div>
  );
}
