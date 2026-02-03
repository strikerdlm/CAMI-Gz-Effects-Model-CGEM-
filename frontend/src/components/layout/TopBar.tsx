/**
 * Top Bar Component
 * 
 * Header with profile selector, status indicators, and quick actions.
 */

import React from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Bell,
  Search,
  Download,
  RefreshCw,
  Moon,
  Sun,
  HelpCircle,
} from 'lucide-react';
import { cn } from '../../utils';

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/': {
    title: 'G-Force Profile Overview',
    subtitle: 'Select and visualize aerobatic maneuver profiles',
  },
  '/prediction': {
    title: 'CGEM Prediction',
    subtitle: 'Configure pilot parameters and run physiological simulation',
  },
  '/dashboard': {
    title: 'Scientific Dashboard',
    subtitle: 'Publication-quality ECharts visualizations',
  },
  '/batch': {
    title: 'Batch Analysis',
    subtitle: 'Compare physiological predictions across all profiles',
  },
  '/analysis': {
    title: 'Physiological Analysis',
    subtitle: 'Detailed maneuver explanations and risk factors',
  },
  '/settings': {
    title: 'Settings',
    subtitle: 'Configure application preferences',
  },
  '/about': {
    title: 'About',
    subtitle: 'Project information and references',
  },
};

export const TopBar: React.FC = () => {
  const location = useLocation();
  const pageInfo = PAGE_TITLES[location.pathname] || {
    title: 'G-Effects Dashboard',
    subtitle: 'Aerospace safety management',
  };

  const [isDarkMode, setIsDarkMode] = React.useState(true);

  return (
    <header
      className={cn(
        'fixed top-0 right-0 z-30 h-16',
        'bg-surface-950/80 backdrop-blur-xl',
        'border-b border-surface-800/50',
        'flex items-center justify-between px-6',
        'transition-all duration-300'
      )}
      style={{ left: 'inherit' }}
    >
      {/* Left: Page Title */}
      <div className="flex items-center gap-4">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          <h1 className="text-lg font-semibold text-white">{pageInfo.title}</h1>
          <p className="text-xs text-surface-400">{pageInfo.subtitle}</p>
        </motion.div>
      </div>

      {/* Center: Search */}
      <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-surface-500" />
          <input
            type="text"
            placeholder="Search profiles, parameters..."
            className={cn(
              'w-full pl-10 pr-4 py-2 rounded-xl',
              'bg-surface-800/60 border border-surface-700/50',
              'text-surface-200 placeholder:text-surface-500',
              'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50',
              'transition-all duration-200'
            )}
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Status indicator */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent-500/10 border border-accent-500/20">
          <div className="w-2 h-2 rounded-full bg-accent-500 animate-pulse" />
          <span className="text-xs font-medium text-accent-400">Model Ready</span>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-1 ml-2">
          <button
            className={cn(
              'p-2 rounded-lg transition-all duration-200',
              'text-surface-400 hover:text-white hover:bg-surface-800'
            )}
            title="Refresh data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            className={cn(
              'p-2 rounded-lg transition-all duration-200',
              'text-surface-400 hover:text-white hover:bg-surface-800'
            )}
            title="Export"
          >
            <Download className="w-4 h-4" />
          </button>

          <button
            className={cn(
              'p-2 rounded-lg transition-all duration-200',
              'text-surface-400 hover:text-white hover:bg-surface-800'
            )}
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
          </button>

          <button
            className={cn(
              'p-2 rounded-lg transition-all duration-200',
              'text-surface-400 hover:text-white hover:bg-surface-800'
            )}
            title="Help"
          >
            <HelpCircle className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={cn(
              'p-2 rounded-lg transition-all duration-200',
              'text-surface-400 hover:text-white hover:bg-surface-800'
            )}
            title={isDarkMode ? 'Light mode' : 'Dark mode'}
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* User avatar */}
        <div className="ml-2 pl-2 border-l border-surface-700">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-semibold text-sm">
            DM
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
