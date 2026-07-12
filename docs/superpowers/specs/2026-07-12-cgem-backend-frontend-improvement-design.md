# CGEM Backend and Frontend Improvement Proposal

**Date:** 2026-07-12

**Status:** Phase 0 implemented; Phases 1–3 proposed

**Scope:** FastAPI/ML service, React application, shared contracts, delivery pipeline, and product-facing scientific communication

**Protected boundaries:** Do not modify `src/cgem.f`, the public `cgem_wrapper.run_cgem_for_profile` / `PilotConfig` signatures, or the `/run-cgem` v2.2.0 response shape without deliberate contract-test updates.

## Executive conclusion

CGEM already has unusually strong research foundations: the FAA Fortran artifact is isolated, the extension layer has explicit OOD and conformal-uncertainty machinery, the data and model provenance are documented, and the React application exposes both the fast surrogate and authoritative model paths.

The next release should be a **reliability-first stabilization release**, not a feature-expansion release. Several current issues can make the same maneuver produce differently framed predictions across pages, make category-specific uncertainty silently fall back to a global interval, or make demonstration data look authoritative. The mobile shell is also unusable at a 390 px viewport, while the API and frontend are largely absent from CI at their integration boundary.

The proposed product direction is a **flight-test evidence console**: an industrial, instrument-like interface where every result visibly carries its source, input configuration, calibration scope, OOD state, and model artifact identity. Keep the strongest cockpit-display cues, but reduce game-like chrome, generic glass cards, and decorative motion in favor of scientific legibility.

## Review basis

This proposal is based on:

- Repository guidance, architecture documents, current roadmaps, recent commits, API schemas, model state construction, wrapper behavior, frontend routes, service hooks, charts, settings, and UI primitives.
- The current [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md), applied to the frontend source.
- A production frontend build and static checks:
  - `npm run type-check`: pass.
  - `npm run lint`: pass.
  - `npm run build`: pass, with one 1.70 MB JavaScript chunk (541 KB gzip) and Vite's chunk-size warning.
- Rendered checks at 1440 × 1000 and 390 × 844. Desktop is coherent; the mobile viewport retains the 260 px fixed sidebar and leaves only a narrow strip for the application content.
- `tests/test_contract.py`: 6 passing tests in the available environment.
- The complete backend suite could not be validated locally because the active Python environment lacks the API/ML development extras (`fastapi`, `xgboost`, `ruff`, and `mypy`). Sixty dependency-light tests passed before imports requiring those extras failed. These are environment failures, not evidence of code regressions.

## Current strengths to preserve

1. **Authoritative-core separation.** `src/cgem.f` and the compiled binary remain distinct from the additive Python/ML layer.
2. **Two explicit inference paths.** `/predict` provides fast surrogate output with uncertainty and OOD status; `/run-cgem` invokes the authoritative binary.
3. **Reproducibility signals.** The dataset seed, binary SHA, model cards, datasheets, OpenAPI document, and publication artifacts are already first-class project concepts.
4. **A useful maneuver corpus.** The 72-record generated maneuver catalog gives the frontend a rich exploration surface.
5. **A promising visual identity.** Amber/phosphor telemetry, condensed headings, tabular numerals, and instrument bezels suit the aerospace context when used with restraint.
6. **Protected downstream contracts.** The pulse-sim import and JSON boundaries are documented and have explicit regression tests.

## Highest-priority findings

| Priority | Finding | Evidence | Why it matters |
|---|---|---|---|
| P0 | Named maneuver inference is not canonical across callers. | `cgem_ext/api/main.py:90-140`; `frontend/src/pages/SimulatorPage.tsx:109-120` | Prediction/Batch submit only a maneuver ID, while Simulator supplies catalog descriptors. The API trusts all supplied descriptors and otherwise derives dataset descriptors. The same maneuver/configuration can therefore enter the surrogate with different feature values. |
| P0 | Every API prediction is assigned the conformal stratum `unregistered`. | `cgem_ext/api/main.py:123-139`; `cgem_ext/surrogate/conformal.py:186-202` | Registered maneuvers do not receive their actual category-specific Mondrian interval. The interface implies category-stratified calibration while deployment uses the global fallback. |
| P0 | Batch risk ordering uses `P(event) × conditional time` as an ascending event time. | `frontend/src/pages/BatchPage.tsx:52-59, 113-136` | A very low event probability produces a near-zero product and can sort ahead of a likely early event. Probability and conditional event time are separate axes and should not be collapsed into this ordering. |
| P0 | Offline heuristic physiology can appear as a normal dashboard result. | `frontend/src/pages/DashboardPage.tsx:229-249`; `frontend/src/services/mockData.ts:253-411` | The fallback is an invented demonstration model, not CGEM. API status alone is not a sufficient provenance distinction for a scientific tool. |
| P0 | The application shell is not responsive. | `frontend/src/components/layout/MainLayout.tsx:15-61`; `frontend/src/components/layout/Sidebar.tsx:100-248` | At 390 px, the fixed 260 px sidebar remains open and the main content becomes a clipped sliver. |
| P0 | Most FastAPI tests are excluded by CI. | `tests/test_api.py:47-193`; `.github/workflows/ci.yml:57` | All 11 API tests carry `needs_cgem_binary`, while the matrix runs `not needs_cgem_binary`. Health, version, predict, sweep, sensitivity, and most schema behavior therefore do not run in the normal test matrix. |
| P0 | Successful `/run-cgem` calls leak temporary directories and run synchronously in an async route. | `cgem_wrapper.py:498-526`; `cgem_ext/api/main.py:292-352` | The wrapper intentionally returns a persistent run directory; the HTTP layer ignores it. Repeated service calls accumulate files. The subprocess also blocks the event loop and has no timeout or concurrency limit. |
| P0 | Dashboard presets advertise parameters that are inactive or not sent. | `frontend/src/pages/DashboardPage.tsx:71-124, 199-227`; `cgem_ext/api/schemas.py:46-68`; `cgem_wrapper.py:211-260` | Presets mention seat optimization, dehydration, and fatigue-like degradation, but seat tilt is absent from the HTTP request schema and dehydration is applied by the wrapper only for custom subjects. The displayed comparison can imply effects that the authoritative run did not model. |
| P1 | Settings promise behavior that is not wired through the app. | `frontend/src/pages/SettingsPage.tsx:104-128`; `frontend/src/pages/SimulatorPage.tsx:48-58, 303-314`; `frontend/src/pages/PredictionPage.tsx:105-119` | Simulator and Prediction use local hard-coded defaults, while color and unit preferences are recorded but mostly not applied. |
| P0 | Scientific terms, provenance, and risk language are inconsistent. | `frontend/src/pages/SimulatorPage.tsx:131-136, 275-299`; `frontend/src/pages/OverviewPage.tsx:48-76`; `frontend/src/components/charts/GForceLineChart.tsx:170-186` | A conformal prediction interval is called a “95% CI,” fixed G bands are called a “Safe Limit,” several unversioned heuristics produce “High Risk” or “G-LOC” badges, and Overview describes the whole mixed/conceptual catalog as in-flight measurements. These labels can overstate what the model and source data support. |
| P1 | The interface mixes two design systems and includes dead controls. | `frontend/src/index.css:88-269, 365-448`; `frontend/src/components/layout/TopBar.tsx:108-184`; `frontend/src/pages/DashboardPage.tsx:345-460` | Legacy blue glassmorphism and newer HUD styling coexist. Global search, top-bar export/notifications/help, and Dashboard “Export All” appear interactive but do not perform their advertised action. |
| P1 | Frontend/API type synchronization is manual and not checked. | `frontend/src/services/types.ts:1-12`; `scripts/export_openapi.py:1-32` | Python API tests cannot detect drift in handwritten TypeScript interfaces. |
| P2 | Initial frontend payload is unnecessarily large. | `frontend/src/components/charts/BaseChart.tsx:8-15`; current build output | All routes and the full ECharts namespace load in one 541 KB gzip entry chunk. |

Priority definitions: **P0** blocks a trustworthy release, **P1** belongs in the next product-quality release, and **P2** is optimization or expansion after correctness is locked.

## Three possible strategies

### 1. Reliability-first stabilization — recommended

Fix the shared inference contract, scientific semantics, CI coverage, subprocess lifecycle, responsive shell, and result provenance before adding new workflows.

**Advantages:** removes the most consequential correctness risks; makes later visual and operational work cheaper; aligns with publication/research credibility.

**Trade-off:** fewer visible new features in the first release.

### 2. Frontend showcase first

Polish the cockpit aesthetic, add exports, refine charts, and make the simulator presentation-ready while leaving most service internals unchanged.

**Advantages:** fastest visible improvement for demonstrations.

**Trade-off:** preserves inconsistent feature resolution, uncertainty scope, test gaps, and misleading fallback behavior. This is not recommended for a research-facing release.

### 3. Backend platform hardening first

Artifactize models, add observability, container hardening, concurrency controls, and deployment automation before changing the UI.

**Advantages:** strongest service-operability story.

**Trade-off:** leaves the current mobile and interpretation problems in place; users can still misunderstand technically correct results.

## Recommended target architecture

### One canonical inference context

Introduce a small domain layer between Pydantic schemas and model objects:

```text
HTTP request
  -> validated named-maneuver OR inline-descriptor input
  -> canonical maneuver/pilot resolver
  -> resolved feature row + maneuver category + catalog version
  -> OOD + surrogate + conformal inference
  -> response with prediction provenance
```

Use a discriminated input shape:

- **Named input:** accepts a registered maneuver ID only. The server derives all maneuver features and the category from the same function used to build the training dataset.
- **Inline input:** accepts all required descriptors, never a partial mixture. Its calibration scope must be explicit. If no valid category is supplied, return a global interval and label it `calibration_scope: global`.

Do not let a request combine a maneuver name with caller-supplied descriptors. This removes the current ambiguity instead of choosing a silent precedence rule.

Although `/predict` is not one of the two explicitly protected contracts, migrate this request shape through a documented deprecation window or a versioned endpoint rather than silently breaking external clients.

Additive response metadata should include the resolved maneuver/category, input/catalog schema versions, calibration scope, and artifact ID. Existing consumers can ignore these fields.

### Versioned model bundle, lightweight API startup

Training five XGBoost models during every API startup is acceptable for development but weak for deployment and reproducibility. Produce a versioned artifact bundle offline:

```text
models/<artifact-id>/
  manifest.json
  surrogates/
  conformal/
  ood/
```

The manifest should bind the package version, Git commit, dataset SHA, binary SHA, feature schema, target list, seeds, hyperparameters, calibration method, and validation metrics. The API loads the bundle, verifies hashes, and refuses readiness when incompatible. Keep a deliberate development-only `CGEM_TRAIN_ON_STARTUP=1` path if useful.

### Bounded authoritative execution

Run CGEM subprocess calls in a bounded worker pool rather than the event loop. Give each call a timeout, clean its run directory in `finally`, and report a stable public error code without exposing internal paths. If inspection artifacts are needed, make retention an explicit debug option with a TTL—not the default HTTP behavior.

### Frontend as a flight-test evidence console

Organize the primary workflow around the user's scientific question:

```text
Explore maneuver -> Predict with UQ -> Verify with Fortran -> Compare/export
```

Suggested information architecture:

- **Explore:** merge the strongest parts of Overview and Simulator—maneuver library, trace, descriptor provenance, and a clearly marked attitude illustration.
- **Run:** combine parameter configuration, surrogate output, authoritative verification, and aligned result comparison.
- **Compare:** batch analysis with two-dimensional risk ordering, filters, and reproducible export.
- **Explain:** sensitivity, model limitations, calibration, and maneuver notes.
- **System:** connection, artifact/catalog identity, preferences, and project information.

This reduces eight top-level destinations to four workflows plus System without deleting capabilities.

## Backend improvement backlog

| ID | Priority | Improvement | Acceptance criteria | Effort |
|---|---|---|---|---|
| B1 | P0 | Canonical named/inline inference resolver | Same maneuver + pilot config produces identical resolved features from every page; named inputs carry the real category; partial mixed inputs return 422; tests cover category-specific and global intervals. | M |
| B2 | P0 | Correct API test markers and inject test state | Non-binary API tests run on Python 3.10–3.12 in CI without a 30 s model fit; only `/run-cgem` execution remains binary-gated; schema and error cases are covered. | M |
| B3 | P0 | Harden `/run-cgem` lifecycle | No successful-call temp-directory leak; subprocess timeout; bounded concurrency; event loop remains responsive; public errors have stable codes. | M |
| B4 | P0 | Tighten request validation | `countermeasures_label` is an enum/Literal; unknown maneuvers are 404/422 rather than 500; numerical limits reflect model semantics; standard profiles clearly reject or ignore custom-only fields. | S–M |
| B5 | P1 | Replace startup training with artifact loading | API readiness after artifact load is deterministic; manifest/hash mismatch fails closed; development retraining remains explicit. | L |
| B6 | P1 | Vectorize `/sweep` and preserve item identity | Models receive batched feature matrices; every result echoes a stable request/maneuver ID; a 10,000-item limit is justified by measured latency and memory or reduced. | M |
| B7 | P1 | Separate liveness/readiness and add provenance | `/livez` checks process health; `/readyz` verifies models, calibration, dataset, and executable; `/version` adds artifact, feature-schema, catalog, and dataset hashes. | M |
| B8 | P1 | Structured logs and metrics | Request ID, endpoint, duration, artifact ID, OOD result, CGEM timeout/failure, queue depth, and response status are observable without logging sensitive payloads. | M |
| B9 | P1 | Environment-specific API security | CORS comes from configuration; local mode stays convenient; network deployments define allowed origins, proxy/auth policy, request-size limits, and rate/concurrency limits. | S–M |
| B10 | P2 | Deterministic CGEM result cache | Canonical input hash + binary SHA key the cache; hit/miss is visible; cache cannot cross binary/config versions. | M |
| B11 | P2 | Container/release hardening | Multi-stage wheel build, non-root runtime, pinned lock/digests, Docker build smoke test, SBOM/image scan, and graceful shutdown are in CI. | M |

Effort guide: **S** ≤2 engineering days, **M** about 3–5 days, **L** about 1–2 weeks, including tests and documentation.

## Frontend improvement backlog

| ID | Priority | Improvement | Acceptance criteria | Effort |
|---|---|---|---|---|
| F1 | P0 | Responsive application shell | No horizontal overflow at 390, 768, 1024, or 1440 px; mobile uses a labeled menu button and modal drawer; header/content never sit under navigation; touch targets are at least 44 px. | M |
| F2 | P0 | One pilot/preferences source | Simulator, Prediction, Dashboard, and Batch use one validated pilot-config builder backed by preferences; settings claims match behavior; changing API URL scopes/invalidates React Query caches. | M |
| F3 | P0 | Remove implicit mock physiology | Offline scientific pages show an unavailable state. If demo mode is retained, it requires explicit opt-in and persistent `DEMO / HEURISTIC — NOT CGEM` labeling; demo exports are disabled or watermarked. | S–M |
| F4 | P0 | Correct probability/time and uncertainty semantics | Batch ranks by event probability descending then conditional time ascending (or a visible risk matrix); conformal results say “95% prediction interval”; conditional time and `P(event) × time` are never presented as interchangeable. | M |
| F5 | P0 | Replace universal “safe/risk” verdicts and expose source quality | Fixed G thresholds become contextual reference bands; heuristic risk badges become neutral load-severity summaries or a documented/versioned policy; measured, literature-encoded, and conceptual profiles are visibly distinguished; the attitude proxy is explicitly non-kinematic; research-use limitation is visible near results, not only on About. | M |
| F6 | P1 | Consolidate the visual system | One token set and component grammar; migrate remaining blue glass cards; amber is selection/time, cyan is uncertainty, green is verified/available, red is observed/predicted adverse event; remove decorative controls and excessive glow. | M–L |
| F7 | P1 | Complete accessibility pass | Skip link and semantic main region; associated labels; `aria-label` on icon buttons; keyboard-operable maneuver selector; visible `focus-visible`; `aria-live` for async results; reduced-motion mode; AA contrast for small text. | M |
| F8 | P1 | Make state deep-linkable | Maneuver, pilot preset, analysis target, batch sort/filter, chart mode, and selected chart use URL parameters where sharing/reloading is valuable. | M |
| F9 | P1 | Implement or remove every control | Global search searches maneuvers; export produces a documented artifact; Help opens relevant guidance. Notifications remain absent until a real notification model exists. | S–M |
| F10 | P1 | Generate API types | Commit `openapi-typescript` as a dev dependency; generate into a dedicated file; CI regenerates OpenAPI + TS and fails on drift; handwritten presentation types remain separate. | S–M |
| F11 | P1 | Scientific chart accessibility/export | Each chart has an accessible name/summary and optional data table; SVG/PNG export includes model/data/input provenance; chart labels are not clipped; color is never the only encoding. | M |
| F12 | P2 | Route and ECharts code splitting | Lazy-load route groups; use modular `echarts/core`; initial JavaScript target ≤250 KB gzip; no Vite chunk warning; loading/error boundaries preserve layout. | M |
| F13 | P2 | Large-list efficiency | Maneuver library and 72-row result table use `content-visibility`, pagination, or virtualization where measured; filtering remains keyboard accessible. | S–M |

### Specific interface-guideline findings to close

- `frontend/src/components/layout/Sidebar.tsx:132` — icon-only collapse button lacks an accessible name.
- `frontend/src/components/layout/TopBar.tsx:112` — global search lacks an associated label/name and currently has no search behavior.
- `frontend/src/components/layout/TopBar.tsx:158-184` — Export, Notifications, and Help are dead icon controls and lack `aria-label`.
- `frontend/src/components/ui/ProfileSelector.tsx:115-221` — custom dropdown lacks `aria-expanded`, listbox semantics, Escape/arrow-key handling, and a labeled search field.
- `frontend/src/components/hud/GTracePlayer.tsx:197-205` — timeline range input has no accessible label.
- `frontend/src/pages/SettingsPage.tsx:58-80, 104-121` — visual labels are not connected to controls; URL uses `type="text"`; numerical inputs lack domain limits and field names.
- `frontend/src/components/charts/BaseChart.tsx:88-93` — canvas-only chart has no accessible description or tabular alternative.
- `frontend/src/index.css` and motion components — no `prefers-reduced-motion` treatment; many `transition-all` declarations animate unspecified properties.
- `frontend/src/index.css:53-54` — `--hud-ink-faint` has about 3.02:1 contrast on the HUD background, below AA for the many 10–11 px labels that use it.

## Visual design direction

### Concept: Flight-Test Evidence Console

The interface should feel like a calibrated research instrument, not a tactical game HUD and not a generic SaaS dashboard.

- **Typography:** keep self-hosted IBM Plex Sans Condensed for headings and IBM Plex Mono for telemetry/numerals. Use normal sentence-case body copy; reserve uppercase tracking for short instrument labels.
- **Palette:** matte graphite dominates. Amber marks the active sample/selection, cyan carries prediction intervals, green means verified/available, and red is reserved for adverse modeled events. Neutral text—not color—does most explanatory work.
- **Composition:** use a stable evidence rail across result pages with model artifact, binary SHA, dataset/catalog hash, source (`surrogate`, `Fortran`, or explicit demo), OOD state, and calibration scope.
- **Motion:** one restrained page-entry sequence and functional playhead motion. Remove per-card entrance animation, pulsing labels, and scanline sweep when they do not convey state. Honor reduced-motion preferences.
- **Surfaces:** replace the mix of translucent blue glass and HUD bezels with solid, low-reflection instrument panels. Use borders, spacing, and typographic hierarchy before shadow/glow.
- **Memorable element:** a synchronized **evidence timeline** aligning Gz, G-effective response, greyout/blackout/G-LOC events, and uncertainty/provenance. This is both distinctive and scientifically useful.

### Chart changes

1. Replace the generic radar risk chart with aligned bars or small multiples; they support accurate comparisons and accessible tabular equivalents.
2. Show probability and conditional time together as a two-dimensional event card, not a single synthetic score.
3. Label threshold lines as reference conditions with the assumed training/countermeasure context.
4. Add visible source badges to charts and include source/config/artifact metadata in exports.
5. Preserve zoom/tooltips, but add keyboard-accessible summaries and a data-table toggle.

## Shared contract and data-flow improvements

1. **Catalog identity:** have `scripts/export_maneuvers_json.py` emit a catalog schema version and SHA. Add the same hash to `/version`; the frontend warns on mismatch.
2. **One configuration builder:** centralize pilot defaults, countermeasure label derivation, standard-vs-custom constraints, and request serialization. Pages should not construct request bodies independently.
3. **Query scoping:** include API base URL and artifact/catalog identity in appropriate React Query keys. Clear or invalidate caches after connection changes.
4. **Response provenance:** echo a request ID and resolved input summary from `/predict` and `/sweep`; never rely only on array position to join batch results.
5. **Terminology registry:** define user-facing names and units once (`Gz`, G-effective, conditional event time, prediction interval, OOD/abstention). Generate table headings and tooltips from it.

## Test and delivery plan

### Backend

- Unit-test canonical resolution independently of model training.
- Add a lightweight fake `AppState`/dependency override for endpoint tests.
- Split markers into meaningful capabilities such as `needs_cgem_binary`, `needs_ml`, and `slow`; do not binary-gate health or pure surrogate API tests.
- Add equivalence tests proving all frontend request paths resolve to the same features.
- Test unknown maneuvers, invalid countermeasure labels, partial descriptors, global-vs-category calibration scope, timeout, temp cleanup, and concurrent `/run-cgem` behavior.
- Keep the protected pulse-sim import and JSON contract gates.

### Frontend

- Add Vitest + Testing Library for request builders, adapters, probability/time ordering, preference behavior, and accessible controls.
- Add MSW-backed component/integration tests for online, degraded, OOD, validation-error, and explicit demo states.
- Add Playwright golden paths for Explore -> Predict -> Verify -> Compare at 390, 768, and 1440 px.
- Run axe checks and keyboard-only paths in CI.
- Add visual regression snapshots for the shell, result provenance rail, and dense tables.
- Enforce an initial-bundle budget and fail CI when generated catalog/OpenAPI/TS files drift.

### CI jobs to add

1. `frontend-static`: `npm ci`, type-check, lint, unit tests, build, bundle budget.
2. `frontend-e2e`: built frontend + mocked API for deterministic responsive/a11y paths.
3. `api-unit`: dependency-injected endpoint tests without binary or model training.
4. `api-ml-integration`: artifact-backed predict/sweep/calibration tests.
5. `generated-contracts`: regenerate maneuver catalog, OpenAPI, and TS types; require a clean diff.
6. `container-smoke`: build image, wait for readiness, call version/predict, and verify non-root execution.

## Phased roadmap

### Phase 0 — Trust contract (approximately 3–5 days)

- [x] B1 canonical inference resolver and real maneuver category.
- [x] B2 API test marker/state-injection correction.
- [x] B3 temp cleanup, subprocess timeout, and bounded execution.
- [x] F2 one pilot-config builder.
- [x] F3 explicit offline/demo behavior.
- [x] F4 probability/time and prediction-interval terminology.
- [x] F5 contextual scientific language and profile-source quality.

**Exit:** identical named requests resolve identically from all pages; no silent global interval for registered maneuvers; non-binary API tests run in CI; no successful-run temp leak; demo output cannot be mistaken for CGEM; results use accurate uncertainty, source, and intended-use language.

### Phase 1 — Usable research instrument (approximately 1–2 weeks)

- F1 responsive shell.
- F6 visual-system consolidation.
- F7 accessibility.
- F8 URL-backed shareable state.
- F9 implement/remove dead controls.
- F10 generated API types.

**Exit:** complete keyboard path; AA small-text contrast; usable 390/768/1440 layouts; every visible control works; every result shows source and calibration scope.

### Phase 2 — Deployable service (approximately 1–2 weeks)

- B5 artifact loading.
- B6 vectorized identity-preserving sweep.
- B7 liveness/readiness and full provenance.
- B8 logging/metrics.
- B9 environment security.
- B11 container/release hardening.
- F12 route/chart code splitting.

**Exit:** deterministic artifact-backed startup; observable bounded execution; deployment-specific CORS/security; container smoke test; initial JavaScript ≤250 KB gzip.

### Phase 3 — Scientific workflow enhancements (after stabilization)

- Publication-grade export/report bundle.
- Saved comparison scenarios with explicit schema/version.
- Multi-run difference view (surrogate vs Fortran, or pilot A vs B).
- Calibration/OOD explorer tied to the model card.
- Optional cached authoritative runs.

## Release-level definition of done

- A named maneuver has one canonical server-resolved feature representation and category.
- Registered maneuvers use the intended category-specific conformal layer; global fallback is explicit.
- Probability, conditional event time, and prediction interval are distinct in the API copy and UI.
- No heuristic/demo output appears without persistent provenance labeling.
- No supported viewport has horizontal clipping; mobile navigation is operable.
- Every interactive control works, is keyboard reachable, and has a visible focus state/accessibility name.
- API, frontend, generated contracts, and container smoke tests run in CI.
- `/run-cgem` has bounded concurrency, timeout, cleanup, and observable failures.
- Production startup loads a versioned verified artifact rather than retraining implicitly.
- The initial frontend bundle meets the agreed performance budget.

## Explicit non-goals for these phases

- Modifying or re-implementing the FAA Fortran physiology core.
- Breaking the pulse-sim Python or `/run-cgem` JSON contracts.
- Real-time sensor ingestion, EHR/PHI workflows, clinical decision support, VR/AR, reinforcement learning, or personalized medical recommendations.
- Authentication/role management for a strictly local research deployment; add it only when a network deployment has a defined threat model.
- New risk heuristics without validation, versioning, and an explicit intended-use statement.

## Recommended first implementation tickets

1. Write failing API tests for canonical named-maneuver resolution and category-specific conformal scope.
2. Introduce the named-vs-inline request resolver and make all frontend callers send named IDs only for catalog maneuvers.
3. Correct API test markers and add injectable lightweight state.
4. Clean `/run-cgem` directories in `finally`; add timeout and bounded worker execution.
5. Remove implicit Dashboard mock fallback or place it behind explicit demo mode.
6. Centralize and validate pilot preferences; wire all pages to it.
7. Correct Batch ordering and all “CI” / “safe” / “risk” copy.
8. Rebuild the shell as responsive grid + mobile drawer and add viewport tests.
9. Add frontend CI, accessible labels/focus/reduced-motion, and OpenAPI type generation.
10. Consolidate the Flight-Test Evidence Console tokens/components, then code-split ECharts routes.

This order intentionally fixes the data and uncertainty contract before refining the presentation built on top of it.
