/**
 * G-Effects Tactical Display — Application Root
 *
 * Routing for the CGEM frontend. Layout chrome (Sidebar / TopBar /
 * ScanlineOverlay) lives in MainLayout.
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { MainLayout } from './components/layout';
import {
  OverviewPage,
  SimulatorPage,
  PredictionPage,
  DashboardPage,
  BatchPage,
  AnalysisPage,
  SettingsPage,
  AboutPage,
} from './pages';

const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/simulator" element={<SimulatorPage />} />
        <Route path="/prediction" element={<PredictionPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/batch" element={<BatchPage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  </BrowserRouter>
);

export default App;
