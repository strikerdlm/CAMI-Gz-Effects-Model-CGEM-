/**
 * Main Layout Component
 * 
 * Provides the overall page structure with sidebar navigation
 * and responsive content area.
 */

import React, { useEffect, useRef, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { ScanlineOverlay } from '../hud';
import { MobileNavDrawer } from './MobileNavDrawer';

export const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const location = useLocation();
  const reduceMotion = useReducedMotion();
  const navigationTriggerRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    // A route may change from browser history or another shell control while the drawer is open.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMobileNavigationOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-hud-bg relative">
      {/* CRT scanlines + slow sweep */}
      <ScanlineOverlay />

      <div data-testid="shell-background" data-shell-background>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50"
      >
        Skip to main content
      </a>
      {/* Background atmosphere */}
      <div className="fixed inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-hud-phosphor/[0.04] rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-hud-amber/[0.03] rounded-full blur-3xl" />
      </div>

      {/* Sidebar */}
      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Top Bar */}
      <TopBar
        onOpenNavigation={() => setMobileNavigationOpen(true)}
        navigationTriggerRef={navigationTriggerRef}
        sidebarCollapsed={sidebarCollapsed}
      />

      {/* Main Content Area */}
      <motion.main
        id="main-content"
        tabIndex={-1}
        initial={false}
        className={`shell-main min-h-screen ${sidebarCollapsed ? 'shell-main-collapsed' : ''}`}
      >
        {/* Page Content */}
        <div className="p-6 pt-20">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              data-page-transition
              data-motion-mode={reduceMotion ? 'reduced' : 'animated'}
              initial={reduceMotion ? false : { opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={reduceMotion ? undefined : { opacity: 0, y: -10 }}
              transition={{ duration: reduceMotion ? 0 : 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.main>
      </div>
      <MobileNavDrawer
        open={mobileNavigationOpen}
        onClose={() => setMobileNavigationOpen(false)}
        triggerRef={navigationTriggerRef}
      />
    </div>
  );
};

export default MainLayout;
