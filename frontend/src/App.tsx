/**
 * G-Effects Safety Dashboard
 * 
 * Main Application Component with Routing
 * 
 * A modern TypeScript frontend for aerospace physiology visualization
 * and G-LOC risk prediction based on the FAA CGEM model.
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { MainLayout } from './components/layout';
import {
  OverviewPage,
  PredictionPage,
  DashboardPage,
  BatchPage,
  AnalysisPage,
  AboutPage,
} from './pages';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/prediction" element={<PredictionPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/batch" element={<BatchPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/settings" element={<SettingsPlaceholder />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

// Placeholder for Settings page
const SettingsPlaceholder: React.FC = () => (
  <div className="glass rounded-2xl p-12 text-center">
    <h2 className="text-xl font-semibold text-white mb-4">Settings</h2>
    <p className="text-surface-400">
      Settings configuration coming soon. Configure themes, export options,
      and default parameters.
    </p>
  </div>
);

export default App;
