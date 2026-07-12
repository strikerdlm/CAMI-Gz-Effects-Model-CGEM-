/**
 * Sidebar Navigation Component
 * 
 * Modern glass-morphism sidebar with navigation links for the safety dashboard.
 */

import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Activity,
  Settings,
  BarChart3,
  Play,
  FileText,
  Info,
  Plane,
  Zap,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { cn } from '../../utils';
import { APP_ROUTES } from '../../app/routes';

const ROUTE_ICONS: Record<string, React.ElementType> = {
  overview: LayoutDashboard,
  simulator: Plane,
  prediction: Play,
  dashboard: BarChart3,
  batch: Activity,
  analysis: FileText,
  settings: Settings,
  about: Info,
};

const NAV_ITEMS = APP_ROUTES.filter((route) => route.group !== 'System');
const SECONDARY_ITEMS = APP_ROUTES.filter((route) => route.group === 'System');

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggle }) => {
  const location = useLocation();

  return (
    <motion.aside
      initial={false}
      animate={{ width: isCollapsed ? 72 : 260 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className={cn(
        'fixed left-0 top-0 h-screen z-40',
        'bg-surface-950/95 backdrop-blur-xl',
        'border-r border-surface-800/50',
        'flex flex-col',
        'shadow-xl shadow-black/20'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-surface-800/50">
        <motion.div
          initial={false}
          animate={{ opacity: isCollapsed ? 0 : 1, width: isCollapsed ? 0 : 'auto' }}
          className="flex items-center gap-3 overflow-hidden"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/30">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div className="whitespace-nowrap">
            <h1 className="text-lg font-bold text-white">G-Effects</h1>
            <p className="text-xs text-surface-400">Safety Dashboard</p>
          </div>
        </motion.div>

        <button
          onClick={onToggle}
          aria-label={isCollapsed ? 'Expand navigation' : 'Collapse navigation'}
          className={cn(
            'p-2 rounded-lg transition-all duration-200',
            'hover:bg-surface-800 text-surface-400 hover:text-white',
            isCollapsed && 'mx-auto'
          )}
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Main Navigation */}
      <nav aria-label="Primary" className="flex-1 p-3 space-y-1 overflow-y-auto custom-scrollbar">
        <div className={cn('mb-2', !isCollapsed && 'px-3')}>
          {!isCollapsed && (
            <span className="text-xs font-semibold text-surface-500 uppercase tracking-wider">
              Main
            </span>
          )}
        </div>

        {NAV_ITEMS.map((item) => {
          const Icon = ROUTE_ICONS[item.id];
          return (
          <NavLink
            key={item.id}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200',
                'text-surface-400 hover:text-white',
                isActive
                  ? 'bg-primary-500/15 text-primary-400 border border-primary-500/30'
                  : 'hover:bg-surface-800/80',
                isCollapsed && 'justify-center px-2'
              )
            }
          >
            <Icon
              className={cn(
                'w-5 h-5 flex-shrink-0 transition-transform duration-200',
                'group-hover:scale-110'
              )}
            />
            {!isCollapsed && (
              <motion.span
                initial={false}
                animate={{ opacity: isCollapsed ? 0 : 1 }}
                className="font-medium whitespace-nowrap"
              >
                {item.label}
              </motion.span>
            )}
            
            {/* Active indicator */}
            {location.pathname === item.path && !isCollapsed && (
              <motion.div
                layoutId="activeNav"
                className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400"
              />
            )}
          </NavLink>
          );
        })}

        {/* Secondary Navigation */}
        <div className={cn('mt-6 mb-2', !isCollapsed && 'px-3')}>
          {!isCollapsed && (
            <span className="text-xs font-semibold text-surface-500 uppercase tracking-wider">
              Settings
            </span>
          )}
        </div>

        {SECONDARY_ITEMS.map((item) => {
          const Icon = ROUTE_ICONS[item.id];
          return (
          <NavLink
            key={item.id}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200',
                'text-surface-400 hover:text-white',
                isActive
                  ? 'bg-surface-800 text-white'
                  : 'hover:bg-surface-800/60',
                isCollapsed && 'justify-center px-2'
              )
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && (
              <span className="font-medium whitespace-nowrap">{item.label}</span>
            )}
          </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-surface-800/50">
        {!isCollapsed ? (
          <div className="px-2">
            <div className="text-xs text-surface-500">
              <p className="font-medium text-surface-400">CGEM v1.1.0.1</p>
              <p>FAA Civil Aerospace Medical Institute</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-2 h-2 rounded-full bg-accent-500 animate-pulse" />
          </div>
        )}
      </div>
    </motion.aside>
  );
};

export default Sidebar;
