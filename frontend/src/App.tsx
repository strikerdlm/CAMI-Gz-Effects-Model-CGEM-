/**
 * G-Effects Tactical Display — Application Root
 *
 * Routing for the CGEM frontend. Layout chrome (Sidebar / TopBar /
 * ScanlineOverlay) lives in MainLayout.
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { APP_ROUTES } from './app/routes';
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

const PAGE_COMPONENTS: Record<string, React.ReactElement> = {
  overview: <OverviewPage />,
  simulator: <SimulatorPage />,
  prediction: <PredictionPage />,
  dashboard: <DashboardPage />,
  batch: <BatchPage />,
  analysis: <AnalysisPage />,
  settings: <SettingsPage />,
  about: <AboutPage />,
};

const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<MainLayout />}>
        {APP_ROUTES.map((route) => (
          <Route key={route.id} path={route.path} element={PAGE_COMPONENTS[route.id]} />
        ))}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  </BrowserRouter>
);

export default App;
