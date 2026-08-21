# Prospective validation of CGEM in human centrifuge and fighter-aircraft operations

**Version:** 0.1 protocol draft

**Date:** 2026-08-21

**Population:** military pilots/aircrew undergoing approved human-centrifuge training and routine fighter-aircraft sorties

**Index model:** FAA CAMI G-Effects Model (CGEM), its additive surrogate/conformal layer in this repository, and a proposed wearable-derived physiological extension

**Wearables in scope:** ActiGraph wGT3X-BT and Polar H10

**Status:** planning document; not authorization to begin human-subject research or flight-test activity

## 1. Short answer and study claim

Yes, these devices can contribute to a rigorous validation study, but **the ActiGraph wGT3X-BT and Polar H10 are not sufficient by themselves to validate all CGEM outputs**.

- The wGT3X-BT is well suited to pre-exposure sleep, circadian, physical-activity, wear-time, and ambient-light assessment. Its accelerometer has a documented ±8 g range and 30–100 Hz sampling [1]. It may saturate during +9 Gz exposures and must not be the authoritative source of the G profile.
- The Polar H10 can supply heart rate, RR intervals, and, when continuously streamed through the Polar SDK, a 130 Hz single-channel ECG [2]. Good agreement with reference ECG has been reported at rest and during conventional exercise [3,4], but that evidence does not establish validity under rapid-onset +Gz, strong AGSM electromyographic contamination, or cockpit motion. It therefore requires local qualification against reference ECG.
- The authoritative exposure input must come from the centrifuge controller/engineering accelerometer or an approved aircraft flight-data/flight-test acquisition system. Use a calibrated sensor range above the maximum planned exposure, preferably at least ±16 g, with a known cockpit-seat coordinate transform.
- Direct validation of `hlap_min` requires qualified continuous beat-to-beat blood pressure referenced or corrected to heart level. NIRS/fNIRS or transcranial Doppler can provide cerebral-perfusion/oxygenation evidence, but neither is interchangeable with CGEM's latent `c_bank` or modeled cerebral-flow variables [7–10].
- Greyout, blackout, and G-LOC need prospectively defined, time-stamped clinical/behavioral endpoints. **No sortie may deliberately induce greyout, blackout, or G-LOC for research.** In-flight data are observational and remain subordinate to flight safety.

The study should make three separate claims:

1. **Reality validation:** how closely the locked CGEM Fortran core predicts new pilot outcomes.
2. **Wrapper validation:** how closely the current surrogate, event classifiers, and conformal intervals perform on those same real exposures.
3. **Incremental physiological value:** whether pre-exposure sleep/activity and ECG-derived features improve prediction beyond locked CGEM, in pilots not used to train the physiological layer.

These claims must not be collapsed into a single accuracy number.

## 2. Repository-specific model contract

The authoritative core is `src/cgem.f`, executed through `cgem_wrapper.py`. At protocol freeze, record:

- Git commit and release tag;
- compiled-binary SHA-256;
- `gloc_inp.dat` SHA-256;
- Python package version;
- surrogate, OOD, and conformal artifact hashes;
- exact preprocessing and telemetry-to-EGP conversion code;
- operating system and Fortran runtime.

For this draft, the local CGEM binary SHA-256 is:

```text
a6f57c67616b78f5fee757cb066f356bd8ea9856cd1a941cc304c343334b7da7
```

The current model outputs relevant to validation are:

| CGEM output | Meaning in this repository | Observable reference | Validation status possible |
|---|---|---|---|
| `time_to_greyout_s` | First model vision/greyout flag | Timed peripheral-vision task, control release, symptom report, and video adjudication | Construct/convergent until a frozen flag-to-task crosswalk is qualified; direct thereafter |
| `time_to_blackout_s` | First model blackout flag | Timed central-vision failure with retained consciousness, if it occurs during routine approved testing | Construct/convergent until a frozen flag-to-task crosswalk is qualified; direct thereafter |
| `time_to_gloc_s` | First modeled G-LOC | Physician-adjudicated behavioral unresponsiveness/G-LOC during routine centrifuge training; incident reports in flight | Direct but rare; never deliberately induced in flight |
| `hlap_min` and `hlap_values` | Heart-level mean arterial pressure | Qualified beat-to-beat BP at heart level or validated hydrostatic correction | Direct if reference BP is available |
| `c_bank_min` and `c_bank_values` | Latent modeled consciousness reserve | No direct sensor equivalent | Criterion/construct validity only |
| `f_con`, `f_vis`, `f_bo` | Modeled cerebral/retinal flow terms | NIRS/fNIRS, transcranial Doppler, vision task | Convergent validity only; do not call them interchangeable |

Important implementation constraints:

- Use `PilotConfig(who_profile=None, ...)` for individualized physiology. When a standard `who_profile` is supplied, the Fortran model overrides individual physiology; dehydration and G-tolerance changes in that arm may be ineffective.
- Map `max_systolic_bp` and `max_diastolic_bp` from an independent, standardized aeromedical exercise assessment when such measurements are available; otherwise use a single preregistered default or sensitivity range. Never infer a pilot's maximum-BP inputs from the centrifuge outcome being predicted.
- A locked, uncalibrated analysis should hold `g_tolerance_multiplier=1.0` unless an independently measured rule was defined before outcomes were seen. Estimating the multiplier from the same pilot's tolerance outcome would be circular.
- The Fortran run should ingest the full measured G(t) trajectory. The surrogate's summary features (`g_peak_abs`, maximum onset rate, duration, countermeasures, and pilot tier) do not replace the exact exposure history.
- The current public wrapper loads named catalogue profiles. Before data collection, implement and test a private research importer that converts an arbitrary, synchronized reference G(t) series into the EGP format without changing the existing public Python or JSON contracts.
- The stock `custom()` output writes periodic rows at one-second intervals and adds rows when state flags change; it is not a beat-level waveform. Treat `hlap_values`, flow values, and reserve banks as model snapshots at those timestamps. Beat-to-beat reference physiology can be compared only after resampling or aggregation to the model output grid, unless a separately approved high-resolution diagnostic export is implemented.
- CGEM represents ±Gz, not Gx/Gy physiology. Record all three axes, but declare profiles dominated by Gx/Gy, tumbles, or substantial off-axis loading out of scope or OOD for the primary analysis.

## 3. Objectives and preregistered hypotheses

### 3.1 Primary objective

Estimate the agreement between locked CGEM predictions and observed **time to first peripheral visual impairment/mandatory visual-task termination** during a standardized, physician-supervised centrifuge profile. This endpoint is a construct/convergent endpoint until the frozen CGEM-flag-to-task crosswalk in Step 8 is qualified; it becomes a direct endpoint only after that qualification.

The event time is interval-censored between the last correct visual response and the first missed response or button release. Runs ending for another reason before the endpoint are right-censored or treated as a competing termination, as defined below.

### 3.2 Secondary objectives

1. Validate event occurrence and event timing for blackout and G-LOC when they occur during routine approved centrifuge training.
2. Compare modeled `hlap_values`/`hlap_min` with qualified heart-level beat-to-beat MAP.
3. Assess convergent relationships between CGEM cerebral/vision terms and fNIRS/NIRS, transcranial Doppler, visual performance, and symptoms.
4. Validate the surrogate event probabilities, event-time predictions, OOD flag, and conformal interval coverage against real outcomes.
5. Determine whether pre-exposure actigraphy and Polar-derived physiological features add out-of-sample predictive value.
6. Test transportability from centrifuge to routine fighter-aircraft exposures without recalibrating on flight outcomes.

### 3.3 Hypotheses

- **H1 (locked CGEM):** predicted greyout time has acceptably small bias and error under a prespecified operational tolerance agreed with the centrifuge medical director and flight-safety stakeholders.
- **H2 (event occurrence):** locked CGEM discriminates runs with versus without visual impairment before profile termination better than a peak-G-only baseline.
- **H3 (hemodynamics):** modeled heart-level MAP captures the direction, timing, and clinically relevant magnitude of reference MAP change.
- **H4 (incremental physiology):** a frozen physiological residual layer improves held-out pilot performance over locked CGEM alone, measured primarily by a reduction in censoring-aware prediction error/Brier score and secondarily by improved calibration.
- **H5 (transportability):** the frozen centrifuge-developed model does not show a clinically unacceptable calibration shift in routine flight exposures within the shared Gz envelope.

Conventional `p < .05` is not a validation criterion. Before registration, replace “acceptable” with operational margins. Provisional margins for discussion—not yet protocol decisions—are:

| Quantity | Provisional margin to review before registration |
|---|---|
| Greyout timing bias | 95% CI contained within ±1.0 s |
| Greyout median absolute error | ≤1.0 s |
| Conformal 95% interval coverage | 90–98%, reported with pilot-clustered CI |
| Continuous HR device qualification | MAE ≤3 beats/min and ≥95% usable beats |
| RR device qualification | R-peak sensitivity and positive predictive value ≥99% vs reference ECG |
| MAP minimum | bias within ±5 mmHg, with limits of agreement reported |

Margins must be justified clinically and by measurement resolution; they must not be chosen after seeing results.

## 4. Materials and methods: study design

Prospective, repeated-measures, multi-environment validation with four ordered phases:

1. **Phase 0 — bench and integration qualification.** Synchronization, accelerometer saturation, Bluetooth dropout, ECG artifact, device retention, electromagnetic compatibility, and data-security testing.
2. **Phase 1 — low-risk physiological qualification.** Reference ECG versus H10 and reference accelerometry versus wearables during rest, standing, AGSM practice, and low/moderate centrifuge G.
3. **Phase 2 — controlled centrifuge validation.** Standardized and operational profiles under routine medical supervision.
4. **Phase 3 — prospective fighter-aircraft transportability study.** Observational recording during already-approved sorties and maneuvers; no maneuver is added or altered to create a research endpoint.

The locked base model may be evaluated on all eligible participants because it is not fitted to them. The physiological layer requires pilot-level development and test separation. No run from a test pilot may appear in training, feature selection, imputation-model fitting, or hyperparameter tuning.

## 5. Setting, participants, and safety

### 5.1 Inclusion criteria

- Current military pilot/aircrew member cleared for the scheduled centrifuge training or sortie.
- Within the age and medical limits of the local aviation authority and centrifuge SOP.
- Able to provide voluntary informed consent without command coercion.
- Able to wear the approved sensors without interfering with life-support, restraint, anti-G, ejection-seat, or communication systems.

### 5.2 Exclusion/deferral criteria

- Any temporary or permanent aeromedical disqualification.
- Acute illness, fever, significant dehydration, new cardiovascular symptoms, or medication change requiring aeromedical review.
- Skin condition preventing electrodes or forehead optics.
- Device fit that interferes with harness, anti-G equipment, helmet, oxygen mask, survival gear, or ejection path.
- Aircraft or centrifuge engineer rejects the research configuration.
- Inability to synchronize authoritative telemetry.

Do not exclude a pilot post hoc because their result is inconvenient. Analyze prespecified signal-quality failures and safety terminations transparently.

### 5.3 Governance

Required before recruitment:

- institutional ethics/IRB approval;
- military research and operational authorization;
- centrifuge medical director and safety board approval;
- aircraft engineering/airworthiness and electromagnetic-interference approval;
- data-protection assessment for health data and potentially classified telemetry;
- independent consent process and explicit non-retaliation language;
- adverse-event, stopping, and unblinding procedures;
- prospective registration and signed statistical analysis plan.

The study never supersedes the centrifuge controller, medical officer, instructor pilot, aircraft commander, or flight manual. In-flight G-LOC is an adverse event, not a target to elicit.

## 6. Instrumentation

### 6.1 Required minimum stack

| Domain | Primary/reference instrument | Wearable/secondary instrument | Purpose |
|---|---|---|---|
| G exposure | Centrifuge engineering output or approved flight-data/flight-test IMU, range above planned maximum | wGT3X-BT raw acceleration; H10 accelerometer if streamed | Reference G(t); wearable artifact/context only |
| Cardiac electrical | Qualified 3-lead or facility ECG | Polar H10 RR and 130 Hz ECG stream | HR/RR qualification and physiology layer |
| Arterial pressure | Qualified continuous beat-to-beat BP, transducer/reference at heart level | None | Direct `hlap` validation |
| Cerebral state | Flight/centrifuge-qualified NIRS/fNIRS; TCD if technically feasible | None | Convergent cerebral oxygenation/perfusion |
| Vision/consciousness | Peripheral and central visual task, control/button log, synchronized video, intercom/audio, physician adjudication | None | Greyout/blackout/G-LOC endpoints |
| Respiration/strain | Respiratory belt or capnography where compatible; suit and PBG pressure; optional EMG | H10-derived respiratory estimates only exploratory | AGSM and ventilation context |
| Sleep/activity | Sleep diary and wGT3X-BT on non-dominant wrist | wGT3X-BT | Seven-day readiness exposure |
| Environment | Cabin altitude/pressure, oxygen setting, temperature, mission timing | wGT3X-BT ambient light | Confounding/context |

High-G fNIRS studies have captured cerebral deoxygenation up to +9 Gz [7], while other work shows that NIRS and transcranial Doppler can diverge under hypergravity [9]. Therefore, cerebral oxygenation is a complementary physiological signal, not a substitute for blood pressure, cerebral blood flow, vision, or consciousness.

### 6.2 ActiGraph wGT3X-BT deployment

**Pre-exposure:**

- non-dominant wrist;
- seven consecutive 24-hour periods before the centrifuge day/sortie, including the immediately preceding night;
- raw 30 Hz collection is sufficient for the longitudinal actigraphy purpose and preserves battery/storage;
- concurrent brief electronic or paper sleep diary with bed time, attempted sleep time, estimated sleep onset, awakenings, final awakening, out-of-bed time, naps, device removal, alcohol/caffeine, and unusual duty periods;
- fixed device serial number, firmware, clock source, wear side, and algorithm version.

**During centrifuge/flight:**

- use only after retention and interference approval;
- raw data may document motion and artifact but are not the primary G input;
- values at or near ±8 g are censored/saturated, not interpreted as true peaks;
- if wrist wear conflicts with gloves or controls, use the approved position and treat sleep and exposure deployments as different measurement contexts.

Primary actigraphy variables:

- total sleep time;
- time in bed/sleep period window;
- sleep efficiency;
- wake after sleep onset;
- sleep midpoint and variability;
- previous-night sleep and seven-day sleep debt relative to each pilot's usual schedule;
- non-wear time;
- sedentary, light, and moderate/vigorous activity time;
- 24-hour activity/rest regularity.

Actigraphy is generally better at detecting sleep than wake and may overestimate sleep or underestimate wake [5,6]. Do not infer sleep stages. Freeze one primary algorithm before analysis; a reasonable choice is a raw-data GGIR/HDCZA workflow, with the ActiLife/Cole–Kripke result as a labeled sensitivity analysis. Use the diary and event markers to support window detection rather than changing the algorithm pilot by pilot.

### 6.3 Polar H10 deployment

- Use a dedicated, institution-controlled logger based on the official Polar BLE SDK; consumer cloud synchronization should be disabled if policy requires local-only processing.
- Stream raw ECG at 130 Hz and RR/HR to the approved logger. The H10's internal recording capability must not be assumed to store continuous raw ECG; verify firmware-specific behavior before deployment [2].
- Record sensor ID, strap size, firmware, battery status, contact preparation, connection mode, receiving-device ID, packet sequence/timestamps, and dropout count.
- Wet the electrodes or use the manufacturer-compatible conductive medium; place the strap consistently and check that the harness/anti-G garment does not displace it.
- Capture at least five minutes of artifact-screened supine rest after a standardized stabilization period, plus recovery. Record respiration because breathing materially changes HRV.
- Primary pre-exposure cardiac features: mean HR, mean RR, RMSSD, and SDNN. Treat LF, HF, LF/HF, nonlinear features, and very short moving-window HRV as secondary/exploratory.
- During dynamic G, use instantaneous HR/RR and signal-quality indices. Do not interpret standard frequency-domain HRV from highly nonstationary AGSM/high-G windows as if it were a resting five-minute recording.

Published H10 results support RR/HR measurement during conventional exercise [3,4], and recent high-G literature supports HRV as a candidate predictor of +Gz tolerance [11]. Neither finding removes the need for local high-G validation.

**BP reference qualification.** Use a facility-approved volume-clamp finger/ear system (for example, Finapres NOVA or an equivalent) with documented high-G qualification, plus simultaneous brachial oscillometric readings at baseline and recovery. Level the sensor to the right-atrial/heart reference, record the vertical offset and three-dimensional G vector, apply a preregistered hydrostatic correction, and retain waveform-confidence and beat-validity flags. Before data collection, lock minimum valid-beat proportion, maximum allowable gaps, calibration residuals, and high-G artifact rules; a provisional feasibility rule is at least 90% valid beats per analysis window and no gap longer than 2 s. If no qualified continuous BP survives high-G artifact testing, do not claim direct `hlap` validation; report only feasibility or construct/convergent comparisons.

### 6.4 Synchronization specification

Every data source must have both UTC time and a monotonic device clock. Before and after every run/sortie:

1. synchronize the acquisition computers to the approved master clock;
2. generate a shared, time-stamped synchronization event visible in telemetry and physiological channels where possible (hardware TTL pulse preferred; otherwise a documented tap/motion/audio marker);
3. estimate offset and clock drift, not offset alone;
4. preserve native timestamps and raw packets;
5. report median, 95th percentile, and maximum residual synchronization error.

Choose the acceptance limit before data collection from the smallest meaningful event-time difference. A provisional target is ≤50 ms residual error. Runs outside the limit remain in a documented synchronization-failure category and are excluded only according to the preregistered rule.

## 7. Procedures step by step

### Step 1 — freeze the scientific question and model

- Select one primary centrifuge profile and one primary endpoint.
- Freeze model/binary hashes, telemetry preprocessing, individualized input mapping, physiological candidates, outcome margins, and statistical code version.
- Generate predictions only after the analysis plan is signed; keep outcome adjudicators blind to predictions.

### Step 2 — build a telemetry-to-CGEM bridge

- Ingest authoritative time, Gx, Gy, Gz, seat attitude, and relevant system channels.
- Transform acceleration into the pilot-seat anatomical coordinate frame.
- Preserve the measured baseline, onset, plateaus, transitions, push-pull components, and recovery; do not replace the waveform with only peak G and duration.
- Apply a documented anti-aliasing/resampling method and export EGP input.
- Unit-test with synthetic ramps, plateaus, rapid-onset profiles, negative-to-positive transitions, missing packets, and clock drift.
- Compare bridge-generated CGEM results with known catalogue profiles before human data are used.

### Step 3 — bench qualification

- Test both wearables on a calibrated shaker/centrifuge fixture through the expected frequency and acceleration range.
- Document wGT3X-BT and H10 accelerometer clipping near ±8 g.
- Test strap/device retention, battery, logger thermal behavior, BLE range, packet loss, and reconnection.
- Complete EMI/airworthiness assessment. A personal phone in the aircraft is not an acceptable default logger.
- Establish the sensor data-quality thresholds and failure codes.

### Step 4 — human device qualification

In 12–20 pilots or representative qualified volunteers, collect simultaneous H10 and reference ECG during:

1. supine and seated rest;
2. standing/orthostatic transition;
3. standardized AGSM practice;
4. low/moderate +Gz;
5. at least one approved high-G profile if safety permits.

Two independent reviewers, blinded to device, should adjudicate R peaks on sampled high-artifact segments. Estimate R-peak sensitivity/positive predictive value, HR/RR bias, limits of agreement, data completeness, and error by G level/AGSM phase. If the qualification margin fails, retain H10 only for pre/post measurements or replace the in-exposure reference path; do not silently filter the failure away.

### Step 5 — recruit and characterize pilots

Collect the minimum necessary variables:

- age, sex, height, mass, sitting height/head-to-heart distance if feasible;
- aircraft type, total/current-type hours, high-G training recency, and recent G exposure;
- resting SBP/DBP from repeated standardized readings and, if already available from an approved independent exercise assessment, maximum SBP/DBP for the custom CGEM input;
- relevant aeromedical history and medications as coded, access-controlled variables;
- fitness and AGSM qualification;
- caffeine, alcohol, food, hydration, illness, temperature, perceived stress/fatigue, and duty/rest timing;
- suit model/fit, actual suit pressure, PBG setting, seat angle, oxygen/cabin-altitude setting.

Do not collect broad sensitive variables without a defined analytical or safety purpose.

### Step 6 — seven-day readiness monitoring

- Initialize the wGT3X-BT and diary.
- Require the immediately prior night plus a prespecified minimum number of valid nights; four valid nights can be a feasibility minimum, while seven is preferred.
- Conduct daily compliance checks that do not expose health data to commanders beyond the approved workflow.
- Keep raw acceleration and diary corrections; do not retain only vendor summary scores.

### Step 7 — test-day baseline

At a standardized time before exposure:

1. confirm eligibility and recent exposures;
2. measure mass, temperature, and repeated BP;
3. measure hydration using a prespecified method such as urine specific gravity, if approved;
4. record five to ten minutes supine rest with reference ECG/H10, BP, respiration, and optional NIRS;
5. perform a standardized visual-task practice;
6. verify clocks, data streams, device fit, suit, oxygen, restraints, and emergency stop.

Avoid experimentally imposing sleep deprivation, dehydration, hypoglycemia, or unsafe fatigue. Natural variation can be measured observationally.

### Step 8 — centrifuge exposures

Use only facility-approved profiles. A defensible sequence is:

1. familiarization/measurement check;
2. gradual-onset relaxed tolerance profile terminated at the facility's visual endpoint;
3. gradual-onset straining profile with standard equipment;
4. one or more rapid-onset/operational profiles using prescribed AGSM and protective equipment.

Randomize or counterbalance the order of scientifically interchangeable profiles when the SOP allows; otherwise model order and cumulative exposure. Use a fixed recovery criterion and record the actual inter-run interval.

The visual endpoint should combine:

- a continuous peripheral and central visual stimulus/task;
- a press-and-hold or repeated response sampled fast enough to define an event interval;
- synchronized face/eye/body video;
- intercom/audio and controller markers;
- medical officer termination reason;
- immediate post-run symptom and awareness report.

**CGEM flag crosswalk and task qualification.** In the current Fortran implementation, `ne2=1` denotes the greyout/vision flag, `non2=1` denotes optic-function shut-down, and `n2=1` denotes unconsciousness. A visual-task miss or button release is not automatically the same state. In a Phase 1 calibration subset, collect synchronized CGEM flags, task responses, video, symptoms, and controller markers. Freeze a threshold, time-tolerance window, and adjudication rule before Phase 2. If no stable mapping is achieved, retain construct/convergent-validity language rather than claiming direct validation. Use two practice blocks; record block, order, and cumulative-exposure variables and include them as prespecified covariates/sensitivity analyses, never as post-hoc event-label changes.

The run stops under the existing SOP. Research personnel never delay termination to obtain a more complete endpoint.

### Step 9 — fighter-aircraft data collection

- Include only routine, approved missions/maneuvers.
- Use aircraft/flight-test G telemetry as the exposure reference; document sensor location, range, sample rate, filters, and coordinate frame.
- Record suit/PBG/oxygen/altitude/seat variables when technically and operationally available.
- If the H10 raw stream or wGT3X-BT is not airworthiness-approved, collect pre/post physiology and authoritative aircraft telemetry rather than bypassing policy.
- Use nonintrusive event markers and post-sortie structured debrief. No in-cockpit research task may increase workload during critical phases.
- Treat reported visual symptoms, A-LOC, or G-LOC as safety incidents requiring the normal aeromedical pathway.

Flight validation is primarily a test of transportability and physiological response under safe exposure. Absence of G-LOC in flight does not prove the model is correct; it mainly supplies right-censored/non-event information.

### Step 10 — blinded outcome adjudication

Two aeromedical adjudicators, blinded to CGEM predictions and wearable-derived risk scores, independently classify:

- no impairment;
- peripheral visual loss/greyout;
- central visual loss/blackout with consciousness retained;
- A-LOC;
- G-LOC;
- medical termination for another cause;
- indeterminate.

Record the interval containing onset, not only a rounded timestamp. Resolve disagreements by a third adjudicator. Report Cohen's kappa for categorical status and an ICC/absolute timing difference for event timing.

### Step 11 — generate locked predictions

For every run:

- map measured pilot and countermeasure variables to `PilotConfig`;
- execute the authoritative Fortran core on exact G(t);
- generate surrogate probability/time/interval predictions from the frozen model;
- record OOD status and distance;
- save raw output and provenance;
- never edit the observed endpoint based on model output.

### Step 12 — develop the physiological layer

Define the layer as an additive discrepancy model, not a rewrite of the validated Fortran core:

```text
observed outcome = locked CGEM prediction + pilot/session discrepancy
pilot/session discrepancy = f(sleep, activity, resting HR/RMSSD/SDNN,
                              BP, hydration, respiration/AGSM, context)
```

For event outcomes, model a correction to log event time or event hazard. For continuous MAP, model residual waveform/minimum error. Use shrinkage and a small prespecified feature set; the number of candidate wearable variables must be compatible with the number of independent pilots and events.

Recommended separation:

- development/calibration: centrifuge pilots only, grouped by pilot;
- internal assessment: nested group cross-validation or a frozen pilot-level holdout;
- final external test: untouched pilots and all eligible fighter-aircraft sessions;
- no feature selection or normalization fitted on the external test set.

## 8. Variable and data dictionary

### 8.1 Identifiers and provenance

| Variable | Type/unit | Source | Role |
|---|---|---|---|
| `pilot_id` | pseudonymous string | study registry | clustering; never service ID |
| `session_id`, `run_id`, `sortie_id` | string | study system | hierarchy |
| `environment` | centrifuge/aircraft | protocol | transportability |
| `aircraft_type`, `profile_id` | controlled category | operations | stratification/context |
| `device_serial`, `firmware`, `logger_version` | string | devices | provenance |
| `model_commit`, `binary_sha256`, `input_sha256` | string | repository | reproducibility |
| `timestamp_utc`, `time_monotonic_ns` | time | all streams | synchronization |

### 8.2 Exposure and countermeasures

| Variable | Unit/rate | Primary source | Derived variables |
|---|---|---|---|
| `gx`, `gy`, `gz` | g; native high rate | reference telemetry | peak/minimum, vector, axis fractions |
| `dgz_dt` | g/s | derived from qualified Gz | maximum onset/offset, phase |
| `dose_above_2g` | g·s | reference telemetry | cumulative exposure |
| `duration_above_4g/6g` | s | reference telemetry | sustained load |
| `seat_tilt` | degrees | aircraft/centrifuge | CGEM input |
| `gsuit_pressure` | psi or kPa | suit system | actual protection |
| `gsuit_coverage` | fraction | equipment record | CGEM input |
| `pbg_pressure` | mmHg | breathing system | CGEM input |
| `agsm_phase/effectiveness` | ordinal plus measured proxies | audio/respiration/EMG and instructor rating | confounder/model input |
| `cabin_altitude`, `fio2/o2_mode`, `temperature` | standard units | aircraft/facility | context |

### 8.3 Pilot and readiness variables

| Variable | Unit | Timing | Role |
|---|---|---|---|
| sex, age, height, mass, sitting height | coded/years/cm/kg | baseline | CGEM/stratification |
| resting SBP/DBP | mmHg | test day | individualized CGEM input |
| experience and G-training recency | h/days | baseline/session | confounding |
| previous-night and 7-day TST | min | pre-exposure | physiological layer |
| sleep efficiency/WASO/midpoint variability | %, min | pre-exposure | physiological layer |
| sedentary/MVPA/activity regularity | min/index | pre-exposure | physiological layer |
| resting HR/mean RR/RMSSD/SDNN | bpm/ms | pre-exposure | physiological layer |
| hydration, temperature, caffeine, illness, stress/fatigue | prespecified units/scales | test day | covariates/sensitivity |

### 8.4 Dynamic physiology and outcomes

| Variable | Unit/rate | Source | Interpretation |
|---|---|---|---|
| reference ECG | mV; facility rate | qualified ECG | cardiac criterion |
| H10 ECG | µV; 130 Hz | Polar SDK | wearable candidate |
| RR and HR | ms/bpm | H10 and reference ECG | autonomic/cardiac response |
| beat-to-beat SBP/DBP/MAP | mmHg | qualified monitor | direct hemodynamic outcome |
| fNIRS/NIRS HbO2, HHb, tissue saturation | device units/% | qualified cerebral sensor | convergent cerebral outcome |
| TCD middle cerebral artery velocity | cm/s | TCD if feasible | cerebral-flow proxy |
| respiration/EtCO2 | breaths/min, mmHg | belt/capnography | ventilation/AGSM |
| visual-task response | correct/incorrect and time | task controller | greyout/blackout interval |
| adjudicated state | category and onset interval | blinded panel | clinical outcome |
| termination reason | controlled category | medical controller | censoring/competing event |
| recovery time | s | task/video | secondary outcome |

### 8.5 Prediction variables

Store, without overwriting:

- core event/no-event and predicted event times;
- full `hlap`, `c_bank`, and available flow series;
- surrogate event probability and event-time estimate;
- conformal lower/upper bounds;
- OOD score, threshold, and flag;
- physiological-layer prediction after it is frozen;
- preprocessing/model version and failure flags.

## 9. Signal processing and quality control

### 9.1 G telemetry

- Keep native, unfiltered data immutable.
- Apply calibration and coordinate transform before filtering.
- Use a prespecified low-pass/anti-alias filter based on sensor bandwidth and target resampling rate.
- Detect clipping, missing packets, impossible slew, and clock discontinuity.
- Derive onset rate from a documented robust derivative; do not select the smoothest result after looking at outcomes.
- Run primary analysis on the full reference waveform and sensitivity analyses across justified filter settings.

### 9.2 ECG/RR

- Detect R peaks with one frozen algorithm and keep a signal-quality index.
- Mark, rather than simply interpolate, dropout, ectopy, and motion/EMG artifact.
- Use normal-to-normal intervals for HRV with prespecified artifact correction.
- Report the percentage corrected and excluded in each window.
- Do not calculate primary resting HRV unless the required clean duration is present.
- Do not impute missing high-G beats for the primary dynamic analysis.

### 9.3 Actigraphy

- Detect non-wear with a fixed algorithm and reconcile sleep windows with diary/event markers under a written rule.
- Require the prespecified valid-night criteria.
- Derive features before outcome/model access.
- Report device removals, missing nights, and algorithm sensitivity results.

### 9.4 BP and cerebral signals

- Qualify sensor retention and artifact under G.
- Correct pressure to heart level if the transducer is elsewhere, using measured geometry and acceleration.
- Flag volume-clamp loss, NIRS optode lift, extracranial contamination, and TCD probe shift.
- Never fill a physiologically critical dropout across the predicted endpoint with a smooth interpolation in the primary analysis.

## 10. Statistical analysis plan

### 10.1 Analysis populations

- **Safety population:** every consented exposure started.
- **Locked-model validation population:** every eligible run with authoritative G telemetry and an adjudicable endpoint/censoring time.
- **Hemodynamic population:** runs also meeting reference BP quality criteria.
- **Physiological-layer population:** pilots meeting prespecified wearable baseline and signal-quality rules.
- **Flight transportability population:** all approved, eligible sorties after the physiological model is frozen.

Report a flow diagram from recruited pilots to pilots, sessions, runs, events, censored runs, and analyzable signals. The pilot—not the run—is the principal independent sampling unit.

### 10.2 Descriptive analysis

- Summarize pilots and exposures by environment, sex, aircraft/profile, countermeasure package, and G-onset regime.
- Report median/IQR and mean/SD as appropriate, plus full range.
- Plot spaghetti trajectories by pilot for G, HR, MAP, cerebral oxygenation, and model outputs.
- Report missingness and signal-quality failures by G level and device.
- Compare included versus excluded runs without significance-test gatekeeping.

### 10.3 Primary event-time analysis

Time origin is the synchronized start of the complete G profile supplied to CGEM. Before unblinding, define a primary horizon `τ` (profile end for the standardized centrifuge profile) and, for flight, a common operational horizon or explicitly label flight estimates as secondary. The visual event is interval-censored between the last correct response and the first missed response/button release.

For each endpoint, assign exactly one status at `τ`: event, administrative censoring, competing event, or indeterminate. Use cause-specific cumulative-incidence/Aalen–Johansen estimators when competing events are present, and inverse-probability-of-censoring weighting (IPCW) for sensitivity analyses. Do not treat safety terminations as ordinary right-censoring in the primary analysis.

For deterministic CGEM predictions:

1. Estimate event-by-`τ` sensitivity, specificity, balanced accuracy, and predictive values with IPCW or a prespecified complete-observation restriction; report pilot-clustered 95% CIs.
2. Assess timing with bias, median absolute error, and RMSE among informative event pairs, clearly labeled conditional, with interval-censoring-aware methods and pilot-clustered bootstrap CIs.
3. Fit an interval/right-censored accelerated-failure-time calibration model relating observed log event time to predicted log event time, with pilot random effect or robust pilot-clustered variance. For medical/safety competing events, use a cause-specific or multi-state timing estimand; otherwise restrict this calibration to the prespecified endpoint-without-competing-event subset and label it conditional. Perfect timing calibration corresponds to intercept 0 and slope 1 on the prespecified scale.
4. Report a censoring-aware C-index and horizon-specific calibration using IPCW, pseudo-observations, or a competing-risk calibration estimator; do not discard censored runs merely to simplify analysis.
5. Compare CGEM with simple baselines: peak G alone, peak G plus onset rate, and facility-standard G-tolerance rules.

For a surrogate classifier/regressor, report horizon-specific event-probability calibration-in-the-large, calibration slope, and flexible calibration curves using IPCW, pseudo-observations, or another prespecified competing-risk-aware estimator. If no such estimator is implemented, label calibration exploratory and restrict it to a prespecified complete-observation subset. Also report IPCW time-dependent AUROC, weighted AUPRC, and IPCW Brier score at prespecified horizons (plus integrated Brier score if a survival representation is available). Event-time error remains conditional on observed events. Standard conformal prediction coverage is not claimed “overall” under censoring: report coverage/width only for observed event-positive runs as exploratory, or implement a prespecified censored/conformal-survival method. Report every metric separately for OOD and in-envelope runs.

### 10.4 Continuous and waveform outcomes

For `hlap` versus reference heart-level MAP:

- aggregate the reference waveform to the stock CGEM one-second/state-transition snapshot grid before comparison; no beat-to-beat agreement claim is permitted without an approved high-resolution diagnostic export;
- time-aligned bias, MAE, RMSE, and concordance correlation coefficient on that common grid;
- difference in minimum MAP and time of minimum at the model's snapshot resolution;
- hierarchical Bland–Altman analysis with repeated runs nested within pilots;
- functional/phase-specific errors for baseline, onset, plateau, offset, and recovery;
- cluster bootstrap by pilot for uncertainty.

For NIRS/TCD/visual performance versus latent CGEM cerebral terms:

- repeated-measures association and lagged cross-correlation;
- mixed-effects regression with pilot random intercept and prespecified G phase;
- construct/convergent validity language only;
- no agreement or interchangeability claim unless the quantities and units truly match.

### 10.5 Physiological-layer analysis

Use a small, frozen predictor set such as:

- previous-night TST and seven-day sleep variability;
- resting mean HR, RMSSD, and SDNN;
- resting SBP/DBP and measured hydration;
- recent G exposure/training recency;
- respiration/AGSM quality where reliably captured.

Fit a penalized hierarchical AFT/survival model for event time and a penalized mixed model for continuous residuals. Bayesian shrinkage is reasonable if priors and convergence diagnostics are preregistered. Include random intercepts for pilot and, if data support it, random G-response slopes.

Compare locked CGEM and CGEM-plus-physiology using paired predictions on the same held-out pilots:

- change in calibration intercept/slope;
- change in integrated Brier score or censoring-aware loss;
- change in MAE/RMSE for timing/continuous outcomes;
- change in conformal coverage/width if a new interval layer is calibrated;
- pilot-clustered bootstrap CI for every difference.

Do not claim incremental value from a training-set likelihood-ratio test alone. Improvement must persist in held-out pilots and the untouched flight cohort.

### 10.6 Environment and repeated measures

The data hierarchy is:

```text
pilot
└── session/sortie
    └── run/maneuver
        └── time samples/beats
```

Use pilot-level grouping in every split and bootstrap. For transportability, report flight calibration separately and test a prespecified environment-by-prediction interaction. Aircraft type and profile may be modeled as fixed effects or an internal-external validation stratum if sample size permits.

### 10.7 Censoring and competing terminations

For each endpoint at horizon `τ`, assign exactly one mutually exclusive status:

- endpoint reached: event;
- planned profile completion without endpoint, or loss to follow-up before `τ` for reasons unrelated to the endpoint: administrative censoring;
- arrhythmia, equipment failure, motion sickness, or another medical/safety stop before the endpoint: competing event in the primary analysis;
- loss of telemetry or endpoint signal: indeterminate/missing, not an assumed non-event.

Use cause-specific cumulative incidence/Aalen–Johansen estimates for competing events and IPCW sensitivity analyses for administrative censoring. A safety termination may be treated as censoring only in a separately labeled sensitivity analysis with an explicit assumption. G-LOC after an earlier greyout endpoint still contributes the earlier greyout event and a separate G-LOC outcome. Assess whether safety termination is informative by reason and G phase; use a multi-state sensitivity analysis if event counts support it.

### 10.8 Missing data

- Never impute the primary event label, authoritative G waveform, or high-frequency physiological dropout across the endpoint.
- Describe missingness mechanisms and patterns.
- Multiple imputation may be used for baseline covariates in model development if the imputation model is fitted within each training fold and includes the outcome appropriately.
- Apply the frozen imputation rule to test data without refitting; complete-case analysis is a sensitivity analysis.
- Analyze device failure/data completeness as a secondary outcome because failure may increase with G and is not missing completely at random.

### 10.9 Multiplicity and subgroups

Use one primary outcome and one primary operational margin. Apply Holm adjustment to a small confirmatory secondary family or control false discovery rate for a broader exploratory physiological family. Report effect sizes and confidence intervals regardless of significance.

Prespecified subgroups may include sex, aircraft type, experience, GOR/ROR, countermeasure package, and OOD status. Use interaction estimates with shrinkage; do not claim subgroup effects from separate within-group `p` values. Sparse representation, especially of female pilots or G-LOC events, must be stated.

### 10.10 Sample size

Do not choose sample size from a generic “10 events per variable” rule or count repeated runs as independent pilots. External-validation sample size should target precision of calibration, discrimination, and prediction error; for censored outcomes, use simulation that incorporates the event-time, censoring, G-profile distribution, and between-pilot correlation [16,17].

Use this sequence:

1. Conduct Phase 1 with 12–20 pilots to estimate high-G signal loss, within/between-pilot variance, event rate, event-time interval width, and censoring.
2. Simulate complete pilot/session/run datasets under those estimates.
3. Vary the number of independent pilots, runs per pilot, event rate, censoring, and dropout.
4. Select the smallest design meeting all prespecified precision targets, such as calibration-slope CI width, greyout-bias CI width, and device-failure precision.
5. Inflate for pilot-level attrition and unusable telemetry, not just run-level loss.

A practical planning scenario of **40–60 pilots with four usable centrifuge profiles each** (160–240 runs) may support a strong mechanistic/repeated-measures study, but it may still be underpowered for confirmatory event-model calibration because the effective sample is driven by independent pilots and informative events. Traditional suggestions of roughly 100 events and 100 non-events are only a rough diagnostic, not a substitute for the Riley precision calculation [16,17]. Do not induce G-LOC to satisfy an event target; if G-LOC remains sparse, report it descriptively and make greyout/physiological response the confirmatory endpoint.

### 10.11 Sensitivity analyses

- exact G(t) core versus surrogate summary-feature prediction;
- custom pilot physiology versus nearest FAA preset;
- alternative justified G filters and event intervals;
- complete-case versus imputed baseline covariates;
- excluding clipped wearable acceleration without excluding the run;
- stratifying by slow versus rapid onset;
- with and without safety competing events;
- first exposure per pilot only versus all exposures with hierarchical modeling;
- centrifuge-only versus flight-only calibration;
- reference ECG versus H10-derived physiology after qualification.

## 11. Data management, security, and reproducibility

- Raw pilot health and flight telemetry must not be committed to Git.
- Store raw data read-only in the approved encrypted environment. Keep the re-identification key separate.
- Use pseudonymous IDs and role-based access; record every export.
- Treat route, aircraft-system, performance, and timing channels according to military classification rules.
- Avoid manufacturer cloud services unless approved in the consent and security plan.
- Preserve native raw files (`.gt3x`, ECG packets, telemetry, video indices) and generate immutable checksums.
- Maintain a machine-readable data dictionary, units, time bases, calibration certificates, firmware/software versions, and preprocessing logs.
- Commit only de-identified derived data approved for release, analysis code, frozen configuration, synthetic test fixtures, and aggregate results.
- Use scripted, containerized analysis; seed all stochastic procedures; save package lock files and model artifacts.
- Pre-register changes as dated amendments before unlocking the flight test set.

Recommended project structure:

```text
docs/validation/                 # protocol, SAP, CRFs, data dictionary
configs/validation/              # frozen model and preprocessing configs
scripts/validation/              # telemetry import, QC, prediction, analysis
tests/validation/                # synthetic synchronization and EGP tests
data/validation/README.md        # access instructions only; no protected raw data
artifacts/validation/            # approved aggregate tables/figures and hashes
```

## 12. Decision gates

| Gate | Pass requirement | If not met |
|---|---|---|
| Airworthiness/EMI | Written approval; no interference with gear/ejection path | No in-flight wearable use; pre/post only |
| G telemetry | Calibrated, unsaturated, synchronized reference G(t) | Run cannot enter core validation |
| H10 high-G qualification | Prespecified HR/RR agreement and completeness | Use H10 only outside exposure or replace with qualified system |
| wGT3X-BT | Complete actigraphy and known clipping behavior | Use for sleep/activity only; do not infer peak G |
| Endpoint | Blinded adjudication and valid onset interval/censoring time | Indeterminate endpoint; exclude by rule, report |
| Model lock | Hashes/configuration verified | No prediction until discrepancy resolved |
| Physiological layer | Pilot-separated development and test | Exploratory analysis only |
| Flight validation | Untouched flight cohort and approved telemetry | No transportability claim |

## 13. Interpretation boundaries

This protocol can establish:

- external performance of CGEM for specific, measured Gz profiles and pilot populations;
- whether prediction error varies by onset regime, countermeasure, readiness, or environment;
- whether wearable-derived physiological readiness adds generalizable predictive information;
- whether the system knows when it is OOD.

It cannot establish, without additional evidence:

- safety of using consumer wearables as certified cockpit medical devices;
- validity for unmeasured Gx/Gy-dominant maneuvers;
- direct measurement of CGEM's consciousness bank by HRV or NIRS;
- causal effects of poor sleep, HRV, hydration, or stress from this observational layer;
- full G-LOC calibration if too few independent G-LOC events occur;
- operational readiness for autonomous real-time warning solely from retrospective accuracy.

## 14. Evidence basis

### Device and measurement sources

1. [ActiGraph wGT3X-BT + ActiLife User Guide](https://actigraphcorp.jp/support/pdf/gt3xbt_usersguide.pdf). ActiGraph; revision A, 2016. Three-axis MEMS accelerometer, ±8 g, 12-bit, 30–100 Hz raw storage.
2. [Polar H10 features available through the official Polar BLE SDK](https://github.com/polarofficial/polar-ble-sdk/blob/master/documentation/products/PolarH10.md). Polar Electro. HR/RR, 130 Hz ECG stream, accelerometer, and recording capabilities.
3. [Validity of the Polar H10 Sensor for Heart Rate Variability Analysis during Resting State and Incremental Exercise in Recreational Men and Women](https://consensus.app/papers/details/0686997c4c3a5b599d08bc8d0b037213/?utm_source=claude_desktop). Schaffarczyk M, Rogers B, Reer R, Gronwald T. *Sensors*. 2022;22:6536. [doi:10.3390/s22176536](https://doi.org/10.3390/s22176536).
4. [RR interval signal quality of a heart rate monitor and an ECG Holter at rest and during exercise](https://consensus.app/papers/details/c6fb820cf61f503bbaef31c3e1df4143/?utm_source=claude_desktop). Gilgen-Ammann R, Schweizer T, Wyss T. *European Journal of Applied Physiology*. 2019;119:1525–1532. [doi:10.1007/s00421-019-04142-5](https://doi.org/10.1007/s00421-019-04142-5).
5. [40 years of actigraphy in sleep medicine and current state of the art algorithms](https://consensus.app/papers/details/10e283907a46571eaa1664f0d5edf42f/?utm_source=claude_desktop). Patterson MR et al. *npj Digital Medicine*. 2023;6. [doi:10.1038/s41746-023-00802-1](https://doi.org/10.1038/s41746-023-00802-1).
6. [Measuring sleep: accuracy, sensitivity, and specificity of wrist actigraphy compared to polysomnography](https://consensus.app/papers/details/dacb61e851585861a393c7c62564b535/?utm_source=claude_desktop). Marino M et al. *Sleep*. 2013;36:1747–1755. [doi:10.5665/sleep.3142](https://doi.org/10.5665/sleep.3142).

### High-G physiology and validation sources

7. [Cerebral oxygenation and perfusion kinetics monitoring of military aircrew at high G using novel fNIRS wearable system](https://consensus.app/papers/details/be60cdabddf7548fb0435396bca3c287/?utm_source=claude_desktop). Roumengous T et al. *Frontiers in Neuroergonomics*. 2024;5. [doi:10.3389/fnrgo.2024.1357905](https://doi.org/10.3389/fnrgo.2024.1357905).
8. [Frontal cortical oxygenation changes during gravity-induced loss of consciousness in humans](https://consensus.app/papers/details/6cc7f6883b285555886d2e7eddd21896/?utm_source=claude_desktop). Kurihara K et al. *Journal of Applied Physiology*. 2007;103:1326–1331. [doi:10.1152/japplphysiol.01191.2006](https://doi.org/10.1152/japplphysiol.01191.2006).
9. [Changes in cerebral oxygen saturation and cerebral blood flow velocity under mild +Gz hypergravity](https://consensus.app/papers/details/d0d8e7137d41532e8cee034a8269b474/?utm_source=claude_desktop). Konishi T et al. *Journal of Applied Physiology*. 2019. [doi:10.1152/japplphysiol.00119.2019](https://doi.org/10.1152/japplphysiol.00119.2019).
10. [Consciousness monitoring using near-infrared spectroscopy during high +Gz exposures](https://doi.org/10.1016/j.medengphy.2004.07.003). Ryoo HC, Sun HH, Shender BS, Hrebien L. *Medical Engineering & Physics*. 2004;26:745–753. doi:10.1016/j.medengphy.2004.07.003.
11. [Heart Rate Variability as a Predictor of +Gz Tolerance During the High-G Selective Test](https://consensus.app/papers/details/19caa0b8d5d755dfa79167f6bcda5549/?utm_source=claude_desktop). Bacevic N et al. *Aerospace Medicine and Human Performance*. 2024;95:93–100. [doi:10.3357/AMHP.6319.2024](https://doi.org/10.3357/AMHP.6319.2024).
12. [Roles of Physiological Responses and Anthropometric Factors on the Gravitational Force Tolerance for Occupational Hypergravity Exposure](https://consensus.app/papers/details/f7675a41deae585eb828e5cfee39faaf/?utm_source=claude_desktop). Tu MY et al. *International Journal of Environmental Research and Public Health*. 2020;17:8061. [doi:10.3390/ijerph17218061](https://doi.org/10.3390/ijerph17218061).
13. [G Tolerance Prediction Model Using Mobile Device–Measured Cardiac Force Index for Military Aircrew](https://doi.org/10.2196/48812). Kuo MH et al. *JMIR mHealth and uHealth*. 2023;11:e48812. doi:10.2196/48812.
14. [The +Gz-induced loss of consciousness curve](https://doi.org/10.1186/2046-7648-2-19). Whinnery JE, Forster EM. *Extreme Physiology & Medicine*. 2013;2:19. doi:10.1186/2046-7648-2-19.
15. [Effect of novel short-arm human centrifugation-induced gravitational gradients upon cardiovascular responses, cerebral perfusion and G-tolerance](https://consensus.app/papers/details/7f86faae9fe350439da5ed109ba96122/?utm_source=claude_desktop). Laing C et al. *The Journal of Physiology*. 2020;598:4237–4249. [doi:10.1113/JP273615](https://doi.org/10.1113/JP273615).

### Statistical design sources

16. [Evaluation of clinical prediction models (part 3): calculating the sample size required for an external validation study](https://www.bmj.com/content/384/bmj-2023-074821). Riley RD et al. *BMJ*. 2024;384:e074821. [doi:10.1136/bmj-2023-074821](https://doi.org/10.1136/bmj-2023-074821).
17. [Minimum sample size calculations for external validation of a clinical prediction model with a time-to-event outcome](https://doi.org/10.1002/sim.9275). Riley RD, Collins GS, Ensor J et al. *Statistics in Medicine*. 2022;41:1280–1295. doi:10.1002/sim.9275.

All 15 journal DOIs used to develop this protocol were resolved through Crossref and screened in Scite on 2026-08-21. No retraction, expression-of-concern, or correction record affecting the cited claim was returned. Device specifications were taken from manufacturer documentation.

## 15. Search and evidence audit

Research performed on 2026-08-21 using the tools requested for this protocol:

- **Consensus MCP:** searches for Polar H10 versus ECG/HRV, actigraphy/sleep in pilots, and centrifuge +Gz physiological monitoring. The latter two initial calls were rate-limited and were rerun successfully after the required interval.
- **Tavily MCP:** searches for official wGT3X-BT specifications, official Polar H10/SDK specifications, high-G ECG/BP/NIRS methods, and external-validation sample-size guidance.
- **Firecrawl MCP:** searches plus direct extraction of the ActiGraph user-guide PDF, official Polar SDK page, field HRV device review, high-G fNIRS study, and the military-aircrew mobile G-tolerance study.
- **Paper-search MCP:** PubMed retrieval and Crossref DOI resolution.
- **Scite MCP:** editorial-notice/retraction and citation-context screening for every journal DOI included in the protocol.

The machine-readable query, tool, URL, DOI, and editorial-screening register is maintained at `docs/validation/validation_source_audit.json` so the audit can be rerun independently.

## 16. Pre-launch checklist

- [ ] Primary endpoint, time origin, censoring, and operational margin finalized.
- [ ] Ethics, military, centrifuge, flight-safety, engineering, and data-security approvals complete.
- [ ] Model, binary, input template, preprocessing, and statistical plan frozen and hashed.
- [ ] Arbitrary measured G(t)-to-EGP bridge implemented and unit-tested.
- [ ] Reference G system calibrated above the maximum exposure.
- [ ] H10 qualified against reference ECG across approved G/AGSM conditions.
- [ ] wGT3X-BT clipping documented; device designated non-reference for high G.
- [ ] BP transducer/reference level and hydrostatic correction validated.
- [ ] Visual endpoint task, synchronized video, and blinded adjudication manual piloted.
- [ ] Pilot-level sample-size simulation completed from feasibility data.
- [ ] Raw-data security, pseudonymization, telemetry classification, and export rules tested.
- [ ] Flight cohort remains untouched until the physiological layer is frozen.
- [ ] No procedure deliberately induces impairment in real aircraft.
