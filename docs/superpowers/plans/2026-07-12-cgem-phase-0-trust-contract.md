# CGEM Phase 0 Trust Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Make maneuver inference, uncertainty scope, authoritative execution, frontend configuration, offline behavior, and event-risk presentation consistent and testable without changing the FAA core or protected pulse-sim contracts.

**Architecture:** Add a focused API inference resolver that turns either a registered maneuver ID or a complete inline descriptor set into one canonical feature context. Inject API state construction for fast endpoint tests, execute `/run-cgem` through a bounded threadpool with guaranteed HTTP-layer cleanup, and centralize frontend pilot-request construction. Remove implicit mock physiology and present event probability separately from conditional event time.

**Tech Stack:** Python 3.10+, FastAPI, Pydantic v2, pandas/NumPy, pytest, React 19, TypeScript 5.9, TanStack Query, Vitest + Testing Library.

## Global Constraints

- Never modify `src/cgem.f`, the compiled binaries, or `gloc_inp.dat` semantics.
- Preserve `cgem_wrapper.run_cgem_for_profile(profile_id, config)` and `PilotConfig` public signatures.
- Preserve the `/run-cgem` v2.2.0 response shape consumed by pulse-sim.
- Registered maneuver IDs are authoritative: callers may not override their descriptors.
- Inline maneuvers require all three numerical descriptors and use explicit global conformal scope unless a supported category is supplied.
- No heuristic/demo physiology may appear as an authoritative CGEM result.
- Use prediction interval, not confidence interval, for conformal bounds.
- Implement every behavior test-first.

---

## File Structure

**Create**

- `cgem_ext/api/inference.py` — canonical maneuver resolution and inference-row construction.
- `tests/test_api_resolution.py` — resolver tests independent of model training.
- `frontend/src/services/pilotConfig.ts` — one pilot-config builder and countermeasure-label derivation.
- `frontend/src/services/pilotConfig.test.ts` — deterministic request-builder tests.
- `frontend/src/pages/BatchPage.test.ts` — event ranking tests through exported pure helpers.
- `frontend/vitest.config.ts` — frontend unit-test configuration.

**Modify**

- `cgem_ext/api/schemas.py` — validate named versus inline descriptors and add prediction provenance fields.
- `cgem_ext/api/main.py` — consume resolved inference contexts, inject state factory, and harden `/run-cgem`.
- `cgem_wrapper.py` — add a private subprocess timeout without changing public signatures.
- `tests/test_api.py` — use injected fake state for non-binary endpoints and reserve the binary marker for direct CGEM execution.
- `.github/workflows/ci.yml` — add frontend static tests and ensure non-binary API tests run.
- `frontend/package.json` and `frontend/package-lock.json` — add Vitest/testing dependencies and scripts.
- `frontend/src/pages/SimulatorPage.tsx` — use preferences and named maneuver requests only.
- `frontend/src/pages/PredictionPage.tsx` — seed configuration from preferences and the shared builder.
- `frontend/src/pages/DashboardPage.tsx` — remove implicit mock results and inactive preset claims.
- `frontend/src/pages/BatchPage.tsx` — rank probability and conditional time separately.
- `frontend/src/pages/SettingsPage.tsx` — make field constraints and behavior claims accurate.
- `frontend/src/pages/OverviewPage.tsx` — replace universal risk verdict/source claims with load-severity/provenance language.
- `frontend/src/components/charts/GForceLineChart.tsx` — rename the fixed +4 G line as a reference band.
- `frontend/src/components/ui/PredictionTable.tsx` — use prediction-interval terminology.
- `frontend/src/services/types.ts` — mirror additive prediction provenance fields.
- `frontend/src/services/mockData.ts` — retain only as an explicitly documented development fixture; remove all runtime imports.

---

### Task 1: Canonical Maneuver Resolution

**Files:**
- Create: `cgem_ext/api/inference.py`
- Create: `tests/test_api_resolution.py`
- Modify: `cgem_ext/api/schemas.py`
- Modify: `cgem_ext/api/main.py`

**Interfaces:**
- Produces: `ResolvedManeuver`, `resolve_maneuver(md)`, and `build_inference_row(req)`.
- `ResolvedManeuver` fields: `maneuver_id: str`, `category: str`, `g_peak_abs: float`, `dgdt_max_g_per_s: float`, `profile_duration_s: float`, `calibration_scope: Literal["category", "global"]`.
- `build_inference_row(req: PredictionRequest) -> tuple[pd.DataFrame, ResolvedManeuver]`.

- [x] **Step 1: Write resolver validation tests**

```python
def test_named_maneuver_resolves_dataset_descriptors():
    resolved = resolve_maneuver(ManeuverDescriptors(maneuver="high_g_turn"))
    summary = _maneuver_summary("high_g_turn")
    assert resolved.category == summary["maneuver_category"]
    assert resolved.dgdt_max_g_per_s == summary["dgdt_max_g_per_s"]
    assert resolved.calibration_scope == "category"


def test_named_maneuver_rejects_descriptor_override():
    with pytest.raises(ValidationError):
        ManeuverDescriptors(maneuver="high_g_turn", g_peak_abs=7.0,
                            dgdt_max_g_per_s=6.0, profile_duration_s=9.5)


def test_inline_requires_all_descriptors_and_uses_global_scope():
    md = ManeuverDescriptors(g_peak_abs=7.0, dgdt_max_g_per_s=6.0,
                             profile_duration_s=9.5)
    resolved = resolve_maneuver(md)
    assert resolved.maneuver_id == "<inline>"
    assert resolved.category == "unregistered"
    assert resolved.calibration_scope == "global"
```

- [x] **Step 2: Run tests and verify failure**

Run: `python -m pytest tests/test_api_resolution.py -v`

Expected: FAIL because `cgem_ext.api.inference` does not exist and mixed descriptor validation is absent.

- [x] **Step 3: Add named/inline schema validation**

Use a Pydantic `model_validator(mode="after")` on `ManeuverDescriptors`. If `maneuver` is set, require all numerical descriptors to be `None`. If `maneuver` is absent, require all three numerical descriptors. Keep the current JSON field names for compatibility while eliminating ambiguous mixtures.

- [x] **Step 4: Implement `inference.py`**

The resolver must call `_maneuver_summary` for named inputs, translate unknown IDs to `HTTPException(status_code=404, detail="unknown maneuver ...")`, reject non-finite derived features, and assign the catalog category. Inline inputs must use `<inline>`, `unregistered`, and global scope. `build_inference_row` must construct the existing 17-feature-compatible row with `maneuver_category=resolved.category`.

- [x] **Step 5: Replace `_maneuver_features` and `_build_inference_row` in `main.py`**

Import and call `build_inference_row`. Pass the resolved category to every conformal `predict_interval` call. Add `resolved_maneuver`, `maneuver_category`, and `calibration_scope` to `PredictionResponse` and populate them in `_predict_one`.

- [x] **Step 6: Run focused tests**

Run: `python -m pytest tests/test_api_resolution.py tests/test_api.py -m "not needs_cgem_binary" -v`

Expected: resolver tests pass; any remaining API failures identify Task 2 state-fixture work.

- [x] **Step 7: Commit**

```bash
git add cgem_ext/api/inference.py cgem_ext/api/schemas.py cgem_ext/api/main.py tests/test_api_resolution.py
git commit -m "fix(api): canonicalize maneuver inference context"
```

### Task 2: Fast Non-Binary API Tests and CI Coverage

**Files:**
- Modify: `cgem_ext/api/main.py`
- Modify: `tests/test_api.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: `create_app(state_factory: Callable[[], AppState] = AppState.build) -> FastAPI`.
- Test fake models expose `predict`, and censored fakes also expose `predict_event_probability`.
- Fake conformal exposes `predict_interval`; fake OOD objects expose `score` and `is_in_envelope`.

- [x] **Step 1: Write a test proving injected state avoids `AppState.build`**

Patch `AppState.build` to raise, construct `create_app(state_factory=lambda: fake_state)`, open `TestClient`, and assert `/healthz`, `/version`, `/predict`, `/sweep`, and `/sensitivity/hlap_min` succeed.

- [x] **Step 2: Run the focused test and verify failure**

Run: `python -m pytest tests/test_api.py::test_non_binary_endpoints_use_injected_state -v`

Expected: FAIL because `create_app` does not accept `state_factory`.

- [x] **Step 3: Implement state-factory lifespan injection**

Create a private `_lifespan(state_factory)` closure and pass it to FastAPI inside `create_app`. Preserve module-level `app = create_app()`.

- [x] **Step 4: Replace the module fixture with deterministic fake state**

Build one `AppState` using a temporary dataset path, fixed version/hash/seed, five deterministic fake models, fixed conformal intervals, fixed OOD score, and a nine-row sensitivity DataFrame. Keep a separate integration fixture only for tests intentionally marked `needs_ml`.

- [x] **Step 5: Correct markers**

Remove `needs_cgem_binary` from root, health, version, predict, sweep, and sensitivity tests. Retain it only on `/run-cgem` execution/schema tests. Add a regression assertion that named prediction returns its true category and `calibration_scope == "category"`.

- [x] **Step 6: Add frontend CI skeleton**

Add a `frontend-static` job running `npm ci`, `npm run type-check`, `npm run lint`, `npm test -- --run`, and `npm run build`. The job starts once Task 4 adds Vitest.

- [x] **Step 7: Run API tests**

Run: `python -m pytest tests/test_api.py tests/test_api_resolution.py -m "not needs_cgem_binary" -v`

Expected: all selected tests pass without training models or invoking the binary.

- [x] **Step 8: Commit**

```bash
git add cgem_ext/api/main.py tests/test_api.py .github/workflows/ci.yml
git commit -m "test(api): run non-binary endpoints in CI"
```

### Task 3: Bounded and Clean Authoritative Execution

**Files:**
- Modify: `cgem_wrapper.py`
- Modify: `cgem_ext/api/main.py`
- Modify: `tests/test_api.py`

**Interfaces:**
- Private wrapper constant: `CGEM_SUBPROCESS_TIMEOUT_S`, default `30.0`, configurable by environment.
- App state: `app.state.cgem_run_semaphore: asyncio.Semaphore`.
- `/run-cgem` continues returning the exact protected response schema.

- [x] **Step 1: Write temp-cleanup and threadpool tests**

Patch `cgem_wrapper.run_cgem_for_profile` to return a deterministic `CGEMResult` plus a real temporary directory containing a sentinel file. POST `/run-cgem`, assert 200, assert response keys are unchanged, and assert the directory no longer exists. Patch `starlette.concurrency.run_in_threadpool` through the imported API symbol and assert it is awaited.

- [x] **Step 2: Run tests and verify failure**

Run: `python -m pytest tests/test_api.py -k "run_cgem_cleanup or run_cgem_threadpool" -v`

Expected: FAIL because the current endpoint calls synchronously and leaves the directory.

- [x] **Step 3: Add private subprocess timeout**

Read `CGEM_SUBPROCESS_TIMEOUT_S` once with a safe positive-float parser. Pass it to `subprocess.run(..., timeout=timeout_s)` inside `_run_cgem`. Do not alter `run_cgem_for_profile`.

- [x] **Step 4: Add bounded endpoint execution and cleanup**

Create the semaphore from `CGEM_MAX_CONCURRENT_RUNS` (default 2) in `create_app`. Inside the endpoint, use `async with semaphore`, call `await run_in_threadpool(run_cgem_for_profile, ...)`, build the response, and delete `_run_dir` in `finally`. Map `TimeoutExpired` to HTTP 504 and other failures to a stable 500 message without raw filesystem details.

- [x] **Step 5: Run contract and API tests**

Run: `python -m pytest tests/test_contract.py tests/test_api.py -v`

Expected: protected contract tests and new cleanup tests pass.

- [x] **Step 6: Commit**

```bash
git add cgem_wrapper.py cgem_ext/api/main.py tests/test_api.py
git commit -m "fix(api): bound and clean authoritative CGEM runs"
```

### Task 4: Shared Frontend Pilot Configuration

**Files:**
- Create: `frontend/src/services/pilotConfig.ts`
- Create: `frontend/src/services/pilotConfig.test.ts`
- Create: `frontend/vitest.config.ts`
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Modify: `frontend/src/pages/SimulatorPage.tsx`
- Modify: `frontend/src/pages/PredictionPage.tsx`
- Modify: `frontend/src/pages/DashboardPage.tsx`
- Modify: `frontend/src/pages/SettingsPage.tsx`

**Interfaces:**
- `countermeasuresLabel(input) -> CountermeasuresLabel`.
- `pilotConfigFromPrefs(prefs: UserPrefs) -> PilotConfigRequest`.
- `pilotConfigWithOverrides(base, overrides) -> PilotConfigRequest`, which re-derives the label after merging.

- [x] **Step 1: Install and configure Vitest**

Add `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, and `jsdom` as dev dependencies. Add scripts `"test": "vitest"` and `"test:run": "vitest run"`. Configure jsdom and `src/**/*.test.{ts,tsx}` discovery.

- [x] **Step 2: Write failing builder tests**

Cover no countermeasures -> `none`, AGSM only -> `agsm`, active suit + AGSM -> `suit_agsm`, and preferences -> exact `PilotConfigRequest`. Assert standard profiles force custom-only dehydration and G-tolerance values to documented neutral defaults.

- [x] **Step 3: Run tests and verify failure**

Run: `npm test -- --run src/services/pilotConfig.test.ts`

Expected: FAIL because `pilotConfig.ts` does not exist.

- [x] **Step 4: Implement the pure builder**

Derive labels from actual numeric components. Clamp preferences to schema bounds. For `who_profile !== null`, set `g_tolerance_multiplier=1` and `dehydration_level=0`; for custom profiles, preserve validated values.

- [x] **Step 5: Wire pages**

Simulator must call `useUserPrefs`, build its pilot config, and send only `{ maneuver: maneuver.id }`. Prediction initializes from preferences and uses the shared label derivation. Dashboard removes `seat_tilt_deg` and fatigue/dehydration claims from presets and builds requests with the shared helper. Settings adds `id`, `htmlFor`, `name`, `min`, `max`, and `step`, and changes its explanatory copy to name the pages actually using defaults.

- [x] **Step 6: Run frontend checks**

Run: `npm test -- --run && npm run type-check && npm run lint`

Expected: all pass.

- [x] **Step 7: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vitest.config.ts frontend/src/services/pilotConfig.ts frontend/src/services/pilotConfig.test.ts frontend/src/pages/SimulatorPage.tsx frontend/src/pages/PredictionPage.tsx frontend/src/pages/DashboardPage.tsx frontend/src/pages/SettingsPage.tsx
git commit -m "fix(frontend): centralize pilot request configuration"
```

### Task 5: Remove Implicit Mock Physiology

**Files:**
- Modify: `frontend/src/pages/DashboardPage.tsx`
- Modify: `frontend/src/services/mockData.ts`
- Test: `frontend/src/pages/DashboardPage.test.tsx`

**Interfaces:**
- Runtime Dashboard consumes only `/run-cgem` data.
- `mockData.ts` remains importable only by tests/development fixtures and carries no runtime fallback contract.

- [x] **Step 1: Write offline-state test**

Mock `useHealth` as down and assert the Dashboard renders `CGEM results unavailable` and never renders physiological metric/chart labels sourced from `simulateCGEMResult`.

- [x] **Step 2: Run test and verify failure**

Run: `npm test -- --run src/pages/DashboardPage.test.tsx`

Expected: FAIL because the current Dashboard creates mock results offline.

- [x] **Step 3: Remove the fallback**

Delete the runtime `simulateCGEMResult` import and branch. Render a durable offline panel with API URL, startup instruction, and research-use language. Keep maneuver metadata browsing on Explore, not authoritative result charts.

- [x] **Step 4: Clarify fixture documentation**

Change the `mockData.ts` module header to state that it is test/demo-fixture code and must never feed production result views.

- [x] **Step 5: Run frontend tests/checks**

Run: `npm test -- --run && npm run type-check && npm run lint`

Expected: all pass and `rg "simulateCGEMResult" frontend/src/pages` returns no matches.

- [x] **Step 6: Commit**

```bash
git add frontend/src/pages/DashboardPage.tsx frontend/src/pages/DashboardPage.test.tsx frontend/src/services/mockData.ts
git commit -m "fix(frontend): remove implicit mock physiology"
```

### Task 6: Correct Event Ranking and Scientific Terminology

**Files:**
- Create: `frontend/src/pages/BatchPage.test.ts`
- Modify: `frontend/src/pages/BatchPage.tsx`
- Modify: `frontend/src/pages/SimulatorPage.tsx`
- Modify: `frontend/src/pages/OverviewPage.tsx`
- Modify: `frontend/src/components/charts/GForceLineChart.tsx`
- Modify: `frontend/src/components/ui/PredictionTable.tsx`

**Interfaces:**
- Export `compareEventRisk(a, b, targetName)`: probability descending, then conditional `point` ascending, then maneuver ID.
- User-facing terms: `Event probability`, `Conditional time if event occurs`, and `95% prediction interval`.

- [x] **Step 1: Write ranking tests**

Create predictions where A has `P=0.01, point=5` and B has `P=0.80, point=8`; assert B ranks first. Add equal-probability and stable-name tie-break cases.

- [x] **Step 2: Run tests and verify failure**

Run: `npm test -- --run src/pages/BatchPage.test.ts`

Expected: FAIL because `compareEventRisk` does not exist.

- [x] **Step 3: Implement ranking and columns**

Default G-LOC ordering uses `compareEventRisk`. Show event probability and conditional event time as separate columns. Stop calling `expected_time_s` an event time; it may remain in API details as `P × conditional time`.

- [x] **Step 4: Correct copy and provenance**

Replace `95% CI` with `95% prediction interval`. Replace Overview `High Risk` with `High Load`, `Moderate Load`, or `Lower Load`, and state that profiles include measured, literature-encoded, and conceptual records. Rename the +4 G `Safe Limit` line to `+4 G reference`. Add a visible research-use note adjacent to prediction results. Keep `ATTITUDE · VISUAL PROXY` and add `illustrative, not aircraft kinematics` in the Simulator panel.

- [x] **Step 5: Run frontend suite**

Run: `npm test -- --run && npm run type-check && npm run lint && npm run build`

Expected: all pass; the existing chunk warning may remain for Phase 2.

- [x] **Step 6: Commit**

```bash
git add frontend/src/pages/BatchPage.tsx frontend/src/pages/BatchPage.test.ts frontend/src/pages/SimulatorPage.tsx frontend/src/pages/OverviewPage.tsx frontend/src/components/charts/GForceLineChart.tsx frontend/src/components/ui/PredictionTable.tsx
git commit -m "fix(frontend): separate event probability from conditional time"
```

### Task 7: Generated Contracts, Full Verification, and Documentation

**Files:**
- Modify: `frontend/src/services/types.ts`
- Modify: `docs/api/openapi.json`
- Modify: `CHANGELOG.md`
- Modify: `ROADMAP.md`
- Modify: `docs/superpowers/specs/2026-07-12-cgem-backend-frontend-improvement-design.md`

**Interfaces:**
- Frontend `PredictionResponse` includes `resolved_maneuver`, `maneuver_category`, and `calibration_scope`.

- [x] **Step 1: Update frontend types and regenerate OpenAPI**

Run `python -m scripts.export_openapi`, update the additive TypeScript fields, and verify no `/run-cgem` response fields changed.

- [x] **Step 2: Run backend gates**

Run:

```bash
python -m pytest tests -m "not needs_cgem_binary" -v
python -m ruff check cgem_ext tests
python -m mypy cgem_ext tests
python -m pytest tests/test_contract.py -v
```

Expected: all commands pass.

- [x] **Step 3: Run frontend gates**

Run:

```bash
cd frontend
npm test -- --run
npm run type-check
npm run lint
npm run build
```

Expected: tests, types, lint, and build pass.

- [x] **Step 4: Verify protected contracts and runtime cleanup**

Run the live `/run-cgem` schema test when the binary is available. Compare OpenAPI's `CGEMRunResponse` required fields to the previous committed spec. Execute one API call and assert no new `cgem_run_*` directory remains afterward.

- [x] **Step 5: Update project documentation**

Document canonical named inputs, explicit global inline calibration, the absence of runtime mock physiology, corrected CI coverage, and authoritative-run cleanup. Mark only completed Phase 0 items as complete.

- [x] **Step 6: Final self-review**

Search for `95% CI`, `Safe Limit`, runtime `simulateCGEMResult` imports, mixed named descriptors, and `needs_cgem_binary` on non-binary API tests. Fix any remaining matches that violate the plan.

- [x] **Step 7: Commit**

```bash
git add docs/api/openapi.json frontend/src/services/types.ts CHANGELOG.md ROADMAP.md docs/superpowers/specs/2026-07-12-cgem-backend-frontend-improvement-design.md
git commit -m "docs(cgem): record phase 0 trust-contract hardening"
```

---

## Phase 0 Completion Gate

- Named catalog maneuvers resolve one server-owned descriptor/category context.
- Registered predictions use category conformal scope; inline fallback is explicit.
- Non-binary API tests run without model training or a Fortran binary.
- `/run-cgem` uses bounded off-event-loop execution, timeout, and guaranteed HTTP-layer cleanup.
- Simulator, Prediction, Dashboard, and Settings share truthful pilot configuration behavior.
- Runtime pages never display heuristic mock physiology as CGEM.
- Batch ranking separates probability from conditional event time.
- Conformal bounds are called prediction intervals; load/reference language is contextual.
- Backend, frontend, generated-contract, and protected-contract gates pass.
