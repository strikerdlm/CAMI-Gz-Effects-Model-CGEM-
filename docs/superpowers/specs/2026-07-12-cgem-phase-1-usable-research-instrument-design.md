# CGEM Phase 1 Usable Research Instrument Design

**Date:** 2026-07-12

**Status:** Approved for implementation planning

**Scope:** F1 responsive shell, F6 visual-system consolidation, F7 accessibility, F8 URL-backed shareable state, F9 functional controls, and F10 generated API types.

**Base:** Phase 0 trust-contract implementation plus `origin/main` kinematic-attitude updates, through merge commit `76347c0`.

## Objective

Turn the existing CGEM frontend into a usable research instrument without changing physiological behavior, the protected FAA Fortran core, public wrapper signatures, or the `/run-cgem` response contract. Phase 1 must deliver a complete keyboard path, AA small-text contrast, usable layouts at 390, 768, 1024, and 1440 px, working visible controls, shareable scientific state, and visible result provenance.

## Delivery strategy

Use a shell-first layered implementation. Establish responsive layout, navigation, semantic landmarks, accessibility primitives, and visual tokens before migrating page interactions. Then add URL state, functional controls, evidence presentation, generated contracts, and end-to-end verification.

Keep existing route URLs and add redirects only when necessary. Do not combine Phase 1 with a wholesale information-architecture rewrite. Existing bookmarks and links must continue to work.

## Application architecture

### Shared route registry

Create one typed route registry consumed by the application router, Sidebar, TopBar, global search, contextual help, and breadcrumbs. Each entry carries path, label, workflow group, description, icon identity, and search keywords. The registry prevents duplicated navigation metadata and inconsistent page titles.

The current eight URLs remain:

- `/` — Explore / overview.
- `/simulator` — kinematic maneuver playback and fast prediction.
- `/prediction` — surrogate prediction and authoritative verification.
- `/dashboard` — authoritative result visualization.
- `/batch` — maneuver comparison.
- `/analysis` — explanations and sensitivity.
- `/settings` — connection and preferences.
- `/about` — limitations, provenance, and project information.

Navigation groups emphasize the workflow without changing routes: Explore, Predict/Verify, Compare, Explain, and System.

### Responsive shell

`MainLayout` owns shell state and renders three layout modes:

- Desktop, at 1024 px and above: persistent evidence-console sidebar and top bar.
- Tablet, from 768 through 1023 px: compact navigation rail with protected content width.
- Mobile, below 768 px: no persistent sidebar; a labeled menu button opens a modal navigation drawer.

The shell provides a skip link, semantic `<header>`, `<nav>`, and `<main>` landmarks, stable content offsets, and a single content-width/overflow policy. No page may create document-level horizontal overflow. Dense tables may scroll inside a bounded region.

The mobile drawer traps focus, closes on Escape and route selection, makes background content inert while open, and restores focus to the menu button on close. Primary mobile controls and navigation targets are at least 44 by 44 CSS pixels.

## Visual system

The visual direction remains **Flight-Test Evidence Console**: a calibrated research instrument rather than a game HUD or generic SaaS dashboard.

- Matte graphite is the dominant surface.
- Amber denotes current selection and conditional time.
- Cyan denotes prediction intervals and uncertainty.
- Green denotes verified or available state.
- Red is reserved for observed or predicted adverse events, not decoration.
- IBM Plex Sans Condensed remains the heading face; IBM Plex Mono remains the telemetry face.

Consolidate surface, border, text, spacing, focus, and state tokens in CSS custom properties. Replace remaining blue glass-card variants in files touched by Phase 1 with solid low-reflection instrument panels. Prefer borders, spacing, and typography over glow and shadow.

Raise the faint telemetry text token to at least WCAG AA contrast for the small text sizes where it is used. Add a consistent `focus-visible` ring that remains distinguishable on graphite, amber, cyan, and green states.

Reduced-motion mode disables scanline sweep, decorative pulsing, page/card entrance movement, and unspecified `transition-all`. Functional playhead motion may remain when the user directly operates playback.

## Result evidence rail

Result-oriented pages use a shared evidence rail. It renders fields only when the response or authoritative run supplies them and never fabricates provenance.

For surrogate results it includes:

- source: surrogate;
- resolved maneuver;
- maneuver category;
- calibration scope;
- OOD/in-envelope state;
- model version;
- CGEM binary SHA prefix.

For authoritative results it includes:

- source: Fortran / authoritative CGEM;
- maneuver;
- pilot profile;
- binary identity when `/version` is available;
- research-use limitation.

The rail is compact on mobile, uses text in addition to color, and exposes an accessible summary.

## URL-backed state

Create a small typed URL-state layer with pure parse and serialization functions. Invalid values fall back to documented defaults without creating unsupported API inputs. Material fallback is announced when it changes the user's requested state.

Persist these values in search parameters:

- Overview and Simulator: maneuver ID.
- Prediction: maneuver ID, pilot profile, and `view=surrogate|authoritative|comparison`.
- Batch: sort target, `direction=asc|desc`, OOD filter, and maneuver-category filter.
- Analysis: target and `view=explanation|sensitivity`.
- Dashboard: maneuver ID, pilot preset, chart, and grid/single layout mode.

Search-parameter updates use replace for transient UI changes and push for meaningful navigational selections. Back/forward navigation restores the visible control state. Defaults are omitted from canonical URLs where omission is unambiguous.

## Functional controls

Every visible control must perform a documented action or be removed.

### Global maneuver search

TopBar search operates as a keyboard-accessible combobox over the registered maneuver catalog. It searches ID, display label, category, aircraft, and tags. Arrow keys move through results, Enter navigates to the selected maneuver, Escape closes results, and focus remains predictable. Navigation targets the Simulator with the maneuver ID in the URL.

### Top-bar actions

- Refresh retains API health/version refetch behavior, has an accessible name, exposes pending state, and announces completion.
- Help navigates to the relevant About limitations section for the current workflow.
- Notifications are removed because no notification model exists.
- Export appears only where real result data exists. A shared result-action context lets the active page register one export payload and filename. Prediction and Dashboard export provenance-bearing JSON; Batch exports provenance-bearing CSV. The action is absent when the active page has no real result payload.

### Profile selector

`ProfileSelector` becomes a keyboard-operable combobox/listbox with an associated label, `aria-expanded`, `aria-controls`, active-descendant or roving-focus semantics, arrow-key navigation, Enter selection, Escape dismissal, search-field naming, and focus restoration.

### API URL changes

React Query keys include the current API base URL for remote data. Updating the URL invalidates or separates cached health, version, prediction, sweep, sensitivity, and authoritative-run data so results from two backends cannot mix.

## Accessibility requirements

Phase 1 provides:

- skip link and semantic landmarks;
- associated labels and names for inputs and icon buttons;
- complete keyboard access to navigation, search, selectors, dialogs, and result actions;
- visible focus for all interactive elements;
- `aria-live` regions for connection state, prediction completion, validation errors, drawer state where needed, and export completion;
- accessible chart names and concise summaries derived from the visible series and units;
- color-independent OOD, calibration, and source communication;
- reduced-motion behavior;
- AA contrast for small text.

Canvas charts are not made keyboard-interactive unless a meaningful interaction exists. They receive accessible summaries and data alternatives rather than artificial focus stops.

## Generated API contracts

Separate generated wire types from handwritten presentation/domain types.

- Generate OpenAPI-derived TypeScript into `src/services/generated/api.ts`.
- Keep UI-only aliases, adapters, and chart types outside the generated file.
- Add deterministic scripts to regenerate OpenAPI and TypeScript.
- CI regenerates both artifacts and fails on a dirty diff.
- Application imports migrate to the generated request/response types without changing runtime payload shapes.

The protected `CGEMRunResponse` field set remains unchanged.

## Error and offline behavior

- Offline pages continue to show unavailable states and never substitute heuristic physiology.
- Invalid URL parameters fall back safely; no malformed request reaches the API.
- Search with no matches reports an accessible empty state.
- Export failures produce a stable user-facing error and do not create partial or misleading files.
- Drawer, combobox, and dialog errors cannot strand focus.
- Evidence rails omit unavailable fields rather than inventing placeholder provenance.

## Verification strategy

### Unit and component tests

Use Vitest and Testing Library for:

- route-registry consistency;
- URL parse/serialize round trips and invalid-value fallback;
- responsive shell navigation and mobile drawer focus behavior;
- skip-link and landmark presence;
- global search keyboard behavior and navigation;
- ProfileSelector combobox behavior;
- API-URL query scoping/invalidation;
- removal or implementation of every TopBar control;
- evidence rail rendering for surrogate, authoritative, OOD, and missing-field cases;
- reduced-motion and accessible-label behavior;
- export payload provenance;
- generated-type usage at compile time.

### Browser verification

Add Playwright smoke coverage for 390, 768, 1024, and 1440 px. Test:

- no document-level horizontal overflow;
- mobile drawer open, keyboard traversal, Escape close, and focus restoration;
- keyboard-only Explore → Predict → Verify → Compare navigation;
- URL state survives reload and back/forward navigation;
- visible controls perform their actions;
- core pages expose landmarks and accessible names.

Use deterministic mocked API responses for browser tests. Live Fortran execution remains covered by backend contract tests, not frontend E2E.

### Static and contract gates

Required gates are:

- `npm test -- --run`;
- `npm run type-check`;
- `npm run lint`;
- `npm run build`;
- Playwright Phase 1 smoke suite;
- generated-contract clean-diff check;
- existing backend non-binary and protected contract suites.

The existing Vite chunk warning may remain. The Phase 2 initial-JavaScript target of 250 KB gzip is explicitly outside Phase 1.

## Delivery slices

1. Route registry, tokens, semantic landmarks, and responsive shell.
2. Mobile drawer, keyboard navigation, reduced motion, and contrast.
3. URL-state utilities and page migrations.
4. Global search, ProfileSelector, contextual help, refresh state, and dead-control removal.
5. Evidence rail and provenance-bearing exports.
6. Generated OpenAPI TypeScript, cache scoping, and drift CI.
7. Playwright responsive/accessibility golden paths and final audit.

Each slice is test-first, independently reviewed, and committed separately.

## Explicit non-goals

- No changes to `src/cgem.f`, compiled binaries, or `gloc_inp.dat` semantics.
- No changes to public `run_cgem_for_profile` or `PilotConfig` signatures.
- No changes to the protected `/run-cgem` response shape.
- No authentication, role management, notifications model, saved scenarios, or publication-grade report bundle.
- No route consolidation that removes current URLs.
- No Phase 2 artifact loading, observability, container hardening, or JavaScript bundle target.

## Completion criteria

- No document-level horizontal overflow at 390, 768, 1024, or 1440 px.
- Mobile navigation is labeled, modal, keyboard-operable, and focus-safe.
- A complete keyboard-only path exists across the primary research workflow.
- Small text meets AA contrast and reduced-motion preferences are honored.
- Every visible control works or has been removed.
- Shareable page state restores correctly from valid URLs.
- Every result shows available source and calibration/provenance evidence.
- API URL changes cannot reuse data cached from a different backend.
- Generated API contracts are deterministic and CI rejects drift.
- Frontend unit, static, build, Playwright, generated-contract, and existing backend contract gates pass.
