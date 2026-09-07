# Extra 300L guided educational model

This is a force-integrated, three-dimensional point-mass teaching model coupled to the unchanged FAA CGEM binary. It is **POH-checked education, not flight-test calibration**. No published source found in this work establishes the drag polar, lift slope, roll response, pilot guidance gains or propeller efficiency used here as measured Extra 300L values. They are estimated and are exposed in API provenance.

## Sources and parameter classification

Verified 2026-09-07:

- [EASA type certificate A.362, Issue 09, 5 August 2026](https://www.easa.europa.eu/en/downloads/7174/en), **Section C: EA 300/L**, pp. 19–22: geometry, engine selection, loads, masses, speed/altitude limits and nominal control travel. This model selects the 224 kW AEIO-540 variant; the certificate also lists other engines. Downloaded PDF SHA256: `8c192c746413f4595f46339859a2243368b40c2b9810cf1b689b351126a66e18`.
- [Manufacturer Information Manual excerpt hosted by NTSB](https://data.ntsb.gov/Docket/Document/docBLOB?ID=16480049&FileExtension=pdf&FileName=Airplane+Information+Manual+Excerpts+Final+1-Rel.pdf), excerpted manual pp. 2-8 and 2-11: aerobatic loading and entry-speed information. The scanned pages were visually checked. Downloaded PDF SHA256: `7305f42a99460f29f452abb6e3bf5d549b12b7e6e79d7cdf4a59a752c5e8fad5`. The cover explicitly identifies this as a general information manual that is not kept current; it cannot replace an aircraft-specific approved POH.
- [Public Extra 300L manual mirror](https://www.manualslib.com/manual/1848391/Extra-300l.html), viewer p. 57: idle, forward-CG stall table supplied and verified during design research. The implementation's anchors are 55 KIAS at 820 kg and 57 KIAS at 870 kg. The attempt to re-fetch that page during implementation was blocked; these anchors retain the design-research provenance, rather than implying a second independent retrieval.

| Parameter | Value | Basis |
|---|---:|---|
| Span / length / height | 8.00 / 6.96 / 2.62 m | EASA Section C |
| Wing area | 10.84 m² | EASA |
| Selected rated engine power | 224 kW at 2700 rpm | EASA AEIO-540 variant |
| Solo / dual mass | 820 / 870 kg | Aerobatic I / II maxima; fixed simulated mass |
| Solo / dual load limit | ±10 / ±8 G | EASA aerobatic loading |
| VA and VNO / VNE | 158 / 220 KIAS | EASA |
| Maximum altitude | 16000 ft | EASA |
| Nominal aileron / elevator / rudder travel | ±30 / ±25 / ±30° | EASA; tolerances omitted |
| Lift-curve slope | 5.2/rad | Estimated symmetric attached-flow model |
| Zero-lift drag CD0 / induced coefficient k | 0.028 / 0.065 | Estimated; no measured polar |
| Propeller efficiency | 0.80 | Estimated |
| Engine density-lapse exponent | 0.85 | Estimated |
| G response lag / rate limit | 0.30 s / 2.5 G/s | Estimated guidance response |
| Roll response lag / acceleration / rate limit | 0.20 s / 160°/s² / 100°/s | Estimated guidance response |
| Throttle response lag / rate limit | 0.4 s / 1.0/s | Estimated |

Loop entry 100–190 KIAS and aileron-roll entry 80–158 KIAS are supported by the NTSB-hosted table. Entry bounds for combinations are educational choices inherited from constituent elements: Immelmann/Cuban 100–190, Split-S 80–158, turn 80–158 KIAS. **These bounds are not a claim that every combination of altitude, speed and intensity can complete.** The system stops when the physical/model envelope is exceeded. Default entries remain 140, 180, 120, 180, 120 and 180 KIAS for turn, loop, roll, Immelmann, Split-S and Cuban eight respectively. The manual cautions against large or abrupt control inputs above VA; default 180 KIAS loops use bounded partial guidance controls. VNE and VA have distinct meanings.

## Mechanics and conventions

The integrated state contains NED position and velocity, a transported wind-right unit vector, normal-load response state, roll rate and throttle. SI units are used internally. The fixed production step is 0.01 s, with classical RK4 and orthonormalization of the transported basis; 0.005 s is available internally only for convergence verification. The HTTP API cannot select the timestep. Runs stop at 120 s.

The velocity unit vector defines wind-forward. Wind-down is its cross product with transported wind-right. The right-vector derivative includes both parallel transport as velocity curves and the commanded axial roll. The resulting basis remains regular through vertical and inverted attitudes. Body-forward is wind-forward rotated upward by angle of attack; the body quaternion (xyzw) maps body axes forward/right/down into NED. Euler instruments are derived display values and do not drive dynamics. Quaternion signs are made continuous between samples.

With dynamic pressure `q = rho V²/2`, `CL = 5.2 alpha`, `CD = 0.028 + 0.065 CL²`, lift is `q S CL` perpendicular to velocity and drag is `q S CD` opposite velocity. Thrust follows body-forward and is `eta P throttle (rho/rho0)^0.85 / max(V,25 m/s)`. Gravity acts in NED down. Density uses the ISA troposphere. IAS is approximated by equivalent airspeed `V sqrt(rho/rho0)`; calibration/position error and compressibility are omitted. TAS drives mechanics.

The body-normal specific force is `Gz = -(a - gravity) dot body_down / g`. This gives +1 for supported upright flight, -1 for supported inverted flight and zero for ballistic flight. The incidence solver includes the drag projection into body-normal force; thrust projects to zero in body-normal coordinates. Translational mechanics satisfy `d(mV²/2 + mgh)/dt = (T cos(alpha) - D)V`. No energy or position is injected to close the maneuver.

Each loading's maximum attached-flow lift coefficient is derived from its reported one-G stall IAS. This reproduces the solo 30°/45° bank stall estimates 59.1/65.4 KIAS versus table 59/65, and dual 61.3/67.8 versus 61/68. That is an anchor check, not an independently validated stall model. Negative CL is assumed symmetric. A stalled, spinning or tumbling airplane is outside this model.

Elevator indication is a bounded proxy for the demanded fraction of available lift, aileron for roll rate, rudder is zero under the no-sideslip guidance assumption, and RPM is a 1000–2700 proxy linked to throttle. No rotational inertia, stability derivatives, control linkage, slipstream or real propeller governor are modelled. No wind, fuel burn, CG motion or terrain elevation variation is included.

## Maneuvers and stopping

All scenarios begin with two seconds of entry flight and finish with a bounded recovery phase. Pulls are terminated from integrated signed flight-path curvature about transported wind-right. Rolls use integrated roll rate. The turn reaches a 180° heading change before rolling out; additional heading change during bounded rollout is allowed.

The loop relaxes normal-load guidance near the top and requests up to the chosen intensity near the bottom. The Split-S uses its selected positive load throughout the descending half-loop: using the loop's relaxed top guidance caused the initial prototype to reach VNE, and the current guidance corrected this without modifying energy or default entry speed. The roll includes a 15° pitch-up and unloads to approximately 0.15 G during rotation. Cuban eight uses 225° pull, half-roll, 270° pull, half-roll, 45° pull followed by recovery. Roll-induced path drift and non-closing shapes are genuine outputs of this reduced model, not hidden by prescribed positions.

Every sampled state checks attached-flow CL/angle-of-attack, structural G, 220 KIAS, terrain at zero MSL, 16000 ft and finite-state bounds. A violation returns the last inspected frame, `status: stopped` and a timed explanatory event. Failure to settle recovery or complete the figure by 120 s produces `incomplete`. Initial invalid combinations return HTTP 422. The unsupported post-stall branch is never extrapolated into fabricated aircraft motion.

## Native CGEM coupling

`adapter.trace_to_ramps` converts the flight Gz timeline into continuous piecewise-linear EGP ramps. Durations are exact positive integer milliseconds, sum to the flight duration, and have no inserted one-millisecond steps. The first sample must be exactly t=0/Gnorm=1; the wrapper template's starting G is checked. The existing wrapper's subject/file preparation and executable resolution helpers are reused. This generated-trace path applies its own 15 s timeout, two concurrent subprocess slots, a bounded trace length and output-size checks. Temporary run directories are cleaned on success and failure. No legacy wrapper or Fortran code changes are required.

The parser follows unchanged `src/cgem.f`, `custom()`, lines 1498–1540:

- A normal periodic row has the next ordered integer-second timestamp and unchanged flags. It is written before that millisecond's integration, so its physiological time is `raw_seconds - 0.001`.
- A transition row changes one or more flags and has integer-millisecond time after integration. Its physiological time is `raw_ms / 1000`. Detection starts from `(0,0,0)`, so first-row and sub-second losses are captured.
- Duplicate times preserve the transition, with a later transition superseding an earlier one. Missing cadence, out-of-order data, non-finite fields, malformed flags or empty output make physiology unavailable; no zero-filled columns or synthetic t=0 row are fabricated.
- Output columns 5/6/7 (one-based) map to F_con / F_vis=FOG / F_bo=FON. Flags 0/1/2 mean normal/loss/recovery, including the unfortunately named legacy `Conscious` field (1 means loss of consciousness).

The CGEM payload retains the existing CGEMRunResponse contract and native sample cadence. Aircraft states remain inspectable if the binary or parser fails, using `physiology.status: unavailable` and a reason. CGEM is axial-only; no surrogate confidence interval applies to a newly generated flight. The approximately 10 G/s CGEM onset validation ceiling is separate from the aircraft's estimated envelope.

Provenance includes URLs, source-document hashes in assumptions, a parameter hash incorporating the physics/guidance implementation files and full request, the exact [integer ms, Gz] trace hash, and the binary hash. The parameter hash includes pilot settings as requested even where standard WHO physiology ignores custom-subject modifiers; assumptions explain that limitation.

## Reproduction and evidence

Run from the repository root:

```sh
/usr/bin/python3 -m pytest tests/test_flight_physics.py tests/test_flight_scenarios.py tests/test_flight_adapter.py tests/test_flight_api.py
/usr/bin/python3 -m docs.extra300l.validate_model
/usr/bin/python3 -m scripts.export_openapi
```

`validation.json` contains default trajectory extents, final attitudes/positions, G and IAS ranges, native CGEM success/cadence, binary/parameter/trace hashes, and trapezoidal full-flight mechanical-energy residuals. All six defaults complete with the real binary; none is a claim of measured flight performance. Loop closure error, Cuban-eight drift and heading overshoot are deliberately reported. The test suite also checks convergence, invalid configurations, the ground stop, millisecond ramp reconstruction, early and >100 s CGEM clocks, recovery flags, no-data failures, and temporary-directory cleanup on subprocess timeout.
