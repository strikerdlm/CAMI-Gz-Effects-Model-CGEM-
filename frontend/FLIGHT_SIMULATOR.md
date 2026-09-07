# Extra 300L learning lab

Open `/simulator` for six guided Extra 300L maneuvers with a shared aircraft, instrument and physiological timeline. Existing `/simulator?id=…` links open the catalog G-trace lessons; unsupported maneuvers do not generate aircraft motion from G alone.

## Run

Use Node 22 or newer and the project's Python API environment. From the repository root, start the API:

```sh
python -m uvicorn cgem_ext.api.main:app --host 127.0.0.1 --port 8000
```

The existing API startup also initializes its surrogate models. The guided simulation calls the additive `/simulate-flight` endpoint and runs the original CGEM directly. It does not use surrogate confidence intervals.

From `frontend/`:

```sh
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173/simulator`. The API address follows the existing Settings preference or `VITE_API_URL`, with `http://localhost:8000` as the default. A missing CGEM binary produces an explicit unavailable-physiology state while leaving the flight inspectable.

## Lesson controls

- Choose a maneuver to generate its trajectory and G history. Playback starts paused. Play, restart, seek, phase buttons and 0.25/0.5/1/2× speeds use the same simulation time.
- Setup changes mass/loading, entry IAS, pressure altitude, pull target, subject or AGSM. Editing invalidates the old result. Generate lesson recomputes flight and physiology; superseded requests cannot overwrite the current selection.
- Solo defaults to 820 kg and ±10 G; dual uses 870 kg and ±8 G. These structural limits are distinct from the model's physiological event criteria. The selected subject defaults from Settings, with no suit, pressure breathing or AGSM. AGSM is an explicit modeled comparison.
- Chase, orbit, cockpit and split views show one trajectory. The physical model has no occupant. Force vectors and the flown path can be toggled. Aircraft motion, control-surface positions and propeller phase derive from the sampled frame; control and RPM responses are estimated visual proxies.
- The barometric setting changes indicated altitude on the instruments; it does not alter aircraft height or the CGEM prediction. ISA density affects dynamics. Altitude hypoxia is not part of this axial CGEM calculation.

## Reference instruments and geometry

The procedural aircraft uses the supplied `/aircraft` front, side, top and rear images as outline/livery references. Its dimensional anchors are 8.00 m span, 6.96 m length and the manufacturer's Extra 300L configuration. The supplied source images remain unchanged.

The instrument photographs show a Garmin TXi layout. The same Canvas renderer drives the panel's Three.js texture, the side instrument display and MP4 composition. It animates attitude, IAS/TAS, altitude, vertical speed, heading and signed G; photographed navigation routes, autopilot annunciations and fixed values are not copied into telemetry.

Heading refers to the simulation's true/local north; magnetic variation is not modeled. IAS is approximated by equivalent airspeed as described in the backend model notes.

The [Garmin TXi Pilot's Guide, 190-01717-10 Rev U](https://static.garmin.com/pumac/190-01717-10_u.pdf) supplies the unusual-attitude declutter thresholds: pitch greater than +30° or less than −20°, or absolute bank greater than 65°. This is a reference-informed educational display, not certified avionics emulation. It has no AHRS-failure or synthetic-terrain database model. Actual TXi aerobatic installation/software requirements must be obtained from the relevant approved avionics documents.

## Video

Export video generates silent H.264 MP4 at 1920 × 1080 and 30 fps. Select all or part of the lesson. A frame's presentation timestamp is `i / 30`; its simulation time is `start + i × playbackRate / 30`. The end is exclusive, with the final video duration rounded up to a whole frame. The current camera mode, barometric setting and overlays are preserved; orbit uses the reference camera angle.

The compositor includes the aircraft, live PFD, G trace, native CGEM sample values, phase description, subject/AGSM settings, model limitations and trace identifier. Export uses a separate scene so it cannot advance or corrupt the viewer's clock. It waits for local fonts and sends one image at a time to a dedicated encoding worker, awaiting acknowledgment for backpressure. Cancellation terminates the worker, including pending initialization or finalization, and releases the rendering resources. A browser with WebCodecs H.264 encoding at 1080p and OffscreenCanvas is required; unsupported browsers show a clear message. The completed MP4 is buffered locally before download, so long slow-motion exports use more memory.

## Scientific scope and provenance

[Model documentation](../docs/extra300l/MODEL.md) describes the force equations, exact source revisions, estimated coefficients, actual trajectory drift, CGEM cadence and validation evidence. This is POH-checked education; the public information manual is not the current aircraft-specific approved POH, and the dynamics have not been calibrated with flight recordings. No spin, tumble, aerodynamic post-stall or unrestricted free-flight model is implied.

The renderer converts world NED to Three.js east/up/south. Body axes are forward/right/down; the xyzw quaternion rotates body into NED. The authoritative signed load is the body-normal projection of specific force, not roll angle or pitch rate. Physiological values retain actual CGEM cadence and are held between samples. Flags 0/1/2 mean baseline/loss/recovery, including the legacy `Conscious` field, whose value 1 means loss of consciousness. No synthetic t=0 physiological record is inserted.

## Verification

```sh
npm test
npm run lint:flight
npm run type-check
npm run build
npx playwright install chromium
npm run test:e2e
```

Browser tests use documented real-response fixtures isolated under `e2e/fixtures`; production does not import them. They cover playback, seeking, view selection, setup invalidation, stale responses, unavailable/error states, mobile layout, legacy trace routing and video validation/cancellation. The complete native flight/API/CGEM validation commands and numerical results are in the model documentation. To validate H.264 with an installed Chrome executable, set `CGEM_CHROME_PATH` for Playwright.
