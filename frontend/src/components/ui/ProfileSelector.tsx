/**
 * Profile Selector Component
 * 
 * Dropdown selector for aerobatic maneuver profiles with preview information.
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Plane, AlertTriangle, Clock } from 'lucide-react';
import { cn } from '../../utils';
import { AEROBATIC_PROFILES } from '../../services/mockData';
import { calculateProfileStats } from '../../utils/calculations';
import type { AerobaticProfile } from '../../types';

interface ProfileSelectorProps {
  selectedProfileId: string;
  onSelect: (profileId: string) => void;
  className?: string;
}

export const ProfileSelector: React.FC<ProfileSelectorProps> = ({
  selectedProfileId,
  onSelect,
  className,
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const profiles = Object.values(AEROBATIC_PROFILES);
  const selectedProfile = AEROBATIC_PROFILES[selectedProfileId];

  const getProfileRiskLevel = (profile: AerobaticProfile): 'low' | 'medium' | 'high' => {
    const stats = calculateProfileStats(profile.samples);
    if (stats.max_positive_g > 6 || stats.max_negative_g < -2) return 'high';
    if (stats.max_positive_g > 4 || stats.max_negative_g < -1) return 'medium';
    return 'low';
  };

  const riskColors = {
    low: 'bg-accent-500/20 text-accent-400 border-accent-500/30',
    medium: 'bg-warning-500/20 text-warning-400 border-warning-500/30',
    high: 'bg-danger-500/20 text-danger-400 border-danger-500/30',
  };

  return (
    <div ref={dropdownRef} className={cn('relative', className)}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-full flex items-center justify-between gap-3 px-4 py-3 rounded-xl',
          'bg-surface-800/80 border border-surface-700/50',
          'hover:border-primary-500/50 hover:bg-surface-800',
          'transition-all duration-200',
          isOpen && 'border-primary-500/50 ring-2 ring-primary-500/20'
        )}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary-500/10">
            <Plane className="w-5 h-5 text-primary-400" />
          </div>
          <div className="text-left">
            <p className="font-medium text-white">
              {selectedProfile 
                ? selectedProfileId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
                : 'Select Profile'
              }
            </p>
            <p className="text-xs text-surface-400 line-clamp-1">
              {selectedProfile?.description || 'Choose an aerobatic maneuver'}
            </p>
          </div>
        </div>
        <ChevronDown
          className={cn(
            'w-5 h-5 text-surface-400 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={cn(
              'absolute z-50 w-full mt-2 py-2',
              'bg-surface-900/98 backdrop-blur-xl',
              'border border-surface-700/50 rounded-xl',
              'shadow-xl shadow-black/30',
              'max-h-[400px] overflow-y-auto custom-scrollbar'
            )}
          >
            {profiles.map((profile) => {
              const stats = calculateProfileStats(profile.samples);
              const riskLevel = getProfileRiskLevel(profile);
              const isSelected = profile.id === selectedProfileId;

              return (
                <button
                  key={profile.id}
                  onClick={() => {
                    onSelect(profile.id);
                    setIsOpen(false);
                  }}
                  className={cn(
                    'w-full px-4 py-3 text-left',
                    'hover:bg-surface-800/80 transition-colors duration-150',
                    isSelected && 'bg-primary-500/10 border-l-2 border-primary-500'
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className={cn(
                        'font-medium',
                        isSelected ? 'text-primary-400' : 'text-white'
                      )}>
                        {profile.id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </p>
                      <p className="text-xs text-surface-400 mt-0.5 line-clamp-2">
                        {profile.description}
                      </p>
                      
                      {/* Quick stats */}
                      <div className="flex items-center gap-3 mt-2">
                        <span className="flex items-center gap-1 text-xs text-surface-500">
                          <Clock className="w-3 h-3" />
                          {stats.total_duration_s.toFixed(1)}s
                        </span>
                        <span className="text-xs text-surface-500">
                          Max: {stats.max_positive_g > 0 ? '+' : ''}{stats.max_positive_g.toFixed(1)}G
                        </span>
                        {stats.max_negative_g < 0 && (
                          <span className="text-xs text-surface-500">
                            Min: {stats.max_negative_g.toFixed(1)}G
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Risk Badge */}
                    <div className={cn(
                      'flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium border',
                      riskColors[riskLevel]
                    )}>
                      {riskLevel === 'high' && <AlertTriangle className="w-3 h-3" />}
                      {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)}
                    </div>
                  </div>
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProfileSelector;
