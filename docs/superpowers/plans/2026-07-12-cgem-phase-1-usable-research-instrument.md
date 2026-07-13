# CGEM Phase 1 Usable Research Instrument Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the complete responsive, accessible, shareable, provenance-bearing Phase 1 frontend without changing CGEM physiology or protected contracts.

**Architecture:** Establish a typed route registry and responsive shell first, then add URL state, keyboard controls, evidence/export actions, generated contracts, accessible charts, and browser verification. Pure utilities own parsing and export logic; React contexts own shell and active-result actions; all eight routes remain stable.

**Tech Stack:** React 19, TypeScript 5.9, React Router 7, TanStack Query 5, Tailwind CSS 4, Framer Motion 12, Vitest 4, Testing Library, Playwright, openapi-typescript, FastAPI/Pydantic OpenAPI.

## Global Constraints

- Never modify `src/cgem.f`, compiled binaries, or `gloc_inp.dat` semantics.
- Preserve public `run_cgem_for_profile` / `PilotConfig` signatures and the `/run-cgem` response field set.
- Preserve `/`, `/simulator`, `/prediction`, `/dashboard`, `/batch`, `/analysis`, `/settings`, and `/about`.
- Never display heuristic physiology or fabricate provenance.
- Keep probability, conditional event time, continuous output, and prediction intervals distinct.
- Desktop is `>=1024px`; tablet is `768–1023px`; mobile is `<768px`.
- Verify no document overflow at 390, 768, 1024, and 1440 px; touch targets are at least 44×44 px.
- Honor `prefers-reduced-motion`; small telemetry text must meet WCAG AA.
- The existing Phase 2 bundle warning remains non-blocking.
- Implement every behavior test-first.

---

### Task 1: Route Registry and Semantic Shell

**Files:**
- Create: `frontend/src/app/routes.ts`, `frontend/src/app/routes.test.ts`, `frontend/src/components/layout/MainLayout.test.tsx`, `frontend/src/test/setup.ts`
- Modify: `frontend/src/App.tsx`, `frontend/src/components/layout/{MainLayout,Sidebar,TopBar}.tsx`, `frontend/vitest.config.ts`

**Interfaces:**
- `APP_ROUTES: readonly AppRoute[]`; `routeForPath(pathname): AppRoute`.
- `AppRoute`: `id`, `path`, `label`, `title`, `subtitle`, `group`, `description`, `keywords`, `helpHash`.
- `<main id="main-content" tabIndex={-1}>` and `Skip to main content`.

- [ ] Add shared Vitest setup with jest-dom and `afterEach(cleanup)`; remove duplicate cleanup hooks.
- [ ] Write a failing registry test asserting the exact eight paths, unique IDs, non-empty keywords, and `#` help hashes.
- [ ] Run `cd frontend && npm test -- --run src/app/routes.test.ts`; expect missing-module failure.
- [ ] Implement the registry; keep page-component mapping in `App.tsx`; replace Sidebar and TopBar metadata copies.
- [ ] Write failing layout tests asserting banner, `Primary` navigation, main landmark, skip link, and named collapse/refresh buttons.
- [ ] Implement semantic landmarks, `aria-current`, and button names.
- [ ] Run `npm test -- --run src/app/routes.test.ts src/components/layout/MainLayout.test.tsx && npm run type-check && npm run lint`.
- [ ] Commit with `git commit -m "feat(frontend): establish semantic route shell"`.

### Task 2: Responsive Drawer, Tokens, and Reduced Motion

**Files:**
- Create: `frontend/src/components/layout/MobileNavDrawer.tsx`
- Modify: `frontend/src/components/layout/{MainLayout,Sidebar,TopBar}.tsx`, `frontend/src/components/hud/ScanlineOverlay.tsx`, `frontend/src/index.css`
- Test: `frontend/src/components/layout/MainLayout.test.tsx`

**Interfaces:**
- `MobileNavDrawer({ open, onClose, triggerRef })` owns focus containment/restoration.
- CSS tokens: `--shell-sidebar-wide:260px`, `--shell-sidebar-rail:72px`, `--shell-header:64px`, `--hud-ink-faint:#aab4c3`.

- [ ] Add failing 390 px tests: persistent sidebar absent, named 44 px trigger, modal `Navigation` dialog, Tab wrap, Escape close, trigger focus restoration.
- [ ] Implement CSS-driven desktop/tablet/mobile modes; do not branch render behavior on `window.innerWidth`.
- [ ] Implement `aria-modal`, focusable-element wrapping, body scroll lock, background `inert`, route-close, and cleanup restoration.
- [ ] Add failing assertions for focus-visible CSS, exact faint token, reduced-motion media rule, and decorative `aria-hidden` scanlines.
- [ ] Add graphite/amber/cyan/green/red tokens; replace shell `transition-all`; disable sweep/pulses/card motion under reduced motion.
- [ ] Run layout tests, type-check, lint, and build.
- [ ] Commit with `git commit -m "feat(frontend): add responsive accessible navigation"`.

### Task 3: Typed URL State and Page Migration

**Files:**
- Create: `frontend/src/services/urlState.ts`, `frontend/src/services/urlState.test.ts`
- Modify: `frontend/src/pages/{Overview,Simulator,Prediction,Dashboard,Batch,Analysis}Page.tsx`

**Interfaces:**
- `readManeuverParam`, `readEnumParam`, `readIntParam`, `setSearchParam` are pure.
- Page schemas: `predictionUrlState`, `dashboardUrlState`, `batchUrlState`, `analysisUrlState`, each with `read` and `write`.
- Defaults are omitted; output parameter order is deterministic.

- [ ] Write failing tests for valid/invalid maneuver IDs; Prediction `view=surrogate|authoritative|comparison`; Dashboard maneuver/preset/chart/layout; Batch target/direction/OOD/category; Analysis target/view; canonical round trips.
- [ ] Run `npm test -- --run src/services/urlState.test.ts`; expect missing-module failure.
- [ ] Implement immutable `URLSearchParams` parsing using catalog IDs and literal allowlists.
- [ ] Add page integration tests that initialize from non-default URLs, change controls, inspect URL updates, and reject invalid values before API calls.
- [ ] Migrate shareable control state to `useSearchParams`; push meaningful selections and replace transient chart/filter changes. Keep playback time and in-progress form edits local.
- [ ] Add a polite fallback announcement when invalid URL state materially changes.
- [ ] Run URL/page tests, type-check, and lint.
- [ ] Commit with `git commit -m "feat(frontend): make research state shareable"`.

### Task 4: Global Search and Accessible Profile Selector

**Files:**
- Create: `frontend/src/components/ui/ManeuverSearch.tsx`, `ManeuverSearch.test.tsx`, `ProfileSelector.test.tsx`, `frontend/src/components/layout/TopBar.test.tsx`
- Modify: `frontend/src/components/ui/ProfileSelector.tsx`, `frontend/src/components/ui/index.ts`, `frontend/src/components/layout/TopBar.tsx`, `frontend/package*.json`

**Interfaces:**
- `ManeuverSearch({ onNavigate })` emits `/simulator?maneuver=<id>`.
- `ProfileSelector` preserves current props and adds `label?: string` defaulting to `Maneuver profile`.
- Both expose combobox/listbox/option semantics and `aria-activedescendant`.

- [ ] Install `@testing-library/user-event`.
- [ ] Write failing search tests: type `hammer`, ArrowDown/Enter navigates; Escape closes; no-match polite status.
- [ ] Implement search over ID/name/category/aircraft/description/tags, capped at eight results.
- [ ] Remove Notifications. Make Help route to current `helpHash`. Make Refresh named, disabled/pending, and live-announced.
- [ ] Write failing ProfileSelector tests for named combobox, arrow navigation, Enter selection, Escape/outside dismissal, and focus restoration; assert old Low/Medium/High risk labels are absent.
- [ ] Implement stable option IDs, active index, scroll-into-view, named search input, and neutral load wording.
- [ ] Run the three component suites, type-check, and lint.
- [ ] Commit with `git commit -m "feat(frontend): implement keyboard research controls"`.

### Task 5: Evidence Rail and Provenance-Bearing Export

**Files:**
- Create: `frontend/src/components/ui/{EvidenceRail,EvidenceRail.test,ResultActions}.tsx`, `frontend/src/services/{exportResult,exportResult.test}.ts`
- Modify: `frontend/src/components/layout/{MainLayout,TopBar}.tsx`, `frontend/src/pages/{Simulator,Prediction,Dashboard,Batch}Page.tsx`

**Interfaces:**
- `Evidence = {kind:'surrogate'; response:PredictionResponse} | {kind:'authoritative'; run:CGEMRunResponse; version?:VersionResponse}`.
- `ExportSpec = {filename:string; mediaType:'application/json'|'text/csv'; content:string}`.
- `ResultActionsProvider` exposes `registerExport(spec|null)` and `activeExport`.
- `downloadExport` always revokes its object URL.

- [ ] Write failing EvidenceRail tests for complete surrogate evidence, authoritative evidence, OOD text, global/category scope, absent optional version, and accessible non-color summary.
- [ ] Implement an `<aside aria-label="Result evidence"><dl>…</dl></aside>` that omits unavailable values.
- [ ] Write failing export tests for deterministic JSON, RFC 4180 CSV escaping, sanitized filenames, and required source/maneuver/version/scope/OOD/input fields.
- [ ] Implement JSON exports for Prediction/Dashboard and row-per-target CSV for Batch; caller supplies timestamp.
- [ ] Implement context registration/unregistration; TopBar shows `Export current result` only when real result content exists and announces completion/errors.
- [ ] Place rails adjacent to Simulator/Prediction/Dashboard results and shared Batch evidence above the table.
- [ ] Run evidence/export/page tests, type-check, and lint.
- [ ] Commit with `git commit -m "feat(frontend): expose and export result evidence"`.

### Task 6: Generated Types and API-Scoped Cache

**Files:**
- Create: `frontend/src/services/generated/api.ts`, `frontend/src/services/wireTypes.ts`, `frontend/src/services/queryKeys.ts`, `queryKeys.test.ts`
- Modify: `frontend/src/services/{types,cgemApi,pilotConfig,runCgemAdapter}.ts`, `frontend/src/state/useUserPrefs.ts`, `frontend/src/pages/SettingsPage.tsx`, `frontend/package*.json`, `scripts/export_openapi.py`, `.github/workflows/ci.yml`

**Interfaces:**
- `wireTypes.ts` aliases `components['schemas'][Name]`; UI types remain handwritten.
- Every query/mutation key begins `['cgem', apiBaseUrl, ...]`.

- [ ] Install `openapi-typescript`; add `generate:openapi`, `generate:types`, and `generate:contracts` scripts targeting `src/services/generated/api.ts`.
- [ ] Run generation and create stable aliases for every currently consumed schema.
- [ ] Write failing query-key tests proving `http://a` and `http://b` cannot collide, including sensitivity target and mutation scopes.
- [ ] Scope hooks with reactive `useUserPrefs().apiUrl`; capture URL in mutation functions; replace static `cgemApiBaseURL` callers.
- [ ] On API URL change remove `['cgem', oldUrl]` queries and announce connection-context change.
- [ ] Add `generated-contracts` CI: generate, then `git diff --exit-code docs/api/openapi.json frontend/src/services/generated/api.ts`.
- [ ] Run generation, tests, type-check, lint, and protected API/contract tests; compare `CGEMRunResponse.required` with `origin/main`.
- [ ] Commit with `git commit -m "build(frontend): generate and scope API contracts"`.

### Task 7: Chart Accessibility and Visual Consolidation

**Files:**
- Create: `frontend/src/components/charts/BaseChart.test.tsx`
- Modify: `frontend/src/components/charts/*.tsx`, `frontend/src/components/ui/{MetricCard,VariableInsightsPanel}.tsx`, all six result pages, `frontend/src/index.css`

**Interfaces:**
- `BaseChart` requires `accessibleName` and `accessibleSummary`.
- Container uses `role="img"`; canvas is not an artificial tab stop.
- `.instrument-panel` replaces glass styling in modified result surfaces.

- [ ] Mock ECharts and write failing tests for chart role/name/data-derived summary and absent canvas tab stop.
- [ ] Add exact summaries: G/effective-G duration and peak; sensitivity top ST feature; distributions range/bin count; state durations; cerebral flow; heatmap state timeline.
- [ ] Define solid graphite `.instrument-panel`; migrate modified surfaces; remove blue tint, excessive glow, decorative card motion, and `transition-all`.
- [ ] Audit all modified buttons/inputs/selects for names, labels, focus, 44 px mobile targets, named transitions, and live async feedback.
- [ ] Fetch and apply the current Web Interface Guidelines to `frontend/src/components` and `frontend/src/pages`; record only Phase 2 performance deferrals.
- [ ] Run all frontend tests, type-check, lint, and build.
- [ ] Commit with `git commit -m "fix(frontend): complete accessible evidence console"`.

### Task 8: Playwright, CI, and Completion Documentation

**Files:**
- Create: `frontend/playwright.config.ts`, `frontend/e2e/fixtures/api.ts`, `frontend/e2e/research-workflow.spec.ts`
- Modify: `frontend/package*.json`, `.github/workflows/ci.yml`, `CHANGELOG.md`, `ROADMAP.md`, Phase 1 spec.

**Interfaces:**
- Projects: `mobile-390`, `tablet-768`, `desktop-1024`, `desktop-1440`.
- `npm run test:e2e` runs all; Vite serves `127.0.0.1:4173`.

- [ ] Install `@playwright/test` and Chromium; configure screenshots on failure and trace on first retry.
- [ ] Build complete mocked `/healthz`, `/version`, `/predict`, `/run-cgem`, `/sweep`, and `/sensitivity/*` fixtures with every documented field.
- [ ] Write browser tests for no document overflow at all four widths; drawer focus/Escape; keyboard search; URL reload/back/forward; Explore→Predict→Verify→Compare; evidence rails; and visible control actions.
- [ ] Add `frontend-e2e` CI depending on frontend-static/generated-contracts; upload report on failure.
- [ ] Run full gates:

```bash
python -m pytest tests -m "not needs_cgem_binary" -q
python -m pytest tests/test_contract.py tests/test_api.py -q
.venv/bin/ruff check cgem_ext tests
.venv/bin/mypy cgem_ext tests
cd frontend
npm run generate:contracts
npm test -- --run
npm run type-check
npm run lint
npm run build
npm run test:e2e
cd ..
git diff --exit-code docs/api/openapi.json frontend/src/services/generated/api.ts frontend/src/data/maneuvers.json
git diff --check
```

- [ ] Update CHANGELOG/ROADMAP/spec with breakpoints, URL parameters, controls, evidence, codegen, and browser coverage; mark only F1/F6/F7/F8/F9/F10 complete.
- [ ] Search for unnamed icon buttons, `transition-all`, runtime `simulateCGEMResult`, `95% CI`, `Safe Limit`, `High Risk`, Notifications, static `cgemApiBaseURL`, and duplicate wire schemas; fix Phase 1 violations.
- [ ] Commit with `git commit -m "test(frontend): verify phase 1 research workflow"`.

---

## Binding Implementation Contracts

Use these signatures verbatim so independently implemented tasks compose:

```ts
export type RouteGroup = 'explore' | 'run' | 'compare' | 'explain' | 'system';
export interface AppRoute {
  id: string; path: string; label: string; title: string; subtitle: string;
  group: RouteGroup; description: string; keywords: readonly string[]; helpHash: `#${string}`;
}
export const APP_ROUTES: readonly AppRoute[];
export function routeForPath(pathname: string): AppRoute;
```

```ts
export function readManeuverParam(params: URLSearchParams, fallback?: string): string;
export function readEnumParam<T extends string>(
  params: URLSearchParams, key: string, allowed: readonly T[], fallback: T,
): T;
export function setSearchParam(
  params: URLSearchParams, key: string, value: string, defaultValue?: string,
): URLSearchParams;
```

```ts
export type Evidence =
  | { kind: 'surrogate'; response: PredictionResponse }
  | { kind: 'authoritative'; run: CGEMRunResponse; version?: VersionResponse };
export interface ExportSpec {
  filename: string;
  mediaType: 'application/json' | 'text/csv';
  content: string;
}
export function downloadExport(spec: ExportSpec, documentRef?: Document): void;
```

```ts
export const queryKeys = {
  health: (url: string) => ['cgem', url, 'health'] as const,
  version: (url: string) => ['cgem', url, 'version'] as const,
  sensitivity: (url: string, target: TargetName | null) =>
    ['cgem', url, 'sensitivity', target] as const,
  predict: (url: string) => ['cgem', url, 'predict'] as const,
  sweep: (url: string) => ['cgem', url, 'sweep'] as const,
  run: (url: string) => ['cgem', url, 'run-cgem'] as const,
};
```

```ts
export interface BaseChartProps {
  option: EChartsOption;
  height?: number;
  className?: string;
  accessibleName: string;
  accessibleSummary: string;
}
```

```ts
export default defineConfig({
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1 --port 4173',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: !process.env.CI,
  },
  projects: [390, 768, 1024, 1440].map((width) => ({
    name: width === 390 ? 'mobile-390' : width === 768 ? 'tablet-768' : `desktop-${width}`,
    use: { viewport: { width, height: 900 } },
  })),
});
```

---

## Phase 1 Completion Gate

- Eight routes remain valid and share one registry.
- Exact desktop/tablet/mobile modes and four viewport overflow checks pass.
- Drawer, search, selectors, help, refresh, exports, and all visible controls are keyboard/focus safe; Notifications is absent.
- URL state round-trips and back/forward restores controls.
- Result pages show truthful source/calibration/OOD/model evidence.
- API URLs isolate all remote caches and mutations.
- Generated types are deterministic and CI rejects drift.
- Canvas charts have accessible names and data-derived summaries.
- Unit, static, build, Playwright, generated-contract, backend, and protected-contract gates pass.
