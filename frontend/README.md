# G-Effects Safety Dashboard - TypeScript Frontend

A modern, publication-quality TypeScript frontend for aerospace physiology visualization and G-LOC risk prediction, based on the FAA Combined G-Effects Model (CGEM).

## Features

- **Publication-Quality Visualizations**: Apache ECharts charts optimized for Q1 science journal publication standards
- **Modern UI**: Glass-morphism dark theme with smooth Framer Motion animations
- **Scientific Accuracy**: All physiological thresholds and calculations based on validated research
- **Verifiable References**: All DOI citations linked to peer-reviewed sources

### Dashboard Pages

1. **Overview**: Profile selection with G-force visualization and risk indicators
2. **Prediction**: CGEM model simulation with configurable pilot parameters
3. **Dashboard**: Scientific visualization suite with 6+ chart types
4. **Batch Analysis**: Compare physiological predictions across all profiles
5. **Analysis**: Detailed maneuver explanations with risk factors

### Chart Types

- G-Force Line Charts with physiological threshold zones
- Physiological State Heatmaps (consciousness, vision, blackout)
- Risk Assessment Radar Charts
- G-Force Distribution Histograms
- State Duration Bar Charts
- Cerebral Blood Flow Dynamics

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── charts/        # ECharts visualization components
│   │   ├── layout/        # MainLayout, Sidebar, TopBar
│   │   └── ui/            # MetricCard, ProfileSelector
│   ├── pages/             # Route pages
│   ├── services/          # Mock data service
│   ├── types/             # TypeScript type definitions
│   └── utils/             # Calculations and constants
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Technology Stack

- **React 19** with TypeScript
- **Vite 7** for fast builds and HMR
- **TailwindCSS 4** for styling
- **Apache ECharts 5** for visualizations
- **Framer Motion** for animations
- **React Router 7** for navigation
- **Lucide React** for icons

## Scientific References

All visualizations and thresholds are based on validated aerospace physiology research:

- Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow-based computer modeling of Gz-induced effects (DOT/FAA/AM-23/6). [DOI: 10.21949/1524446](https://doi.org/10.21949/1524446)
- Copeland, K. (2021). CGEM User's Guide (DOT/FAA/AM-23/5). [DOI: 10.21949/1524438](https://doi.org/10.21949/1524438)
- Whinnery, T., & Forster, E. M. (2015). Visual Neuroscience, 32, E008. [DOI: 10.1017/S095252381500005X](https://doi.org/10.1017/S095252381500005X)
- Tripp, L. D., et al. (2009). Human Factors, 51(6), 775-784. [DOI: 10.1177/0018720809359631](https://doi.org/10.1177/0018720809359631)

## Extending the Application

### Adding New Profiles

Edit `src/services/mockData.ts` to add new aerobatic profiles:

```typescript
const newProfileSamples: Sample[] = [
  { nz: 1.0, duration_ms: 1000 },
  { nz: 3.5, duration_ms: 2000 },
  // ...
];
```

### Adding New Chart Types

1. Create a new component in `src/components/charts/`
2. Use the `BaseChart` component with `ChartOption` type
3. Export from `src/components/charts/index.ts`
4. Add to the Dashboard page grid

### Customizing Physiological Thresholds

Edit `src/utils/constants.ts` to modify thresholds:

```typescript
export const PHYSIOLOGICAL_THRESHOLDS = {
  greyout_geff: 4.1,
  blackout_geff: 5.0,
  gloc_geff: 5.5,
  // ...
};
```

## Export for Publications

Charts can be exported for journal submissions:
- Use browser developer tools to save SVG
- Right-click charts for PNG export
- ECharts toolbox provides built-in export options

Recommended export settings for Q1 journals:
- Resolution: 300 DPI minimum
- Format: SVG (vector) or PNG (raster)
- Fonts: Embed or convert to paths

## License

MIT License - See repository root for details.
