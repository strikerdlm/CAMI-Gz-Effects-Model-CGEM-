/**
 * Metric Card Component
 * 
 * Displays a single metric with optional delta/trend indicator.
 * Designed for physiological measurements and safety metrics.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '../../utils';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  color?: 'default' | 'primary' | 'accent' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const colorStyles = {
  default: 'border-surface-700/50',
  primary: 'border-primary-500/30 bg-primary-500/5',
  accent: 'border-accent-500/30 bg-accent-500/5',
  warning: 'border-warning-500/30 bg-warning-500/5',
  danger: 'border-danger-500/30 bg-danger-500/5',
};

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
};

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  delta,
  deltaType = 'neutral',
  icon,
  trend,
  color = 'default',
  size = 'md',
  className,
}) => {
  const TrendIcon = trend ? trendIcons[trend] : null;

  const sizeStyles = {
    sm: { card: 'p-3', value: 'text-xl', label: 'text-xs' },
    md: { card: 'p-4', value: 'text-2xl', label: 'text-sm' },
    lg: { card: 'p-5', value: 'text-3xl', label: 'text-base' },
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'metric-card',
        colorStyles[color],
        sizeStyles[size].card,
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className={cn('metric-label mb-1', sizeStyles[size].label)}>
            {label}
          </p>
          <div className="flex items-baseline gap-1">
            <span className={cn('metric-value', sizeStyles[size].value)}>
              {value}
            </span>
            {unit && (
              <span className="text-surface-400 text-sm font-medium">
                {unit}
              </span>
            )}
          </div>
          
          {delta && (
            <div className="flex items-center gap-1 mt-2">
              {TrendIcon && (
                <TrendIcon
                  className={cn(
                    'w-3 h-3',
                    deltaType === 'positive' && 'text-accent-400',
                    deltaType === 'negative' && 'text-danger-400',
                    deltaType === 'neutral' && 'text-surface-400'
                  )}
                />
              )}
              <span
                className={cn(
                  'text-xs font-medium',
                  deltaType === 'positive' && 'text-accent-400',
                  deltaType === 'negative' && 'text-danger-400',
                  deltaType === 'neutral' && 'text-surface-400'
                )}
              >
                {delta}
              </span>
            </div>
          )}
        </div>

        {icon && (
          <div className="p-2 rounded-lg bg-surface-800/50">
            {icon}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default MetricCard;
