export type RouteGroup = 'Explore' | 'Predict/Verify' | 'Compare' | 'Explain' | 'System';

export interface AppRoute {
  id: string;
  path: string;
  label: string;
  title: string;
  subtitle: string;
  group: RouteGroup;
  description: string;
  keywords: readonly string[];
  helpHash: `#${string}`;
}

export const APP_ROUTES: readonly AppRoute[] = [
  {
    id: 'overview', path: '/', label: 'Overview', title: 'G-FORCE PROFILE OVERVIEW',
    subtitle: 'Maneuver library · risk preview', group: 'Explore',
    description: 'Profile selection and G-force visualization',
    keywords: ['overview', 'profiles', 'maneuvers', 'risk'], helpHash: '#overview',
  },
  {
    id: 'simulator', path: '/simulator', label: 'Simulator', title: 'TACTICAL SIMULATOR',
    subtitle: 'Attitude · G-trace · live conformal T-LOC', group: 'Predict/Verify',
    description: 'Kinematic maneuver playback and fast prediction',
    keywords: ['simulator', 'attitude', 'g-trace', 'playback'], helpHash: '#simulator',
  },
  {
    id: 'prediction', path: '/prediction', label: 'Prediction', title: 'CGEM PREDICTION',
    subtitle: 'Conformal /predict on the trained surrogate', group: 'Predict/Verify',
    description: 'Surrogate prediction and authoritative verification',
    keywords: ['prediction', 'surrogate', 'conformal', 'verification'], helpHash: '#prediction',
  },
  {
    id: 'dashboard', path: '/dashboard', label: 'Dashboard', title: 'SCIENTIFIC DASHBOARD',
    subtitle: 'Publication-quality CGEM time-series', group: 'Predict/Verify',
    description: 'Authoritative result visualization',
    keywords: ['dashboard', 'results', 'time-series', 'physiology'], helpHash: '#dashboard',
  },
  {
    id: 'batch', path: '/batch', label: 'Batch Analysis', title: 'BATCH ANALYSIS',
    subtitle: 'Compare predictions across all maneuvers', group: 'Compare',
    description: 'Compare predictions across maneuvers',
    keywords: ['batch', 'comparison', 'maneuvers', 'predictions'], helpHash: '#batch',
  },
  {
    id: 'analysis', path: '/analysis', label: 'Analysis', title: 'PHYSIOLOGICAL ANALYSIS',
    subtitle: 'Sobol sensitivity · maneuver briefings', group: 'Explain',
    description: 'Physiological explanations and sensitivity',
    keywords: ['analysis', 'physiology', 'sobol', 'sensitivity'], helpHash: '#analysis',
  },
  {
    id: 'settings', path: '/settings', label: 'Settings', title: 'SETTINGS',
    subtitle: 'API URL · default pilot config · display', group: 'System',
    description: 'Connection and display preferences',
    keywords: ['settings', 'api', 'pilot', 'preferences'], helpHash: '#settings',
  },
  {
    id: 'about', path: '/about', label: 'About', title: 'ABOUT',
    subtitle: 'Project information and references', group: 'System',
    description: 'Limitations, provenance, and project information',
    keywords: ['about', 'limitations', 'provenance', 'references'], helpHash: '#about',
  },
];

export function routeForPath(pathname: string): AppRoute {
  return APP_ROUTES.find((route) => route.path === pathname) ?? APP_ROUTES[0];
}
