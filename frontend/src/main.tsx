/**
 * Application Entry Point
 *
 * Wraps the app in:
 *   - StrictMode (development-time double-render checks)
 *   - QueryClientProvider (React Query cache + retry policy for the
 *     FastAPI service at VITE_API_URL; falls back to http://localhost:8000)
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './index.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // The FastAPI service is deterministic given inputs (the lifespan
      // freezes the surrogate at boot). 5-minute stale time keeps the UI
      // snappy; a manual refetch picks up version bumps.
      staleTime: 5 * 60 * 1000,
      retry: 2,
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 8000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>
);
