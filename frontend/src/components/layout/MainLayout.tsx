/**
 * Main Layout Component
 * 
 * Provides the overall page structure with sidebar navigation
 * and responsive content area.
 */

import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { ScanlineOverlay } from '../hud';

export const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();

  if (location.pathname === '/simulator') return <div className="flight-app-shell"><nav className="flight-app-navigation" aria-label="Application navigation"><Link to="/" className="flight-app-brand">CGEM<span>G-EFFECTS MODEL</span></Link><div><Link to="/simulator" aria-current="page">Learning lab</Link><Link to="/dashboard">Scientific dashboard</Link><Link to="/settings">Settings</Link></div><span className="flight-app-credit">CIVIL AEROSPACE MEDICAL INSTITUTE</span></nav><Outlet /></div>;

  return (
    <div className="min-h-screen bg-hud-bg relative">
      {/* CRT scanlines + slow sweep */}
      <ScanlineOverlay />

      {/* Background atmosphere */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-hud-phosphor/[0.04] rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-hud-amber/[0.03] rounded-full blur-3xl" />
      </div>

      {/* Sidebar */}
      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Area */}
      <motion.main
        initial={false}
        animate={{
          marginLeft: sidebarCollapsed ? 72 : 260,
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="min-h-screen"
      >
        {/* Top Bar */}
        <TopBar />

        {/* Page Content */}
        <div className="p-6 pt-20">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.main>
    </div>
  );
};

export default MainLayout;
