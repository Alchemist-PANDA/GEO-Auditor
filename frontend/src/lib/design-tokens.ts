/**
 * Profound Design System Tokens
 * Extracted from Phase 0 Audit
 */

export const profoundColors = {
  // Base Themes
  dark: {
    background: '#09090b', // Deep almost-black
    surface: '#18181b',    // Slightly lighter for cards/dropdowns
    border: '#27272a',     // Subtle border
    text: {
      primary: '#ffffff',
      secondary: '#a1a1aa', // Muted gray
      tertiary: '#52525b',
    }
  },
  light: {
    background: '#f8fafc', // Very subtle off-white
    surface: '#ffffff',
    border: '#e2e8f0',
    text: {
      primary: '#0f172a',
      secondary: '#64748b',
      tertiary: '#94a3b8',
    }
  },
  // Accents & State
  accent: {
    green: '#10b981', // Up arrows, positive
    red: '#ef4444',   // Down arrows, negative
    blue: '#3b82f6',  // Links, Primary action
  },
  // Chart Colors (from Explorer Donut)
  charts: {
    orange: '#f97316',
    cyan: '#06b6d4',
    purple: '#a855f7',
    green: '#22c55e',
  }
};

export const profoundTypography = {
  fontFamily: 'var(--font-sans)',
  scale: {
    xs: '0.75rem',    // 12px - Badges, subtext
    sm: '0.875rem',   // 14px - Table rows, secondary text
    base: '1rem',     // 16px - Standard text
    lg: '1.125rem',   // 18px - Card headers
    xl: '1.25rem',    // 20px - Sub-section headers
    '2xl': '1.5rem',  // 24px - Main headers
    '3xl': '1.875rem',// 30px - Large metrics
  },
  weight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  }
};

export const profoundSpacing = {
  dense: '0.25rem',    // 4px - Between icon and text
  tight: '0.5rem',     // 8px - Inside dense tables
  base: '1rem',        // 16px - Standard padding
  relaxed: '1.5rem',   // 24px - Section padding
  loose: '2rem',       // 32px - Page padding
};

// Component Styles translated to Tailwind classes
export const profoundComponents = {
  badge: {
    solid: 'px-2 py-0.5 rounded-full text-xs font-medium',
    outline: 'px-2 py-0.5 rounded-full text-xs font-medium border',
    pill: 'px-3 py-1 rounded-full text-sm font-medium',
  },
  card: {
    dark: 'bg-[#18181b] border border-[#27272a] rounded-lg',
    light: 'bg-white border border-[#e2e8f0] rounded-lg shadow-sm',
  },
  table: {
    wrapper: 'w-full text-sm text-left',
    header: 'text-xs tracking-wider text-slate-500 font-medium border-b border-border/50 pb-2',
    row: 'border-b border-border/10 hover:bg-black/5 dark:hover:bg-white/5 transition-colors',
    cell: 'py-3 px-4 align-middle',
  },
  dropdown: {
    trigger: 'flex items-center gap-2 px-3 py-1.5 text-sm rounded-md border border-border/50 bg-transparent hover:bg-black/5 dark:hover:bg-white/5 transition-colors',
    menu: 'absolute z-50 min-w-[8rem] overflow-hidden rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md',
  }
};
