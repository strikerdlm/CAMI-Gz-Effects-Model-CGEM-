# CGEM Frontend Aviation Revamp — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the three frontend gaps (mock-only Dashboard, placeholder Settings, unused health hooks), add a new `/simulator` page that plays the 71 archived aerobatic G-traces against the live FastAPI `/predict` and `/run-cgem` endpoints, and re-skin the entire app in an MFD/HUD cockpit aesthetic — then ship it to the community on `main`.

**Architecture:** Pure-frontend change for the user-visible surface; one Python build-time script (`scripts/export_maneuvers_json.py`) joins `maneuvers_catalog.CATALOG` with the txt files in `Aerobatics_sample_inputs/` and writes `frontend/src/data/maneuvers.json` (71 entries with G-trace samples + Aresti / hemodynamic metadata). Frontend ingests that JSON, retires `services/mockData.ts` as the primary data source, and wires every page to the existing `cgemApi.ts` hooks. The HUD aesthetic lives in design tokens (CSS variables + Tailwind theme extension) and a new `components/hud/` primitive set; no backend / contract change.

**Tech Stack:** React 19, TypeScript 5.9, Vite 7, Tailwind v4, ECharts 5.6 (existing), Framer Motion 12 (existing), `@tanstack/react-query` 5 (existing), IBM Plex Sans + IBM Plex Mono (Google Fonts), `axios` + `localStorage` for the configurable API URL. Backend untouched.

---

## File Structure

**Create**

| Path | Responsibility |
|---|---|
| `scripts/export_maneuvers_json.py` | Parse `maneuvers_catalog.CATALOG` + `Aerobatics_sample_inputs/*.txt` → `frontend/src/data/maneuvers.json`. |
| `frontend/src/data/maneuvers.json` | Build-time output: array of 71 maneuver records with `samples[]`, `g_peak`, `dgdt_max`, `category`, `aresti_family`, `hemodynamic_concern`. |
| `frontend/src/data/maneuvers.ts` | Typed import wrapper around `maneuvers.json` + grouping helpers. |
| `frontend/src/components/hud/Bezel.tsx` | Instrument-bezel container (border + corner notches + label strip). |
| `frontend/src/components/hud/SegmentReadout.tsx` | Phosphor-style numeric readout. |
| `frontend/src/components/hud/RiskBadge.tsx` | OOD / risk-tier badge (CLEAR / CAUTION / G-LOC). |
| `frontend/src/components/hud/StatusStrip.tsx` | Top-of-page status line (mode, frame, time). |
| `frontend/src/components/hud/ScanlineOverlay.tsx` | Subtle CRT scanline overlay (CSS-only). |
| `frontend/src/components/hud/AttitudeIndicator.tsx` | SVG roll/pitch dial driven by integrated G-trace. |
| `frontend/src/components/hud/GTracePlayer.tsx` | Animated G-trace player with playhead + conformal band. |
| `frontend/src/components/hud/index.ts` | Re-exports. |
| `frontend/src/pages/SimulatorPage.tsx` | `/simulator` route — maneuver picker + attitude + G-trace + live prediction. |
| `frontend/src/pages/SettingsPage.tsx` | Real `/settings` route (replaces `SettingsPlaceholder`). |
| `frontend/src/state/useUserPrefs.ts` | Zustand-less hook: localStorage-backed preferences (API URL, phosphor color, default countermeasures, units). |

**Modify**

| Path | What changes |
|---|---|
| `frontend/index.html` | Add IBM Plex Sans + IBM Plex Mono Google Fonts link; update `<title>`. |
| `frontend/tailwind.config.js` | Extend theme with HUD palette + monospace font stack. |
| `frontend/src/index.css` | Replace existing CSS variables with HUD tokens (`--hud-bg`, `--hud-amber`, `--hud-green`, etc.); add `.bezel`, `.scanlines`, `.grid-bg` utilities. |
| `frontend/src/App.tsx` | Add `/simulator` route; replace `SettingsPlaceholder` with `<SettingsPage />`; reorder sidebar entries. |
| `frontend/src/components/layout/Sidebar.tsx` | Add Simulator nav entry with icon; restyle to bezel look. |
| `frontend/src/components/layout/TopBar.tsx` | Wire `useHealth` + `useVersion`; render pulsing connection LED, version, callsign chrome. |
| `frontend/src/components/layout/MainLayout.tsx` | Add `<ScanlineOverlay />` and grid background. |
| `frontend/src/services/cgemApi.ts` | Read base URL from `useUserPrefs` localStorage (fallback to env var, then default). |
| `frontend/src/services/mockData.ts` | Re-export `AEROBATIC_PROFILES` as a thin shim over `data/maneuvers.ts` (so legacy pages still compile while we migrate). |
| `frontend/src/pages/DashboardPage.tsx` | Replace `simulateCGEMResult` with `useRunCgem` call; gracefully degrade to mock only when `useHealth` reports `down`. |
| `frontend/src/pages/OverviewPage.tsx` | Replace `AEROBATIC_PROFILES` import with `maneuvers.ts`; add "Open in Simulator" CTA. |
| `frontend/src/pages/AnalysisPage.tsx` | Use `maneuvers.ts` for the picker (already wired to `/sensitivity`). |
| `frontend/src/pages/PredictionPage.tsx` | Use `maneuvers.ts` for the picker (already wired to `/predict`). |
| `frontend/src/pages/BatchPage.tsx` | Use `maneuvers.ts` for the picker (already wired to `/sweep`). |
| `frontend/src/pages/index.ts` | Export `SimulatorPage`, `SettingsPage`. |
| `frontend/package.json` | Add `prebuild` script that runs the Python exporter. |

**Delete:** none. `mockData.ts` stays as a compatibility shim so we can land in stages.

---

## Task 1 — Pre-flight: clean tree, deps installed

**Files:** none modified.

- [ ] **Step 1: Verify clean working tree on `main`.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
git status --short
git branch --show-current
```

Expected: branch = `main`; only `.playwright-mcp/` untracked (from prior session).

- [ ] **Step 2: Install frontend deps so type-check / build can run.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm install --no-audit --no-fund
```

Expected: completes without error; `node_modules/.bin/tsc` and `node_modules/.bin/vite` now exist.

- [ ] **Step 3: Baseline build before any changes.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
```

Expected: both succeed. This is the "green baseline" to compare regressions against.

---

## Task 2 — Build-time maneuver export

**Files:**
- Create: `scripts/export_maneuvers_json.py`
- Create: `frontend/src/data/maneuvers.json` (build artifact, committed)
- Create: `frontend/src/data/maneuvers.ts` (typed wrapper)
- Modify: `frontend/package.json` (add `prebuild` script)

- [ ] **Step 1: Write the exporter.**

```python
# scripts/export_maneuvers_json.py
"""Export `maneuvers_catalog.CATALOG` + Aerobatics_sample_inputs/*.txt
to a single JSON manifest consumed by the frontend at build time."""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from maneuvers_catalog import CATALOG  # noqa: E402

INPUTS_DIR = REPO_ROOT / "Aerobatics_sample_inputs"
OUTPUT = REPO_ROOT / "frontend" / "src" / "data" / "maneuvers.json"


def parse_txt(path: Path) -> list[dict[str, float]]:
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    if not lines:
        return []
    # First line is segment count; ignore — trust the row count.
    samples: list[dict[str, float]] = []
    for ln in lines[1:]:
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) != 2:
            continue
        try:
            nz = float(parts[0])
            dur_ms = float(parts[1])
        except ValueError:
            continue
        samples.append({"nz": nz, "duration_ms": dur_ms})
    return samples


def main() -> None:
    records: list[dict] = []
    for identifier, meta in sorted(CATALOG.items()):
        # filename guess: most txt files match identifier, a few use camelCase.
        candidates = [
            INPUTS_DIR / f"{identifier}.txt",
            INPUTS_DIR / f"{identifier.replace('_', '')}.txt",
        ]
        samples: list[dict[str, float]] = []
        filename = ""
        for c in candidates:
            if c.exists():
                samples = parse_txt(c)
                filename = c.name
                break
        records.append({
            "id": meta.identifier,
            "filename": filename,
            "category": meta.category.value,
            "description": meta.description,
            "aircraft": meta.aircraft,
            "peak_pos_gz": meta.peak_pos_gz,
            "peak_neg_gz": meta.peak_neg_gz,
            "onset_rate_g_per_s": meta.onset_rate_g_per_s,
            "total_duration_s": meta.total_duration_s,
            "aresti_family": meta.aresti_family,
            "aresti_code": meta.aresti_code,
            "sustained_gz": meta.sustained_gz,
            "sustained_duration_s": meta.sustained_duration_s,
            "hemodynamic_concern": meta.hemodynamic_concern,
            "source": meta.source,
            "tags": list(meta.tags),
            "samples": samples,
        })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"wrote {len(records)} maneuvers to {OUTPUT}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run exporter, verify 71-ish records and non-empty samples.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
python3 scripts/export_maneuvers_json.py
python3 -c "import json; d = json.load(open('frontend/src/data/maneuvers.json')); print(len(d), 'with samples:', sum(1 for r in d if r['samples']))"
```

Expected: `71 with samples: >=60`. Some catalog entries (extreme post-stall conceptual) may not have a `.txt` file — that's OK as long as the majority do.

- [ ] **Step 3: Write typed TS wrapper.**

```typescript
// frontend/src/data/maneuvers.ts
import raw from './maneuvers.json';

export type ManeuverCategory =
  | 'championship'
  | 'military_acm'
  | 'extreme_post_stall'
  | 'training'
  | 'conceptual';

export interface ManeuverSample {
  nz: number;
  duration_ms: number;
}

export interface Maneuver {
  id: string;
  filename: string;
  category: ManeuverCategory;
  description: string;
  aircraft: string;
  peak_pos_gz: number;
  peak_neg_gz: number;
  onset_rate_g_per_s: number;
  total_duration_s: number;
  aresti_family: number | null;
  aresti_code: string | null;
  sustained_gz: number | null;
  sustained_duration_s: number | null;
  hemodynamic_concern: string;
  source: string;
  tags: string[];
  samples: ManeuverSample[];
}

export const MANEUVERS: Maneuver[] = raw as Maneuver[];

export const MANEUVERS_BY_ID: Record<string, Maneuver> = Object.fromEntries(
  MANEUVERS.map((m) => [m.id, m]),
);

export const MANEUVERS_BY_CATEGORY: Record<ManeuverCategory, Maneuver[]> = MANEUVERS.reduce(
  (acc, m) => {
    (acc[m.category] ||= []).push(m);
    return acc;
  },
  {} as Record<ManeuverCategory, Maneuver[]>,
);

export function flightTimeSeconds(m: Maneuver): number[] {
  let t = 0;
  return m.samples.map((s) => {
    t += s.duration_ms / 1000;
    return t;
  });
}
```

- [ ] **Step 4: Add prebuild hook.**

In `frontend/package.json`, add inside `"scripts"`:

```json
"prebuild": "cd .. && python3 scripts/export_maneuvers_json.py"
```

- [ ] **Step 5: Verify TypeScript can import the JSON.**

Add to `frontend/tsconfig.app.json` (if not present in `compilerOptions`):

```json
"resolveJsonModule": true,
```

(It likely is already on; only add if missing.)

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check
```

Expected: PASS.

- [ ] **Step 6: Commit.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
git add scripts/export_maneuvers_json.py frontend/src/data/ frontend/package.json frontend/tsconfig.app.json
git commit -m "feat(frontend): export 71 maneuvers + Aresti metadata to JSON at build time"
```

(No `Co-Authored-By` — repo policy: Diego is sole author.)

---

## Task 3 — HUD design tokens, fonts, global CSS

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/tailwind.config.js`
- Modify: `frontend/src/index.css`

- [ ] **Step 1: Add IBM Plex fonts.**

In `frontend/index.html`, inside `<head>` (above `<title>`):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Sans+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
```

Also update title:

```html
<title>CGEM · G-Effects Tactical Display</title>
```

- [ ] **Step 2: Extend Tailwind theme.**

Replace `frontend/tailwind.config.js` contents with:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        hud: {
          bg: '#0a0e0c',
          panel: '#10171a',
          'panel-2': '#0d1316',
          bezel: '#1a2429',
          line: '#2a3530',
          line2: '#37474f',
          amber: '#FFB400',
          'amber-dim': '#a87800',
          phosphor: '#4FE773',
          'phosphor-dim': '#2f8c45',
          ice: '#6FD3FF',
          red: '#FF3B30',
          'red-dim': '#a32420',
          ink: '#e8eaea',
          'ink-dim': '#8c9692',
          'ink-faint': '#566066',
        },
        surface: {
          900: '#0a0e0c',
          800: '#10171a',
          700: '#1a2429',
          600: '#2a3530',
          500: '#566066',
          400: '#8c9692',
          300: '#b7bfbc',
          200: '#dde3e0',
          100: '#f0f3f1',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        condensed: ['"IBM Plex Sans Condensed"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        'hud-glow-amber': '0 0 12px rgba(255,180,0,0.35), inset 0 0 1px rgba(255,180,0,0.5)',
        'hud-glow-green': '0 0 12px rgba(79,231,115,0.30), inset 0 0 1px rgba(79,231,115,0.5)',
        'hud-glow-red':   '0 0 14px rgba(255,59,48,0.45), inset 0 0 1px rgba(255,59,48,0.6)',
        bezel: 'inset 0 0 0 1px #2a3530, 0 2px 0 #000, 0 8px 24px rgba(0,0,0,0.5)',
      },
      letterSpacing: {
        callsign: '0.18em',
      },
      animation: {
        'scanline': 'scanline 8s linear infinite',
        'pulse-amber': 'pulse-amber 1.6s ease-in-out infinite',
      },
      keyframes: {
        'scanline': {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        'pulse-amber': {
          '0%, 100%': { opacity: '1', filter: 'drop-shadow(0 0 6px rgba(255,180,0,0.6))' },
          '50%':      { opacity: '0.55', filter: 'drop-shadow(0 0 0 rgba(255,180,0,0))' },
        },
      },
    },
  },
  plugins: [],
};
```

- [ ] **Step 3: Replace `frontend/src/index.css`.**

Write the full file:

```css
@import "tailwindcss";

:root {
  --hud-bg: #0a0e0c;
  --hud-amber: #FFB400;
  --hud-amber-dim: #a87800;
  --hud-phosphor: #4FE773;
  --hud-red: #FF3B30;
  --hud-ink: #e8eaea;
  --hud-line: #2a3530;
}

html, body, #root {
  height: 100%;
  background: var(--hud-bg);
  color: var(--hud-ink);
  font-family: "IBM Plex Sans", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}

body {
  background-image:
    radial-gradient(circle at 50% 0%, rgba(79,231,115,0.04) 0%, transparent 55%),
    repeating-linear-gradient(
      to right,
      rgba(42,53,48,0.18) 0 1px,
      transparent 1px 64px
    ),
    repeating-linear-gradient(
      to bottom,
      rgba(42,53,48,0.18) 0 1px,
      transparent 1px 64px
    );
  background-attachment: fixed;
}

.bezel {
  background: linear-gradient(180deg, #10171a 0%, #0d1316 100%);
  border: 1px solid var(--hud-line);
  border-radius: 6px;
  box-shadow:
    inset 0 0 0 1px rgba(42,53,48,0.4),
    0 2px 0 #000,
    0 12px 32px rgba(0,0,0,0.55);
  position: relative;
}

.bezel::before,
.bezel::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 10px;
  border-color: var(--hud-amber);
  border-style: solid;
  opacity: 0.7;
}
.bezel::before { top: 4px; left: 4px;  border-width: 1px 0 0 1px; }
.bezel::after  { bottom: 4px; right: 4px; border-width: 0 1px 1px 0; }

.bezel-label {
  position: absolute;
  top: -8px;
  left: 14px;
  background: var(--hud-bg);
  padding: 0 8px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--hud-amber-dim);
  text-transform: uppercase;
}

.phosphor {
  color: var(--hud-phosphor);
  text-shadow: 0 0 8px rgba(79,231,115,0.45);
}

.amber {
  color: var(--hud-amber);
  text-shadow: 0 0 8px rgba(255,180,0,0.45);
}

.scanlines {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    to bottom,
    rgba(255,255,255,0.012) 0 2px,
    transparent 2px 4px
  );
  mix-blend-mode: screen;
  z-index: 100;
}

.scanline-sweep {
  position: fixed;
  inset: -10vh 0 0 0;
  pointer-events: none;
  height: 100vh;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(79,231,115,0.04) 48%,
    rgba(79,231,115,0.08) 50%,
    rgba(79,231,115,0.04) 52%,
    transparent 100%
  );
  animation: scanline 8s linear infinite;
  z-index: 99;
}

/* Custom scrollbar — minimal, MFD style */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--hud-line) transparent;
}
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-track { background: transparent; }
*::-webkit-scrollbar-thumb { background: var(--hud-line); border-radius: 4px; }
*::-webkit-scrollbar-thumb:hover { background: var(--hud-amber-dim); }

::selection { background: rgba(255,180,0,0.35); color: #fff; }
```

- [ ] **Step 4: Verify build still passes.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
```

Expected: PASS.

- [ ] **Step 5: Commit.**

```bash
git add frontend/index.html frontend/tailwind.config.js frontend/src/index.css
git commit -m "feat(frontend): HUD/MFD design tokens, IBM Plex typography, scanline overlay"
```

---

## Task 4 — HUD primitive components

**Files:**
- Create: `frontend/src/components/hud/Bezel.tsx`
- Create: `frontend/src/components/hud/SegmentReadout.tsx`
- Create: `frontend/src/components/hud/RiskBadge.tsx`
- Create: `frontend/src/components/hud/StatusStrip.tsx`
- Create: `frontend/src/components/hud/ScanlineOverlay.tsx`
- Create: `frontend/src/components/hud/index.ts`

- [ ] **Step 1: `Bezel.tsx`.**

```typescript
// frontend/src/components/hud/Bezel.tsx
import React from 'react';
import clsx from 'clsx';

interface BezelProps {
  label?: string;
  status?: 'ok' | 'caution' | 'fail' | 'idle';
  className?: string;
  children: React.ReactNode;
}

const statusColor: Record<NonNullable<BezelProps['status']>, string> = {
  ok: 'text-hud-phosphor',
  caution: 'text-hud-amber',
  fail: 'text-hud-red',
  idle: 'text-hud-ink-faint',
};

export const Bezel: React.FC<BezelProps> = ({ label, status = 'idle', className, children }) => (
  <div className={clsx('bezel p-4', className)}>
    {label && (
      <span className={clsx('bezel-label', statusColor[status])}>
        {label}
      </span>
    )}
    {children}
  </div>
);
```

- [ ] **Step 2: `SegmentReadout.tsx`.**

```typescript
// frontend/src/components/hud/SegmentReadout.tsx
import React from 'react';
import clsx from 'clsx';

interface SegmentReadoutProps {
  value: number | string | null | undefined;
  unit?: string;
  precision?: number;
  width?: number;        // padded character width
  tone?: 'amber' | 'phosphor' | 'red' | 'ice';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  prefix?: string;
}

const toneCls: Record<NonNullable<SegmentReadoutProps['tone']>, string> = {
  amber: 'amber',
  phosphor: 'phosphor',
  red: 'text-hud-red drop-shadow-[0_0_8px_rgba(255,59,48,0.5)]',
  ice: 'text-hud-ice drop-shadow-[0_0_8px_rgba(111,211,255,0.5)]',
};

const sizeCls: Record<NonNullable<SegmentReadoutProps['size']>, string> = {
  sm: 'text-base',
  md: 'text-xl',
  lg: 'text-3xl',
  xl: 'text-5xl',
};

export const SegmentReadout: React.FC<SegmentReadoutProps> = ({
  value,
  unit,
  precision = 1,
  width = 0,
  tone = 'amber',
  size = 'md',
  prefix,
}) => {
  let body = '----';
  if (typeof value === 'number' && Number.isFinite(value)) {
    body = value.toFixed(precision);
  } else if (typeof value === 'string') {
    body = value;
  }
  const padded = width > 0 ? body.padStart(width, ' ') : body;
  return (
    <span className={clsx('font-mono tabular-nums tracking-tight', toneCls[tone], sizeCls[size])}>
      {prefix && <span className="text-hud-ink-faint pr-1">{prefix}</span>}
      <span>{padded}</span>
      {unit && <span className="text-hud-ink-faint text-[0.55em] pl-1 align-baseline">{unit}</span>}
    </span>
  );
};
```

- [ ] **Step 3: `RiskBadge.tsx`.**

```typescript
// frontend/src/components/hud/RiskBadge.tsx
import React from 'react';
import clsx from 'clsx';

export type RiskTier = 'CLEAR' | 'CAUTION' | 'WARNING' | 'G-LOC' | 'OOD';

interface RiskBadgeProps {
  tier: RiskTier;
  pulse?: boolean;
  className?: string;
}

const tierStyle: Record<RiskTier, string> = {
  CLEAR:   'bg-hud-phosphor/10 text-hud-phosphor border-hud-phosphor/50 shadow-hud-glow-green',
  CAUTION: 'bg-hud-amber/10 text-hud-amber border-hud-amber/60 shadow-hud-glow-amber',
  WARNING: 'bg-hud-amber/20 text-hud-amber border-hud-amber shadow-hud-glow-amber',
  'G-LOC': 'bg-hud-red/15 text-hud-red border-hud-red shadow-hud-glow-red',
  OOD:     'bg-hud-ice/10 text-hud-ice border-hud-ice/60',
};

export const RiskBadge: React.FC<RiskBadgeProps> = ({ tier, pulse, className }) => (
  <span
    className={clsx(
      'inline-flex items-center gap-2 px-3 py-1 rounded-sm border font-mono font-semibold text-xs tracking-callsign uppercase',
      tierStyle[tier],
      pulse && 'animate-pulse-amber',
      className,
    )}
  >
    <span className="w-1.5 h-1.5 rounded-full bg-current" />
    {tier}
  </span>
);
```

- [ ] **Step 4: `StatusStrip.tsx`.**

```typescript
// frontend/src/components/hud/StatusStrip.tsx
import React, { useEffect, useState } from 'react';

interface StatusStripProps {
  mode?: string;
  callsign?: string;
}

const fmt = (d: Date) =>
  d.toISOString().slice(11, 19) + 'Z';

export const StatusStrip: React.FC<StatusStripProps> = ({
  mode = 'TACTICAL',
  callsign = 'CGEM-1',
}) => {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-callsign text-hud-ink-faint px-1 pb-2 border-b border-hud-line/60">
      <span><span className="text-hud-amber">●</span> {mode}</span>
      <span>{callsign}</span>
      <span>{fmt(now)}</span>
    </div>
  );
};
```

- [ ] **Step 5: `ScanlineOverlay.tsx`.**

```typescript
// frontend/src/components/hud/ScanlineOverlay.tsx
import React from 'react';

export const ScanlineOverlay: React.FC = () => (
  <>
    <div className="scanlines" aria-hidden="true" />
    <div className="scanline-sweep" aria-hidden="true" />
  </>
);
```

- [ ] **Step 6: Barrel export.**

```typescript
// frontend/src/components/hud/index.ts
export { Bezel } from './Bezel';
export { SegmentReadout } from './SegmentReadout';
export { RiskBadge } from './RiskBadge';
export type { RiskTier } from './RiskBadge';
export { StatusStrip } from './StatusStrip';
export { ScanlineOverlay } from './ScanlineOverlay';
export { AttitudeIndicator } from './AttitudeIndicator';
export { GTracePlayer } from './GTracePlayer';
```

(The last two are added in Tasks 5 & 6 but the barrel export is fine to declare ahead — type-check will fail until those files land, so this commit happens only after Task 6.)

---

## Task 5 — AttitudeIndicator (SVG)

**Files:**
- Create: `frontend/src/components/hud/AttitudeIndicator.tsx`

**Approach.** Pure SVG, 240×240 viewBox. Sky (top) / ground (bottom) painted as two clipped rects rotated by `roll` and translated by `pitch`. Pitch ladder rungs every 10° from −90 to +90. Center cross + roll markers at top arc. `roll` and `pitch` are driven by integrating the G-trace: pitch ≈ scaled cumulative integral of `(Gz - 1)` (only used for visual proxy, not physiologically accurate); roll oscillates with sustained negative G or knife-edge segments per a lookup `rollHintForCategory`.

- [ ] **Step 1: Write the component.**

```typescript
// frontend/src/components/hud/AttitudeIndicator.tsx
import React from 'react';

interface AttitudeIndicatorProps {
  roll: number;   // degrees, positive = right wing down
  pitch: number;  // degrees, positive = nose up
  size?: number;
  showLabels?: boolean;
}

export const AttitudeIndicator: React.FC<AttitudeIndicatorProps> = ({
  roll,
  pitch,
  size = 240,
  showLabels = true,
}) => {
  const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
  const r = clamp(roll, -90, 90);
  const p = clamp(pitch, -45, 45);
  const pitchPx = p * 2;   // 2 px per degree on the ladder

  return (
    <svg
      viewBox="0 0 240 240"
      width={size}
      height={size}
      style={{ filter: 'drop-shadow(0 0 12px rgba(79,231,115,0.18))' }}
    >
      <defs>
        <clipPath id="adi-clip"><circle cx="120" cy="120" r="100" /></clipPath>
      </defs>
      <circle cx="120" cy="120" r="100" fill="#0a0e0c" stroke="#2a3530" strokeWidth="1.5" />
      <g clipPath="url(#adi-clip)" transform={`rotate(${-r} 120 120)`}>
        <g transform={`translate(0 ${pitchPx})`}>
          {/* Sky */}
          <rect x="0" y="-200" width="240" height="320" fill="#0d2330" />
          {/* Ground */}
          <rect x="0" y="120" width="240" height="320" fill="#2a1a08" />
          {/* Horizon line */}
          <line x1="0" y1="120" x2="240" y2="120" stroke="#FFB400" strokeWidth="1.5" />
          {/* Pitch ladder rungs */}
          {[-40, -30, -20, -10, 10, 20, 30, 40].map((deg) => {
            const y = 120 - deg * 2;
            const len = deg % 20 === 0 ? 50 : 30;
            return (
              <g key={deg}>
                <line x1={120 - len} y1={y} x2={120 + len} y2={y} stroke="#4FE773" strokeWidth="1" opacity={0.8} />
                {deg % 20 === 0 && (
                  <>
                    <text x={120 - len - 6} y={y + 3} fill="#4FE773" fontSize="9" fontFamily="IBM Plex Mono" textAnchor="end">
                      {Math.abs(deg)}
                    </text>
                    <text x={120 + len + 6} y={y + 3} fill="#4FE773" fontSize="9" fontFamily="IBM Plex Mono">
                      {Math.abs(deg)}
                    </text>
                  </>
                )}
              </g>
            );
          })}
        </g>
      </g>
      {/* Roll arc markers */}
      <g stroke="#FFB400" strokeWidth="1" fill="none">
        {[-60, -45, -30, -10, 0, 10, 30, 45, 60].map((deg) => {
          const a = (deg - 90) * (Math.PI / 180);
          const r1 = 95;
          const r2 = deg === 0 ? 80 : 88;
          return (
            <line
              key={deg}
              x1={120 + Math.cos(a) * r1}
              y1={120 + Math.sin(a) * r1}
              x2={120 + Math.cos(a) * r2}
              y2={120 + Math.sin(a) * r2}
            />
          );
        })}
      </g>
      {/* Roll pointer */}
      <g transform={`rotate(${-r} 120 120)`}>
        <polygon points="120,30 115,42 125,42" fill="#FFB400" />
      </g>
      {/* Center cross (aircraft symbol) */}
      <g stroke="#FFB400" strokeWidth="2.5" fill="none">
        <line x1="86" y1="120" x2="106" y2="120" />
        <line x1="134" y1="120" x2="154" y2="120" />
        <circle cx="120" cy="120" r="3" fill="#FFB400" />
      </g>
      {/* Bezel ring */}
      <circle cx="120" cy="120" r="101" fill="none" stroke="#000" strokeWidth="3" />
      {showLabels && (
        <>
          <text x="120" y="232" fill="#8c9692" fontSize="9" fontFamily="IBM Plex Mono" textAnchor="middle" letterSpacing="2">
            ATT  R {r.toFixed(0).padStart(3, ' ')}°  P {p.toFixed(0).padStart(3, ' ')}°
          </text>
        </>
      )}
    </svg>
  );
};
```

- [ ] **Step 2: Type-check.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check
```

Expected: PASS (this file uses no external imports beyond React).

---

## Task 6 — GTracePlayer

**Files:**
- Create: `frontend/src/components/hud/GTracePlayer.tsx`

**Approach.** ECharts time-series with `playbackIndex` driven by a `requestAnimationFrame` loop. Two series: cumulative G-trace + (optional) conformal band around predicted G-LOC time. Playhead = vertical mark line. Controls: play/pause, scrub, speed 0.5×/1×/2×.

- [ ] **Step 1: Write the component.**

```typescript
// frontend/src/components/hud/GTracePlayer.tsx
import React, { useEffect, useMemo, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import type { Maneuver } from '../../data/maneuvers';
import { flightTimeSeconds } from '../../data/maneuvers';

interface ConformalAnnotation {
  median_s: number;
  low_s: number;
  high_s: number;
  label: string;
}

interface GTracePlayerProps {
  maneuver: Maneuver;
  conformal?: ConformalAnnotation | null;
  height?: number;
  onTimeChange?: (t: number, g: number) => void;
}

export const GTracePlayer: React.FC<GTracePlayerProps> = ({
  maneuver,
  conformal = null,
  height = 320,
  onTimeChange,
}) => {
  const times = useMemo(() => flightTimeSeconds(maneuver), [maneuver]);
  const gs = useMemo(() => maneuver.samples.map((s) => s.nz), [maneuver]);
  const duration = times.length > 0 ? times[times.length - 1] : 0;

  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState<0.5 | 1 | 2>(1);
  const [t, setT] = useState(0);
  const lastFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (!playing) {
      lastFrameRef.current = null;
      return;
    }
    let raf = 0;
    const tick = (now: number) => {
      if (lastFrameRef.current === null) {
        lastFrameRef.current = now;
      }
      const dt = (now - lastFrameRef.current) / 1000;
      lastFrameRef.current = now;
      setT((prev) => {
        const next = prev + dt * speed;
        if (next >= duration) {
          setPlaying(false);
          return duration;
        }
        return next;
      });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, speed, duration]);

  // Interpolate current G at time t.
  const currentG = useMemo(() => {
    if (times.length === 0) return 0;
    if (t <= times[0]) return gs[0];
    if (t >= times[times.length - 1]) return gs[gs.length - 1];
    for (let i = 1; i < times.length; i++) {
      if (t < times[i]) {
        const f = (t - times[i - 1]) / (times[i] - times[i - 1]);
        return gs[i - 1] + f * (gs[i] - gs[i - 1]);
      }
    }
    return gs[gs.length - 1];
  }, [t, times, gs]);

  useEffect(() => {
    onTimeChange?.(t, currentG);
  }, [t, currentG, onTimeChange]);

  const option = useMemo<EChartsOption>(() => {
    const seriesData = times.map((tt, i) => [tt, gs[i]]);
    const markLines: any[] = [
      { xAxis: t, lineStyle: { color: '#FFB400', width: 1.5, type: 'solid' }, label: { show: false } },
      { yAxis: 5, lineStyle: { color: '#FF3B30', width: 0.5, type: 'dashed' }, label: { formatter: '5 G ALERT', color: '#FF3B30', fontFamily: 'IBM Plex Mono', fontSize: 9 } },
      { yAxis: 9, lineStyle: { color: '#FF3B30', width: 0.5, type: 'dashed' }, label: { formatter: '9 G LIMIT', color: '#FF3B30', fontFamily: 'IBM Plex Mono', fontSize: 9 } },
      { yAxis: 0, lineStyle: { color: '#37474f', width: 0.5, type: 'solid' }, label: { show: false } },
    ];
    const markAreas: any[] = [];
    if (conformal) {
      markAreas.push([
        { name: conformal.label, xAxis: conformal.low_s, itemStyle: { color: 'rgba(255,180,0,0.08)' } },
        { xAxis: conformal.high_s },
      ]);
      markLines.push({
        xAxis: conformal.median_s,
        lineStyle: { color: '#4FE773', width: 1.5, type: 'dashed' },
        label: { formatter: `T-LOC ${conformal.median_s.toFixed(1)}s`, color: '#4FE773', fontFamily: 'IBM Plex Mono', fontSize: 9 },
      });
    }
    return {
      animation: false,
      grid: { left: 48, right: 16, top: 16, bottom: 32 },
      xAxis: {
        type: 'value',
        name: 't (s)',
        nameLocation: 'middle',
        nameGap: 22,
        nameTextStyle: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        axisLine: { lineStyle: { color: '#2a3530' } },
        axisLabel: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(42,53,48,0.4)' } },
      },
      yAxis: {
        type: 'value',
        name: '+Gz',
        nameTextStyle: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        axisLine: { lineStyle: { color: '#2a3530' } },
        axisLabel: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(42,53,48,0.4)' } },
      },
      series: [
        {
          type: 'line',
          data: seriesData,
          smooth: false,
          showSymbol: false,
          lineStyle: { color: '#FFB400', width: 2 },
          areaStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(255,180,0,0.35)' },
                { offset: 1, color: 'rgba(255,180,0,0.0)' },
              ],
            },
          },
          markLine: { silent: true, symbol: 'none', data: markLines },
          markArea: { silent: true, data: markAreas },
        },
      ],
    };
  }, [times, gs, t, conformal]);

  const reset = () => { setT(0); setPlaying(false); };

  return (
    <div className="flex flex-col gap-2">
      <ReactECharts option={option} style={{ height, width: '100%' }} notMerge={false} lazyUpdate />
      <div className="flex items-center gap-3 text-xs font-mono">
        <button
          onClick={() => setPlaying((p) => !p)}
          className="px-3 py-1 bg-hud-amber/10 border border-hud-amber/50 text-hud-amber hover:bg-hud-amber/20 rounded-sm tracking-callsign uppercase"
        >
          {playing ? '■ Stop' : '▶ Play'}
        </button>
        <button
          onClick={reset}
          className="px-3 py-1 bg-hud-panel border border-hud-line text-hud-ink-dim hover:text-hud-ink rounded-sm tracking-callsign uppercase"
        >
          ⟲ Rewind
        </button>
        <div className="flex gap-1">
          {([0.5, 1, 2] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className={
                'px-2 py-1 rounded-sm border tracking-callsign uppercase ' +
                (speed === s
                  ? 'bg-hud-phosphor/20 border-hud-phosphor/60 text-hud-phosphor'
                  : 'bg-hud-panel border-hud-line text-hud-ink-faint hover:text-hud-ink')
              }
            >
              {s}×
            </button>
          ))}
        </div>
        <input
          type="range"
          min={0}
          max={duration}
          step={0.05}
          value={t}
          onChange={(e) => { setT(Number(e.target.value)); setPlaying(false); }}
          className="flex-1 accent-hud-amber"
        />
        <span className="amber font-mono w-20 text-right tabular-nums">{t.toFixed(2)} s</span>
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Type-check.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check
```

Expected: PASS. If ECharts type errors mention `any`-shaped `markLine` data, add `// eslint-disable-next-line @typescript-eslint/no-explicit-any` or convert the `any[]` declarations to `EChartsOption['series'][number]` shapes. Acceptable to keep `any[]` for the marker arrays since ECharts' mark types are intentionally loose.

- [ ] **Step 3: Commit Tasks 4–6 together.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
git add frontend/src/components/hud/
git commit -m "feat(frontend): HUD primitives — bezel, segment readout, risk badge, ADI, G-trace player"
```

---

## Task 7 — SimulatorPage `/simulator`

**Files:**
- Create: `frontend/src/pages/SimulatorPage.tsx`
- Modify: `frontend/src/pages/index.ts` (export SimulatorPage)
- Modify: `frontend/src/App.tsx` (add `/simulator` route)
- Modify: `frontend/src/components/layout/Sidebar.tsx` (add nav entry)

- [ ] **Step 1: Implement `SimulatorPage.tsx`.**

Architecture: three-column layout.
- Left rail (260 px): maneuver picker grouped by category, with peak G chip and Aresti family.
- Center (1 fr): `StatusStrip`, large `AttitudeIndicator` (bezel-wrapped), `GTracePlayer` below it.
- Right rail (320 px): live SegmentReadouts (current G, time, predicted T-LOC + CI), RiskBadge, hemodynamic_concern callout.

The page integrates pitch/roll using a simple proxy:
- `pitch += (gNow - 1) * 12 * dt` per frame, clamped to ±45°.
- `roll = sin(t * 0.6) * (maneuver.category === 'extreme_post_stall' ? 40 : 12)` — purely cosmetic; flagged as proxy in a tiny "VISUAL PROXY" note.

```typescript
// frontend/src/pages/SimulatorPage.tsx
import React, { useMemo, useState, useEffect, useRef } from 'react';
import {
  MANEUVERS,
  MANEUVERS_BY_CATEGORY,
  type Maneuver,
  type ManeuverCategory,
} from '../data/maneuvers';
import {
  Bezel,
  SegmentReadout,
  RiskBadge,
  StatusStrip,
  AttitudeIndicator,
  GTracePlayer,
  type RiskTier,
} from '../components/hud';
import { usePredict, useHealth, apiErrorMessage } from '../services/cgemApi';
import type {
  ManeuverDescriptors,
  PilotConfigRequest,
  PredictionRequest,
} from '../services/types';

const CATEGORY_LABELS: Record<ManeuverCategory, string> = {
  championship: 'CHAMPIONSHIP',
  military_acm: 'MILITARY ACM',
  extreme_post_stall: 'EXTREME / POST-STALL',
  training: 'TRAINING',
  conceptual: 'CONCEPTUAL',
};

function riskFromPrediction(median: number | null | undefined, eventProb: number | null | undefined): RiskTier {
  if (eventProb == null || median == null) return 'CLEAR';
  if (eventProb < 0.05) return 'CLEAR';
  if (eventProb < 0.25 && median > 10) return 'CAUTION';
  if (eventProb < 0.6) return 'WARNING';
  return 'G-LOC';
}

const DEFAULT_PILOT: PilotConfigRequest = {
  who_profile: 4,
  gsuit_max_psi: 5,
  gsuit_coverage_fraction: 0.6,
  agsm_effectiveness: 0.5,
  pbg_max_mmhg: 0,
  dehydration_level: 0,
  g_tolerance_multiplier: 1.0,
};

export const SimulatorPage: React.FC = () => {
  const health = useHealth();
  const apiAlive = health.data?.status === 'ok';

  const [selectedId, setSelectedId] = useState<string>('hammerhead');
  const maneuver = useMemo<Maneuver>(
    () => MANEUVERS.find((m) => m.id === selectedId) ?? MANEUVERS[0],
    [selectedId],
  );

  const [now, setNow] = useState({ t: 0, g: maneuver.samples[0]?.nz ?? 0 });

  // Proxy attitude: integrate pitch from G, oscillate roll on extreme maneuvers.
  const pitchRef = useRef(0);
  const lastTRef = useRef(0);
  useEffect(() => { pitchRef.current = 0; lastTRef.current = 0; }, [selectedId]);
  const dt = now.t - lastTRef.current;
  if (dt > 0) {
    pitchRef.current = Math.max(-45, Math.min(45, pitchRef.current + (now.g - 1) * 12 * dt));
    lastTRef.current = now.t;
  } else if (dt < 0) {
    // user scrubbed back; reset
    pitchRef.current = 0;
    lastTRef.current = now.t;
  }
  const rollAmp = maneuver.category === 'extreme_post_stall' ? 40
                 : maneuver.category === 'military_acm' ? 22
                 : 12;
  const roll = Math.sin(now.t * 0.6 + maneuver.id.length) * rollAmp;

  const predictMutation = usePredict();
  // Fire one prediction per maneuver change.
  useEffect(() => {
    if (!apiAlive) return;
    const desc: ManeuverDescriptors = {
      maneuver: maneuver.id,
      maneuver_category: maneuver.category,
      g_peak_abs: Math.abs(maneuver.peak_pos_gz),
      dgdt_max_g_per_s: maneuver.onset_rate_g_per_s,
      profile_duration_s: maneuver.total_duration_s,
    };
    const req: PredictionRequest = {
      pilot: DEFAULT_PILOT,
      maneuver: desc,
      targets: ['time_to_gloc_s'],
    };
    predictMutation.mutate(req);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [maneuver.id, apiAlive]);

  const glocPred = predictMutation.data?.predictions?.find(
    (p) => p.target === 'time_to_gloc_s',
  );
  const median = glocPred?.median ?? null;
  const lo = glocPred?.lower ?? null;
  const hi = glocPred?.upper ?? null;
  const eventProb = glocPred?.event_probability ?? null;
  const conformal = median != null && lo != null && hi != null
    ? { median_s: median, low_s: lo, high_s: hi, label: '95% CI' }
    : null;

  const risk = riskFromPrediction(median, eventProb);

  return (
    <div className="grid grid-cols-[260px_1fr_320px] gap-4 h-full">
      {/* Left rail — maneuver picker */}
      <Bezel label="MANEUVER LIBRARY · 71" className="overflow-y-auto max-h-[calc(100vh-120px)]">
        <div className="flex flex-col gap-4 mt-2">
          {(Object.keys(MANEUVERS_BY_CATEGORY) as ManeuverCategory[]).map((cat) => (
            <div key={cat}>
              <div className="font-mono text-[10px] tracking-callsign text-hud-amber-dim mb-1 pl-1">
                {CATEGORY_LABELS[cat]} · {MANEUVERS_BY_CATEGORY[cat].length}
              </div>
              <ul className="flex flex-col gap-0.5">
                {MANEUVERS_BY_CATEGORY[cat].map((m) => {
                  const active = m.id === selectedId;
                  return (
                    <li key={m.id}>
                      <button
                        onClick={() => setSelectedId(m.id)}
                        className={
                          'w-full text-left px-2 py-1 rounded-sm font-mono text-xs flex justify-between items-center ' +
                          (active
                            ? 'bg-hud-amber/15 text-hud-amber border border-hud-amber/40'
                            : 'border border-transparent text-hud-ink-dim hover:bg-hud-panel-2 hover:text-hud-ink')
                        }
                      >
                        <span className="truncate">{m.id.replace(/_/g, ' ')}</span>
                        <span className="text-[10px] text-hud-phosphor tabular-nums pl-2">
                          {m.peak_pos_gz >= 0 ? '+' : ''}{m.peak_pos_gz.toFixed(1)} G
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </Bezel>

      {/* Center — instrumentation */}
      <div className="flex flex-col gap-4 min-w-0">
        <StatusStrip mode={`SIM · ${maneuver.category.toUpperCase().replace('_', ' ')}`} callsign={maneuver.id.toUpperCase()} />
        <div className="grid grid-cols-[auto_1fr] gap-4">
          <Bezel label="ATTITUDE · VISUAL PROXY" status="caution" className="flex items-center justify-center">
            <AttitudeIndicator roll={roll} pitch={pitchRef.current} size={260} />
          </Bezel>
          <Bezel label="MANEUVER BRIEFING" status="ok" className="text-sm leading-relaxed text-hud-ink-dim">
            <div className="font-condensed text-xl text-hud-ink mb-2 tracking-wide uppercase">
              {maneuver.id.replace(/_/g, ' ')}
            </div>
            <p className="mb-3">{maneuver.description}</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-xs">
              <div className="text-hud-ink-faint">AIRCRAFT</div>
              <div className="amber">{maneuver.aircraft}</div>
              <div className="text-hud-ink-faint">PEAK +Gz</div>
              <div className="amber">{maneuver.peak_pos_gz.toFixed(1)} G</div>
              <div className="text-hud-ink-faint">PEAK −Gz</div>
              <div className="amber">{maneuver.peak_neg_gz.toFixed(1)} G</div>
              <div className="text-hud-ink-faint">ONSET</div>
              <div className="amber">{maneuver.onset_rate_g_per_s.toFixed(2)} G/s</div>
              <div className="text-hud-ink-faint">DURATION</div>
              <div className="amber">{maneuver.total_duration_s.toFixed(1)} s</div>
              {maneuver.aresti_family != null && (
                <>
                  <div className="text-hud-ink-faint">ARESTI</div>
                  <div className="amber">Fam {maneuver.aresti_family}{maneuver.aresti_code ? ` · ${maneuver.aresti_code}` : ''}</div>
                </>
              )}
            </div>
            {maneuver.hemodynamic_concern && (
              <div className="mt-3 pt-3 border-t border-hud-line text-hud-amber text-xs">
                ⚠ {maneuver.hemodynamic_concern}
              </div>
            )}
          </Bezel>
        </div>
        <Bezel label="G-TRACE PLAYBACK" status="ok">
          <GTracePlayer
            maneuver={maneuver}
            conformal={conformal}
            height={300}
            onTimeChange={(t, g) => setNow({ t, g })}
          />
        </Bezel>
      </div>

      {/* Right rail — live readouts */}
      <div className="flex flex-col gap-4">
        <Bezel label="LIVE TELEMETRY" status="ok">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">+Gz NOW</span>
              <SegmentReadout value={now.g} unit="G" tone="amber" size="xl" precision={2} width={5} />
            </div>
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">T ELAPSED</span>
              <SegmentReadout value={now.t} unit="s" tone="phosphor" size="md" precision={2} width={6} />
            </div>
          </div>
        </Bezel>
        <Bezel label={apiAlive ? 'PREDICTION · /predict' : 'PREDICTION · OFFLINE'} status={apiAlive ? 'ok' : 'fail'}>
          {!apiAlive && (
            <div className="text-hud-red text-xs font-mono">
              FastAPI service unreachable. Start it with<br />
              <span className="amber">uvicorn cgem_ext.api.main:app --reload</span>
            </div>
          )}
          {apiAlive && predictMutation.isPending && (
            <div className="text-hud-amber font-mono text-xs animate-pulse-amber">QUERYING SURROGATE…</div>
          )}
          {apiAlive && predictMutation.isError && (
            <div className="text-hud-red font-mono text-xs">{apiErrorMessage(predictMutation.error)}</div>
          )}
          {apiAlive && predictMutation.isSuccess && glocPred && (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">T-LOC MEDIAN</span>
                <SegmentReadout value={median} unit="s" tone="amber" size="lg" precision={1} width={5} />
              </div>
              <div className="flex justify-between">
                <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">95% CI</span>
                <span className="font-mono text-sm text-hud-phosphor tabular-nums">
                  [{lo!.toFixed(1)}, {hi!.toFixed(1)}]
                </span>
              </div>
              <div className="flex justify-between">
                <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">P(event)</span>
                <SegmentReadout value={eventProb} tone="ice" size="md" precision={3} width={5} />
              </div>
              <div className="pt-2 border-t border-hud-line flex justify-center">
                <RiskBadge tier={risk} pulse={risk === 'G-LOC' || risk === 'WARNING'} />
              </div>
            </div>
          )}
        </Bezel>
        <Bezel label="PILOT CONFIG" status="idle" className="text-xs font-mono">
          <div className="grid grid-cols-2 gap-x-3 gap-y-1">
            <div className="text-hud-ink-faint">WHO</div><div className="amber">FAA-4</div>
            <div className="text-hud-ink-faint">G-SUIT</div><div className="amber">5 psi · 60%</div>
            <div className="text-hud-ink-faint">AGSM</div><div className="amber">0.50</div>
            <div className="text-hud-ink-faint">PBG</div><div className="amber">0 mmHg</div>
            <div className="text-hud-ink-faint">DEHYD</div><div className="amber">0.00</div>
          </div>
          <div className="mt-3 text-hud-ink-faint">
            Edit in <span className="phosphor">/settings</span>
          </div>
        </Bezel>
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Export and route.**

In `frontend/src/pages/index.ts` append:

```typescript
export { SimulatorPage } from './SimulatorPage';
export { SettingsPage } from './SettingsPage';
```

In `frontend/src/App.tsx`, add `SimulatorPage` and `SettingsPage` to the import block, replace `SettingsPlaceholder` route with `<SettingsPage />`, and insert the simulator route (placed between `/prediction` and `/dashboard` for narrative ordering). Final route block:

```tsx
<Route path="/" element={<OverviewPage />} />
<Route path="/simulator" element={<SimulatorPage />} />
<Route path="/prediction" element={<PredictionPage />} />
<Route path="/dashboard" element={<DashboardPage />} />
<Route path="/batch" element={<BatchPage />} />
<Route path="/analysis" element={<AnalysisPage />} />
<Route path="/settings" element={<SettingsPage />} />
<Route path="/about" element={<AboutPage />} />
<Route path="*" element={<Navigate to="/" replace />} />
```

Delete the `SettingsPlaceholder` component.

- [ ] **Step 3: Add Sidebar entry.**

In `frontend/src/components/layout/Sidebar.tsx`, append the Simulator entry in the navigation array (place after Overview):

```tsx
{ to: '/simulator', label: 'Simulator', icon: <Plane className="w-4 h-4" /> },
```

Import `Plane` from `lucide-react` at the top.

- [ ] **Step 4: Type-check + build.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
```

Expected: PASS. SettingsPage is referenced in App.tsx but not yet created — defer Task 7 commit until Task 9 lands, OR add a 4-line stub now:

```typescript
// frontend/src/pages/SettingsPage.tsx
import React from 'react';
import { Bezel } from '../components/hud';
export const SettingsPage: React.FC = () => (
  <Bezel label="SETTINGS"><div className="text-hud-ink-dim">Loading…</div></Bezel>
);
```

Use the stub so this task's commit lands green, then Task 9 replaces it.

- [ ] **Step 5: Commit.**

```bash
git add frontend/src/pages/SimulatorPage.tsx frontend/src/pages/SettingsPage.tsx frontend/src/pages/index.ts frontend/src/App.tsx frontend/src/components/layout/Sidebar.tsx
git commit -m "feat(frontend): /simulator page with attitude indicator, G-trace playback, live /predict"
```

---

## Task 8 — DashboardPage uses real API

**Files:**
- Modify: `frontend/src/pages/DashboardPage.tsx`

- [ ] **Step 1: Replace mock with real call.**

Open `frontend/src/pages/DashboardPage.tsx`. Replace the `import { AEROBATIC_PROFILES, simulateCGEMResult } from '../services/mockData';` line with:

```typescript
import { MANEUVERS_BY_ID } from '../data/maneuvers';
import { useRunCgem, useHealth } from '../services/cgemApi';
import type { RunCGEMRequest } from '../services/types';
```

Then in the component, replace the `result = useMemo(...simulateCGEMResult)` block with a real mutation pattern:

```typescript
const health = useHealth();
const apiAlive = health.data?.status === 'ok';
const runCgem = useRunCgem();

useEffect(() => {
  if (!apiAlive || !profile) return;
  const req: RunCGEMRequest = {
    pilot: {
      who_profile: selectedPreset.whoProfile,
      gsuit_max_psi: selectedPreset.countermeasureOverrides?.gsuit_max_psi ?? 5,
      gsuit_coverage_fraction: selectedPreset.countermeasureOverrides?.gsuit_coverage_fraction ?? 0.6,
      agsm_effectiveness: selectedPreset.countermeasureOverrides?.agsm_effectiveness ?? 0.5,
      pbg_max_mmhg: selectedPreset.countermeasureOverrides?.pbg_max_mmhg ?? 0,
      dehydration_level: selectedPreset.countermeasureOverrides?.dehydration_level ?? 0,
      g_tolerance_multiplier: 1.0,
    },
    maneuver: selectedProfileId,
  };
  runCgem.mutate(req);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [selectedProfileId, selectedPreset.whoProfile, apiAlive]);

const result = useMemo<CGEMResult | null>(() => {
  if (runCgem.data?.data) {
    // Coerce CGEMRunData -> CGEMResult (legacy shape used by chart components)
    const d = runCgem.data.data;
    return {
      times_s: d.time_s,
      g_values: d.gz,
      geff_values: d.geff ?? d.gz,
      hlap_values: d.hlap ?? [],
      c_bank_values: d.c_bank ?? [],
      bo_bank_values: d.bo_bank ?? [],
      f_vis_values: d.f_vis ?? [],
      events: d.events ?? {},
    } as CGEMResult;
  }
  return null;
}, [runCgem.data]);
```

(Adapt the field names to whatever `CGEMRunData` actually exposes; if `geff` is absent, fall back to `gz`.)

- [ ] **Step 2: Loading / offline UX.**

Replace the existing `if (!profile || !stats || !result || !durations) { return <Loading /> }` with:

```tsx
if (!apiAlive) {
  return (
    <Bezel label="DASHBOARD · OFFLINE" status="fail">
      <p className="text-hud-red font-mono text-sm">
        FastAPI service is not reachable. Start it with:
      </p>
      <pre className="amber font-mono text-xs mt-2">uvicorn cgem_ext.api.main:app --reload</pre>
    </Bezel>
  );
}
if (runCgem.isPending || !result) {
  return (
    <Bezel label="DASHBOARD · COMPUTING" status="caution">
      <p className="text-hud-amber font-mono text-sm animate-pulse-amber">
        Running CGEM Fortran core via /run-cgem…
      </p>
    </Bezel>
  );
}
```

Import `Bezel` from `'../components/hud'` at the top.

- [ ] **Step 3: Type-check + build.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
```

Fix any reference to `AEROBATIC_PROFILES[...]` by switching to `MANEUVERS_BY_ID[...]`. The profile shape (`samples`, `id`, `description`) is identical between the two.

If `selectedPreset.countermeasureOverrides` types break, leave them as-is and use `as any` only on the read site (not on the write). Document with a comment that this is the legacy adapter site.

- [ ] **Step 4: Commit.**

```bash
git add frontend/src/pages/DashboardPage.tsx
git commit -m "feat(frontend): Dashboard uses /run-cgem instead of mock simulator"
```

---

## Task 9 — Real Settings page

**Files:**
- Create: `frontend/src/state/useUserPrefs.ts`
- Replace: `frontend/src/pages/SettingsPage.tsx` (stub from Task 7)
- Modify: `frontend/src/services/cgemApi.ts` (read baseURL from prefs at request time)

- [ ] **Step 1: Preferences hook.**

```typescript
// frontend/src/state/useUserPrefs.ts
import { useEffect, useSyncExternalStore } from 'react';

export interface UserPrefs {
  apiUrl: string;
  phosphorColor: 'amber' | 'green';
  units: 'G' | 'm_per_s2';
  defaults: {
    who_profile: number;
    gsuit_max_psi: number;
    gsuit_coverage_fraction: number;
    agsm_effectiveness: number;
    pbg_max_mmhg: number;
    dehydration_level: number;
  };
}

const KEY = 'cgem.prefs.v1';

const DEFAULTS: UserPrefs = {
  apiUrl: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  phosphorColor: 'amber',
  units: 'G',
  defaults: {
    who_profile: 4,
    gsuit_max_psi: 5,
    gsuit_coverage_fraction: 0.6,
    agsm_effectiveness: 0.5,
    pbg_max_mmhg: 0,
    dehydration_level: 0,
  },
};

function read(): UserPrefs {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return DEFAULTS;
  }
}

let current = read();
const listeners = new Set<() => void>();
const subscribe = (cb: () => void): (() => void) => {
  listeners.add(cb);
  return () => listeners.delete(cb);
};
const getSnapshot = () => current;

export function updateUserPrefs(patch: Partial<UserPrefs>): void {
  current = { ...current, ...patch };
  localStorage.setItem(KEY, JSON.stringify(current));
  listeners.forEach((cb) => cb());
}

export function useUserPrefs(): UserPrefs {
  return useSyncExternalStore(subscribe, getSnapshot, () => DEFAULTS);
}

// Cross-tab sync
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === KEY) {
      current = read();
      listeners.forEach((cb) => cb());
    }
  });
}
```

- [ ] **Step 2: Wire cgemApi to prefs.**

Replace the top of `frontend/src/services/cgemApi.ts`:

```typescript
import axios, { type AxiosError } from 'axios';
import { ... } from '@tanstack/react-query';
import type { ... } from './types';

const ENV_URL = (import.meta as unknown as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL;
const PREFS_KEY = 'cgem.prefs.v1';

function readPrefsApiUrl(): string {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (typeof parsed.apiUrl === 'string' && parsed.apiUrl.length > 0) return parsed.apiUrl;
    }
  } catch {/* ignore */}
  return ENV_URL ?? 'http://localhost:8000';
}

export const cgemHttp = axios.create({
  timeout: 60_000,
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
});

// Per-request baseURL ensures live updates from the Settings page.
cgemHttp.interceptors.request.use((cfg) => {
  cfg.baseURL = readPrefsApiUrl();
  return cfg;
});
```

Update the exported `cgemApiBaseURL` to be a function: `export const cgemApiBaseURL = readPrefsApiUrl;`. Update any consumer accordingly (probably none).

- [ ] **Step 3: Write the real `SettingsPage`.**

```typescript
// frontend/src/pages/SettingsPage.tsx
import React, { useState } from 'react';
import { Bezel, SegmentReadout } from '../components/hud';
import { useUserPrefs, updateUserPrefs } from '../state/useUserPrefs';
import { useHealth, useVersion } from '../services/cgemApi';

export const SettingsPage: React.FC = () => {
  const prefs = useUserPrefs();
  const [apiUrl, setApiUrl] = useState(prefs.apiUrl);
  const health = useHealth();
  const version = useVersion();

  const save = () => {
    updateUserPrefs({ apiUrl: apiUrl.trim() });
    health.refetch();
    version.refetch();
  };
  const reset = () => {
    setApiUrl('http://localhost:8000');
    updateUserPrefs({ apiUrl: 'http://localhost:8000' });
  };

  const updateDefault = <K extends keyof typeof prefs.defaults>(key: K, val: number) => {
    updateUserPrefs({ defaults: { ...prefs.defaults, [key]: val } });
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Bezel label="API CONNECTION" status={health.data?.status === 'ok' ? 'ok' : 'fail'}>
        <label className="block font-mono text-xs text-hud-ink-faint tracking-callsign">BASE URL</label>
        <input
          type="text"
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          className="w-full mt-1 bg-hud-bg border border-hud-line text-hud-amber font-mono px-2 py-1 rounded-sm focus:outline-none focus:border-hud-amber"
        />
        <div className="flex gap-2 mt-3">
          <button
            onClick={save}
            className="px-3 py-1 bg-hud-amber/10 border border-hud-amber/50 text-hud-amber hover:bg-hud-amber/20 rounded-sm font-mono text-xs tracking-callsign uppercase"
          >
            Apply
          </button>
          <button
            onClick={reset}
            className="px-3 py-1 bg-hud-panel border border-hud-line text-hud-ink-dim hover:text-hud-ink rounded-sm font-mono text-xs tracking-callsign uppercase"
          >
            Default
          </button>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-xs">
          <div className="text-hud-ink-faint">HEALTH</div>
          <div className={health.data?.status === 'ok' ? 'phosphor' : 'text-hud-red'}>
            {health.data?.status ?? 'unknown'}
          </div>
          <div className="text-hud-ink-faint">VERSION</div>
          <div className="amber">{version.data?.version ?? '—'}</div>
          <div className="text-hud-ink-faint">MODELS</div>
          <div className="amber">{version.data?.models_trained ? '✓ ready' : 'training'}</div>
        </div>
      </Bezel>

      <Bezel label="DEFAULT PILOT CONFIG" status="ok">
        {(['who_profile','gsuit_max_psi','gsuit_coverage_fraction','agsm_effectiveness','pbg_max_mmhg','dehydration_level'] as const).map((k) => (
          <div key={k} className="flex items-center justify-between py-1 border-b border-hud-line/40 last:border-0">
            <label className="font-mono text-xs text-hud-ink-faint tracking-callsign uppercase">{k.replace(/_/g, ' ')}</label>
            <input
              type="number"
              step="0.05"
              value={prefs.defaults[k]}
              onChange={(e) => updateDefault(k, Number(e.target.value))}
              className="w-24 bg-hud-bg border border-hud-line text-hud-amber font-mono px-2 py-0.5 rounded-sm text-right focus:outline-none focus:border-hud-amber"
            />
          </div>
        ))}
      </Bezel>

      <Bezel label="DISPLAY" status="idle">
        <div className="font-mono text-xs space-y-2">
          <div className="text-hud-ink-faint">PHOSPHOR PRIMARY</div>
          <div className="flex gap-2">
            {(['amber','green'] as const).map((c) => (
              <button
                key={c}
                onClick={() => updateUserPrefs({ phosphorColor: c })}
                className={
                  'px-3 py-1 rounded-sm border font-mono tracking-callsign uppercase ' +
                  (prefs.phosphorColor === c
                    ? c === 'amber'
                      ? 'bg-hud-amber/20 border-hud-amber text-hud-amber'
                      : 'bg-hud-phosphor/20 border-hud-phosphor text-hud-phosphor'
                    : 'bg-hud-panel border-hud-line text-hud-ink-faint')
                }
              >
                {c}
              </button>
            ))}
          </div>
          <div className="text-hud-ink-faint pt-3">UNIT (DISPLAY ONLY)</div>
          <div className="flex gap-2">
            {(['G','m_per_s2'] as const).map((u) => (
              <button
                key={u}
                onClick={() => updateUserPrefs({ units: u })}
                className={
                  'px-3 py-1 rounded-sm border font-mono tracking-callsign uppercase ' +
                  (prefs.units === u ? 'bg-hud-phosphor/20 border-hud-phosphor text-hud-phosphor' : 'bg-hud-panel border-hud-line text-hud-ink-faint')
                }
              >
                {u === 'G' ? '+Gz' : 'm/s²'}
              </button>
            ))}
          </div>
        </div>
      </Bezel>

      <Bezel label="ABOUT" status="ok">
        <div className="font-mono text-xs text-hud-ink-dim space-y-1">
          <div>CGEM Tactical Display</div>
          <div>FAA CAMI G-Effects Model · Wrapper</div>
          <div className="amber pt-2">Build: <SegmentReadout value={version.data?.version ?? '0.0.0'} tone="amber" size="sm" /></div>
          <a href="https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-" className="phosphor hover:underline pt-2 block">
            github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-
          </a>
        </div>
      </Bezel>
    </div>
  );
};
```

- [ ] **Step 4: Type-check + build.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
```

Expected: PASS.

- [ ] **Step 5: Commit.**

```bash
git add frontend/src/pages/SettingsPage.tsx frontend/src/state/ frontend/src/services/cgemApi.ts
git commit -m "feat(frontend): real Settings page with API URL, default config, display prefs"
```

---

## Task 10 — TopBar API health/version

**Files:**
- Modify: `frontend/src/components/layout/TopBar.tsx`
- Modify: `frontend/src/components/layout/MainLayout.tsx`

- [ ] **Step 1: TopBar wires hooks + LED + version chip.**

Inside `TopBar.tsx`, at the top of the component:

```typescript
import { useHealth, useVersion } from '../../services/cgemApi';

const health = useHealth();
const version = useVersion();
const apiState: 'ok' | 'down' | 'pending' =
  health.isPending ? 'pending'
  : health.data?.status === 'ok' ? 'ok'
  : 'down';

const dotColor = apiState === 'ok' ? 'bg-hud-phosphor shadow-hud-glow-green'
              : apiState === 'down' ? 'bg-hud-red shadow-hud-glow-red'
              : 'bg-hud-amber shadow-hud-glow-amber';
```

Replace the right-side info block with:

```tsx
<div className="flex items-center gap-4 font-mono text-[11px] tracking-callsign text-hud-ink-faint">
  <span className="flex items-center gap-1.5">
    <span className={`w-2 h-2 rounded-full ${dotColor} ${apiState === 'pending' ? 'animate-pulse-amber' : ''}`} />
    <span className={apiState === 'ok' ? 'phosphor' : apiState === 'down' ? 'text-hud-red' : 'amber'}>
      {apiState === 'ok' ? 'API LINK' : apiState === 'down' ? 'NO LINK' : 'HANDSHAKE'}
    </span>
  </span>
  {version.data?.version && (
    <span className="amber">v{version.data.version}</span>
  )}
  <span>CGEM-1 · DLM</span>
</div>
```

Replace the existing search bar text with a callsign-tinted label:

```tsx
<input
  type="text"
  placeholder="SEARCH MANEUVER · TAG · CATEGORY"
  className="bg-hud-panel-2 border border-hud-line text-hud-amber font-mono text-xs tracking-callsign placeholder:text-hud-ink-faint placeholder:tracking-callsign px-3 py-1.5 rounded-sm focus:outline-none focus:border-hud-amber w-72"
/>
```

- [ ] **Step 2: MainLayout adds scanline overlay.**

In `frontend/src/components/layout/MainLayout.tsx`, import `ScanlineOverlay` and render it once at root:

```tsx
import { ScanlineOverlay } from '../hud';
// inside the return:
<>
  <ScanlineOverlay />
  {/* existing layout */}
</>
```

- [ ] **Step 3: Build + commit.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
cd ..
git add frontend/src/components/layout/
git commit -m "feat(frontend): TopBar API link/version indicator, CRT scanline overlay"
```

---

## Task 11 — OverviewPage upgrade

**Files:**
- Modify: `frontend/src/pages/OverviewPage.tsx`

- [ ] **Step 1: Swap mock data for real catalog.**

Replace `import { AEROBATIC_PROFILES } from '../services/mockData';` with `import { MANEUVERS_BY_ID, MANEUVERS } from '../data/maneuvers';` and update any reference (`AEROBATIC_PROFILES[id]` → `MANEUVERS_BY_ID[id]`, `Object.values(AEROBATIC_PROFILES)` → `MANEUVERS`).

- [ ] **Step 2: Add a HUD-styled "Open in Simulator" CTA.**

Find the existing "Run Simulation" / detail button and wrap in:

```tsx
import { Link } from 'react-router-dom';
// ...
<Link
  to={`/simulator?id=${selectedProfileId}`}
  className="inline-block mt-3 px-4 py-2 bg-hud-amber/15 border border-hud-amber text-hud-amber font-mono text-sm tracking-callsign uppercase hover:bg-hud-amber/25 rounded-sm"
>
  ▶ Open in Simulator
</Link>
```

(The simulator currently doesn't read the query string; that's acceptable — selection still defaults to hammerhead. A small follow-up could wire `useSearchParams`; not in scope for this PR.)

- [ ] **Step 3: Build + commit.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
cd ..
git add frontend/src/pages/OverviewPage.tsx
git commit -m "feat(frontend): Overview uses real maneuver catalog + Simulator CTA"
```

---

## Task 12 — Pages that still import mockData

**Files:**
- Modify: `frontend/src/pages/PredictionPage.tsx`, `BatchPage.tsx`, `AnalysisPage.tsx`, `frontend/src/components/ui/ProfileSelector.tsx`

These pages already call the real API; only the maneuver picker source is mock. Same swap.

- [ ] **Step 1: Replace imports across the four files.**

In each file, replace `import { AEROBATIC_PROFILES } from '../services/mockData';` (or `'../../services/mockData'` in the UI component) with `import { MANEUVERS_BY_ID as AEROBATIC_PROFILES } from '../data/maneuvers';` (the alias keeps the existing variable name; types are compatible because `Maneuver` is a superset of `AerobaticProfile`'s `id` + `description` + `samples`).

If TypeScript complains about extra fields, change to:

```typescript
import { MANEUVERS } from '../data/maneuvers';
const AEROBATIC_PROFILES = Object.fromEntries(MANEUVERS.map((m) => [m.id, { id: m.id, filename: m.filename, description: m.description, samples: m.samples }]));
```

- [ ] **Step 2: Build + commit.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run type-check && npm run build
cd ..
git add frontend/src/pages/ frontend/src/components/ui/
git commit -m "feat(frontend): all pickers source from build-time maneuver catalog (mockData retired as primary)"
```

---

## Task 13 — Test gate: lint + type-check + build + backend pytest

- [ ] **Step 1: Frontend lint + type-check + build.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run lint || true   # capture warnings, don't block on them
npm run type-check
npm run build
```

Expected: type-check + build PASS. Lint warnings noted but acceptable (project has not been gating on lint strictness).

- [ ] **Step 2: Backend test gate.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
source .venv/bin/activate 2>/dev/null || source ~/.venvs/cgem-ci/bin/activate
pytest -m "not needs_cgem_binary" -v 2>&1 | tail -40
```

Expected: backend tests pass. None of our changes should affect them (we touched no backend code beyond adding a new script).

- [ ] **Step 3: Boot dev server, snapshot the home + simulator.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-/frontend
npm run dev &
sleep 3
curl -sf http://localhost:5173/ -o /dev/null && echo OK || echo FAIL
kill %1 2>/dev/null
```

Expected: `OK`. If FastAPI isn't running, the Simulator page should render with the "OFFLINE" badge — that's the designed degradation.

---

## Task 14 — Push to `main`

- [ ] **Step 1: Verify clean tree + correct branch.**

```bash
cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
git status --short
git log --oneline -10
git branch --show-current
```

Expected: branch = `main`; the recent commits are the ones from Tasks 2, 4–12.

- [ ] **Step 2: Push.**

```bash
git push origin main
```

Expected: success. If the remote rejects due to upstream changes, `git pull --rebase origin main` and re-push.

- [ ] **Step 3: Done. The frontend is on `main` for the community.**

---

## Self-Review

**Spec coverage:**
- [x] DashboardPage uses real API → Task 8
- [x] Settings page (real, not placeholder) → Task 9
- [x] OverviewPage upgrade → Task 11
- [x] Health/version surfaced in chrome → Task 10
- [x] Aerobatic simulation from the `Aerobatics_sample_inputs/` folder → Tasks 2 + 7
- [x] Aviation-friendly aesthetic → Tasks 3, 4, 5, 6 + applied across pages
- [x] Build + lint + test gate → Task 13
- [x] Commit + push to main → Task 14

**Placeholder scan:** No TBDs, no "implement later." Every code block is concrete. Where a follow-up is acknowledged (e.g. `useSearchParams` in OverviewPage CTA, lint-strict gating), it is called out explicitly as out of scope.

**Type consistency:** `Maneuver` defined in Task 2, consumed verbatim in Tasks 7, 11, 12. `RiskTier` defined in Task 4, consumed in Task 7. `UserPrefs` defined in Task 9 with the same shape read by `cgemApi.ts`. The DashboardPage adapter (Task 8) explicitly notes the CGEMRunData → CGEMResult coercion and falls back when fields are absent — acceptable.

**Risk register:**
1. The `runCgem.data.data` field names in Task 8 assume the JSON contract shape — if `c_bank` is named differently in `CGEMRunData`, the adapter logs nothing useful. **Mitigation:** check `frontend/src/services/types.ts` first, adjust field names accordingly, and keep the fallback pattern (`d.c_bank ?? []`).
2. The `prebuild` script requires `python3` on PATH at build time. On CI (GitHub Actions), the workflow already sets up Python 3.12 — no action needed.
3. Pushing directly to `main` bypasses code review. User explicitly accepted this in the scope-question; risk owned.
