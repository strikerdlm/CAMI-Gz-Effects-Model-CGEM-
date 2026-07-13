/**
 * Profile Selector Component
 * 
 * Dropdown selector for aerobatic maneuver profiles with preview information.
 */

import React, { useMemo } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Plane, AlertTriangle, Clock, Search } from 'lucide-react';
import { cn } from '../../utils';
import { MANEUVERS_BY_ID as AEROBATIC_PROFILES } from '../../data/maneuvers';
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
  const [searchQuery, setSearchQuery] = React.useState('');
  const [activeFilter, setActiveFilter] = React.useState<'all' | 'high_g' | 'negative_g' | 'mixed'>('all');
  const dropdownRef = React.useRef<HTMLDivElement>(null);
  const menuRef = React.useRef<HTMLDivElement>(null);
  const [menuStyle, setMenuStyle] = React.useState<React.CSSProperties>({});

  const updateMenuPosition = React.useCallback(() => {
    const trigger = dropdownRef.current;
    if (!trigger) return;

    const rect = trigger.getBoundingClientRect();
    const gap = 8;
    const viewportPadding = 12;
    const spaceBelow = window.innerHeight - rect.bottom - viewportPadding;
    const spaceAbove = rect.top - viewportPadding;
    const openAbove = spaceBelow < 240 && spaceAbove > spaceBelow;
    const availableHeight = openAbove ? spaceAbove : spaceBelow;

    setMenuStyle({
      left: rect.left,
      width: rect.width,
      maxHeight: Math.max(160, Math.min(400, availableHeight - gap)),
      ...(openAbove
        ? { bottom: window.innerHeight - rect.top + gap }
        : { top: rect.bottom + gap }),
    });
  }, []);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(target) &&
        !menuRef.current?.contains(target)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setIsOpen(false);
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  React.useLayoutEffect(() => {
    if (!isOpen) return;
    updateMenuPosition();
    window.addEventListener('resize', updateMenuPosition);
    window.addEventListener('scroll', updateMenuPosition, true);
    return () => {
      window.removeEventListener('resize', updateMenuPosition);
      window.removeEventListener('scroll', updateMenuPosition, true);
    };
  }, [isOpen, updateMenuPosition]);

  const profiles = useMemo(() => Object.values(AEROBATIC_PROFILES), []);
  const selectedProfile = AEROBATIC_PROFILES[selectedProfileId];

  const formatProfileName = (profileId: string): string =>
    profileId.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());

  const classifyProfile = (
    stats: ReturnType<typeof calculateProfileStats>
  ): 'high_g' | 'negative_g' | 'mixed' => {
    if (stats.max_positive_g >= 5.5 && stats.max_negative_g <= -1.0) {
      return 'mixed';
    }
    if (stats.max_negative_g <= -1.0) {
      return 'negative_g';
    }
    return 'high_g';
  };

  const getProfileRiskLevel = (profile: AerobaticProfile): 'low' | 'medium' | 'high' => {
    const stats = calculateProfileStats(profile.samples);
    if (stats.max_positive_g > 6 || stats.max_negative_g < -2) return 'high';
    if (stats.max_positive_g > 4 || stats.max_negative_g < -1) return 'medium';
    return 'low';
  };

  const profileSummaries = useMemo(
    () =>
      profiles.map((profile) => {
        const stats = calculateProfileStats(profile.samples);
        return {
          profile,
          stats,
          riskLevel: getProfileRiskLevel(profile),
          category: classifyProfile(stats),
          displayName: formatProfileName(profile.id),
        };
      }),
    [profiles]
  );

  const filteredProfiles = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();
    return profileSummaries.filter(({ profile, displayName, category }) => {
      const matchesFilter = activeFilter === 'all' || category === activeFilter;
      if (!matchesFilter) {
        return false;
      }
      if (normalizedQuery.length === 0) {
        return true;
      }
      return (
        displayName.toLowerCase().includes(normalizedQuery) ||
        profile.description.toLowerCase().includes(normalizedQuery)
      );
    });
  }, [activeFilter, profileSummaries, searchQuery]);

  const riskColors = {
    low: 'bg-accent-500/20 text-accent-400 border-accent-500/30',
    medium: 'bg-warning-500/20 text-warning-400 border-warning-500/30',
    high: 'bg-danger-500/20 text-danger-400 border-danger-500/30',
  };

  const filterLabels = {
    all: 'All',
    high_g: '+G Focused',
    negative_g: '-G Focused',
    mixed: 'Mixed Profile',
  } as const;

  return (
    <div ref={dropdownRef} className={cn('relative', className)}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
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
                ? formatProfileName(selectedProfileId)
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
      {typeof document !== 'undefined' && createPortal(
        <AnimatePresence>
          {isOpen && (
            <motion.div
              ref={menuRef}
              role="listbox"
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              style={menuStyle}
              className={cn(
                'fixed z-[200] py-2',
                'bg-surface-900/98 backdrop-blur-xl',
                'border border-surface-700/50 rounded-xl',
                'shadow-xl shadow-black/30',
                'overflow-y-auto custom-scrollbar'
              )}
            >
            <div className="px-3 pt-2 pb-3 border-b border-surface-700/40 sticky top-0 bg-surface-900/95 backdrop-blur-xl z-10">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-surface-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  placeholder="Search maneuver..."
                  className={cn(
                    'w-full h-8 pl-9 pr-3 rounded-lg text-xs',
                    'bg-surface-800/80 border border-surface-700/60',
                    'text-surface-100 placeholder:text-surface-500',
                    'focus:outline-none focus:ring-1 focus:ring-primary-500/60 focus:border-primary-500/40'
                  )}
                />
              </div>
              <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                {Object.entries(filterLabels).map(([filterId, label]) => (
                  <button
                    key={filterId}
                    onClick={() =>
                      setActiveFilter(filterId as 'all' | 'high_g' | 'negative_g' | 'mixed')
                    }
                    className={cn(
                      'px-2.5 py-1 rounded-md text-[11px] border transition-colors',
                      activeFilter === filterId
                        ? 'bg-primary-500/20 text-primary-300 border-primary-500/35'
                        : 'bg-surface-800/70 text-surface-400 border-surface-700/60 hover:text-surface-200'
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {filteredProfiles.map(({ profile, stats, riskLevel, displayName }) => {
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
                        {displayName}
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

            {filteredProfiles.length === 0 && (
              <div className="px-4 py-6 text-center">
                <p className="text-sm text-surface-400">No profiles match your filters.</p>
                <p className="text-xs text-surface-500 mt-1">Try clearing search or selecting "All".</p>
              </div>
            )}
            </motion.div>
          )}
        </AnimatePresence>,
        document.body,
      )}
    </div>
  );
};

export default ProfileSelector;
