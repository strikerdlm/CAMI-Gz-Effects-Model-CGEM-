# Maneuver Hemodynamics — CGEM Cross-Sectional Analysis

This report compares cerebral-perfusion outcomes predicted by CGEM across every maneuver in `aerobatic_profiles.PROFILES`, evaluated for the standard midrange male pilot (`who_profile=2`) under five countermeasure configurations: **no_countermeasures**, **gsuit_only** (G-suit 5.5 PSI / 40% coverage), **agsm_only** (AGSM effectiveness 0.7), **full_countermeasures** (G-suit + AGSM + 30 mmHg PBG + 15° seat tilt), and **dehydrated** (full countermeasures with dehydration_level 0.5 and reduced AGSM/PBG).

All values are produced by the FAA CGEM Fortran model via `cgem_wrapper.run_cgem_for_profile()`. Times are in seconds from maneuver start. Cerebral-flow and HLAP minima reflect the deepest physiologic excursion observed during the run.

## Top G-LOC-prone maneuvers (no countermeasures)

| Maneuver | Category | Peak +Gz | t-greyout (s) | t-blackout (s) | t-G-LOC (s) |
|---|---|---:|---:|---:|---:|
| `corner_velocity_turn` | military_acm | 9.00 | 5.74 | 5.74 | **7.80** |
| `defensive_break_chaff_flare` | military_acm | 9.00 | 5.44 | 5.74 | **7.80** |
| `defensive_spiral` | military_acm | 7.50 | 5.54 | 5.94 | **8.00** |
| `defensive_break_9g` | military_acm | 9.00 | 5.86 | 6.04 | **8.10** |
| `rate_fight_sustained` | military_acm | 8.00 | 6.04 | 6.44 | **8.50** |
| `sustained_9g_turn` | military_acm | 9.00 | 6.34 | 6.34 | **8.55** |
| `slatted_high_aoa_turn` | military_acm | 7.50 | 6.04 | 6.54 | **8.60** |

## Countermeasure efficacy

For each maneuver that triggers G-LOC without countermeasures, this table shows whether full countermeasures prevent G-LOC entirely or merely delay it.

| Maneuver | t-G-LOC no-CM (s) | t-G-LOC full-CM (s) | t-G-LOC dehydrated (s) | Δ no-CM → full-CM |
|---|---:|---:|---:|---:|
| `corner_velocity_turn` | 7.80 | — | — | **prevented** |
| `defensive_break_chaff_flare` | 7.80 | — | — | **prevented** |
| `defensive_spiral` | 8.00 | — | — | **prevented** |
| `defensive_break_9g` | 8.10 | — | — | **prevented** |
| `rate_fight_sustained` | 8.50 | — | — | **prevented** |
| `sustained_9g_turn` | 8.55 | — | — | **prevented** |
| `slatted_high_aoa_turn` | 8.60 | — | — | **prevented** |

## Push-pull stress (ms below 0 G)

Maneuvers with the largest negative-G exposure (cumulative ms with Nz < -0.1) are the operational worst case for push-pull cerebral perfusion deficit when followed by a positive pull.

| Maneuver | Category | ms below 0 G | Min HLAP (mmHg) | Min F_con | Min c_bank (s) |
|---|---|---:|---:|---:|---:|
| `outside_inside_vert8` | championship | 18 | 100.00 | 0.00 | 6.12 |
| `half_vert_roll_neg_pull` | championship | 18 | 100.00 | 42.95 | 7.10 |
| `horizontal_rolling_360` | championship | 16 | 100.00 | 21.70 | 7.10 |
| `english_bunt` | championship | 13 | 100.00 | 0.00 | 5.61 |
| `inverted_flat_spin` | championship | 11 | 100.00 | 49.50 | 7.10 |
| `snap_45deg_down_roll` | championship | 9 | 100.00 | 0.00 | 6.41 |
| `inverted_spin` | championship | 9 | 100.00 | 49.50 | 7.10 |
| `hammerhead` | championship | 7 | 100.00 | 42.95 | 7.10 |
| `outside_360` | championship | 6 | 100.00 | 42.95 | 7.10 |
| `triple_push_pull_loop` | conceptual | 6 | 100.00 | 4.71 | 5.61 |
| `inverted_spin_recovery` | extreme_post_stall | 6 | 100.00 | 0.00 | 5.49 |
| `quarter_down_roll` | championship | 5 | 100.00 | 0.00 | 6.21 |
| `triple_push_pull_immelmann` | conceptual | 5 | 100.00 | 37.38 | 7.10 |
| `triple_push_pull_split_s` | conceptual | 5 | 100.00 | 45.74 | 7.10 |
| `tailslide_negative` | championship | 4 | 100.00 | 32.56 | 7.10 |
| `square_loop` | championship | 3 | 100.00 | 0.00 | 6.00 |
| `strike_turn_strafing_pullout` | military_acm | 3 | 100.00 | 0.00 | 1.71 |
| `push_pull_missile_evasion` | military_acm | 3 | 100.00 | 0.00 | -0.07 |
| `helicopter_bugout` | military_acm | 3 | 100.00 | 0.00 | 4.43 |
| `lomcovak_repeats` | extreme_post_stall | 3 | 100.00 | 0.00 | 3.23 |

## Per-category cross-config table

Each row gives the time-to-G-LOC (in seconds) across the five configurations. `—` means no G-LOC was triggered. **Bold** entries indicate G-LOC events under that configuration.

### Championship

| Maneuver | Peak ±Gz | no countermeasures | gsuit only | agsm only | full countermeasures | dehydrated |
|---|---:|---:|---:|---:|---:|---:|
| `avalanche` | +6.0 / -1.0 | — | — | — | — | — |
| `cuban_eight` | +4.8 / +0.0 | — | — | — | — | — |
| `double_immelmann` | +5.0 / -0.5 | — | — | — | — | — |
| `english_bunt` | +0.5 / -4.5 | — | — | — | — | — |
| `flat_spin_positive` | +2.5 / -0.5 | — | — | — | — | — |
| `half_vert_roll_neg_pull` | +2.0 / -3.0 | — | — | — | — | — |
| `hammerhead` | +2.0 / -2.0 | — | — | — | — | — |
| `hesitation_roll_4pt` | +1.0 / -1.0 | — | — | — | — | — |
| `hesitation_roll_8pt` | +1.0 / -1.0 | — | — | — | — | — |
| `horizontal_rolling_360` | +2.0 / -1.5 | — | — | — | — | — |
| `humpty_bump_negative` | +5.5 / -4.0 | — | — | — | — | — |
| `humpty_bump_positive` | +5.5 / -0.5 | — | — | — | — | — |
| `immelmann_turn` | +5.0 / +0.0 | — | — | — | — | — |
| `inverted_flat_spin` | +2.0 / -2.5 | — | — | — | — | — |
| `inverted_spin` | +3.0 / -2.5 | — | — | — | — | — |
| `knife_edge_pass_highg` | +6.0 / -0.3 | — | — | — | — | — |
| `lazy_eight` | +2.5 / +0.5 | — | — | — | — | — |
| `loop_standard` | +4.5 / +0.0 | — | — | — | — | — |
| `outside_360` | +0.5 / -3.5 | — | — | — | — | — |
| `outside_inside_vert8` | +4.0 / -3.0 | — | — | — | — | — |
| `outside_snap_level` | +1.5 / -4.5 | — | — | — | — | — |
| `quarter_clover` | +5.0 / -0.5 | — | — | — | — | — |
| `quarter_down_roll` | +2.0 / -3.0 | — | — | — | — | — |
| `reverse_cuban_eight` | +5.0 / -1.0 | — | — | — | — | — |
| `reverse_half_cuban` | +5.0 / -1.0 | — | — | — | — | — |
| `slow_roll_level` | +1.0 / -1.0 | — | — | — | — | — |
| `snap_45deg_down_roll` | +4.0 / -1.5 | — | — | — | — | — |
| `snap_roll_level` | +6.0 / -1.0 | — | — | — | — | — |
| `split_s` | +5.0 / +0.0 | — | — | — | — | — |
| `square_loop` | +6.0 / -0.2 | — | — | — | — | — |
| `tailslide_negative` | +1.0 / -2.5 | — | — | — | — | — |
| `tailslide_positive` | +3.5 / -0.5 | — | — | — | — | — |
| `torque_roll` | +2.5 / -0.5 | — | — | — | — | — |
| `vertical_eight` | +4.6 / -0.4 | — | — | — | — | — |
| `vertical_snap_upline` | +6.0 / -1.5 | — | — | — | — | — |

### Military Acm

| Maneuver | Peak ±Gz | no countermeasures | gsuit only | agsm only | full countermeasures | dehydrated |
|---|---:|---:|---:|---:|---:|---:|
| `barrel_roll_attack` | +5.0 / +0.0 | — | — | — | — | — |
| `combat_immelmann` | +7.0 / +0.0 | — | — | — | — | — |
| `combat_split_s` | +8.0 / -0.5 | — | — | — | — | — |
| `corner_velocity_turn` | +9.0 / +0.0 | **7.80** | — | — | — | — |
| `defensive_break_9g` | +9.0 / +0.0 | **8.10** | — | — | — | — |
| `defensive_break_chaff_flare` | +9.0 / +0.0 | **7.80** | — | — | — | — |
| `defensive_jink` | +6.5 / -0.5 | — | — | — | — | — |
| `defensive_spiral` | +7.5 / +0.0 | **8.00** | — | — | — | — |
| `flat_scissors_defensive` | +4.5 / +0.5 | — | — | — | — | — |
| `helicopter_bugout` | +4.5 / -0.7 | — | — | — | — | — |
| `high_g_turn` | +6.8 / +0.0 | — | — | — | — | — |
| `high_yoyo_offensive` | +6.0 / +0.5 | — | — | — | — | — |
| `lag_pursuit_roll` | +4.0 / +0.0 | — | — | — | — | — |
| `last_ditch_break` | +9.5 / -1.0 | — | — | — | — | — |
| `low_yoyo_offensive` | +7.0 / +0.0 | — | — | — | — | — |
| `push_pull_missile_evasion` | +7.0 / -1.5 | — | — | — | — | — |
| `rate_fight_sustained` | +8.0 / +0.0 | **8.50** | **8.50** | **8.50** | — | — |
| `rolling_scissors` | +5.0 / +0.5 | — | — | — | — | — |
| `slatted_high_aoa_turn` | +7.5 / +0.0 | **8.60** | **8.75** | **8.60** | — | — |
| `strike_turn_strafing_pullout` | +7.0 / -1.0 | — | — | — | — | — |
| `sustained_9g_turn` | +9.0 / +0.0 | **8.55** | **8.70** | **8.70** | — | — |
| `vertical_climb_missile_evasion` | +7.0 / +0.0 | — | — | — | — | — |

### Extreme Post Stall

| Maneuver | Peak ±Gz | no countermeasures | gsuit only | agsm only | full countermeasures | dehydrated |
|---|---:|---:|---:|---:|---:|---:|
| `bell_tailslide` | +3.5 / -2.0 | — | — | — | — | — |
| `falling_leaf` | +2.5 / -1.2 | — | — | — | — | — |
| `helicopter_maneuver` | +3.5 / -1.2 | — | — | — | — | — |
| `herbst_jturn` | +3.8 / -0.5 | — | — | — | — | — |
| `inverted_cobra` | +1.0 / -5.5 | — | — | — | — | — |
| `inverted_spin_recovery` | +6.0 / -2.5 | — | — | — | — | — |
| `kulbit` | +8.0 / -1.8 | — | — | — | — | — |
| `lomcovak` | +6.5 / -5.5 | — | — | — | — | — |
| `lomcovak_repeats` | +6.5 / -5.5 | — | — | — | — | — |
| `pugachev_cobra` | +6.5 / -0.4 | — | — | — | — | — |
| `snake_modulated` | +3.8 / -2.0 | — | — | — | — | — |
| `tailslide_tumble` | +6.0 / -5.0 | — | — | — | — | — |

### Conceptual

| Maneuver | Peak ±Gz | no countermeasures | gsuit only | agsm only | full countermeasures | dehydrated |
|---|---:|---:|---:|---:|---:|---:|
| `triple_push_pull_immelmann` | +6.0 / -3.0 | — | — | — | — | — |
| `triple_push_pull_loop` | +5.0 / -3.0 | — | — | — | — | — |
| `triple_push_pull_split_s` | +6.0 / -3.0 | — | — | — | — | — |

## Sustained-G endurance maneuvers

Maneuvers with explicit sustained-G plateaus (`sustained_gz` set in the catalog). These are the principal AGSM-endurance and G-tolerance-test profiles.

| Maneuver | Plateau +Gz | Plateau (s) | t-G-LOC no-CM | t-G-LOC full-CM | Min c_bank (no-CM) |
|---|---:|---:|---:|---:|---:|
| `defensive_break_9g` | 9.0 | 4.0 | 8.10 | — | 0.00 |
| `sustained_9g_turn` | 9.0 | 25.0 | 8.55 | — | 0.00 |
| `corner_velocity_turn` | 9.0 | 3.0 | 7.80 | — | 0.00 |
| `defensive_break_chaff_flare` | 8.5 | 2.5 | 7.80 | — | 0.00 |
| `combat_split_s` | 7.5 | 2.5 | — | — | 0.81 |
| `rate_fight_sustained` | 7.5 | 18.0 | 8.50 | — | 0.00 |
| `slatted_high_aoa_turn` | 7.2 | 10.0 | 8.60 | — | 0.00 |
| `low_yoyo_offensive` | 7.0 | 2.5 | — | — | 1.21 |
| `defensive_spiral` | 7.0 | 12.0 | 8.00 | — | 0.00 |
| `high_g_turn` | 6.5 | 4.0 | — | — | 0.11 |
| `combat_immelmann` | 6.5 | 2.5 | — | — | 2.00 |
| `strike_turn_strafing_pullout` | 6.5 | 3.0 | — | — | 1.71 |
| `push_pull_missile_evasion` | 6.5 | 3.5 | — | — | -0.07 |
| `vertical_climb_missile_evasion` | 6.5 | 2.5 | — | — | 4.00 |
| `high_yoyo_offensive` | 5.5 | 2.0 | — | — | 4.00 |
| `barrel_roll_attack` | 4.5 | 6.0 | — | — | 0.07 |
| `rolling_scissors` | 4.5 | 5.0 | — | — | 4.15 |
| `flat_scissors_defensive` | 4.0 | 1.5 | — | — | 5.81 |
| `helicopter_bugout` | 4.0 | 2.5 | — | — | 4.43 |
| `lag_pursuit_roll` | 3.5 | 6.0 | — | — | 7.10 |

## Methodology and caveats

- **Pilot model.** All runs use `who_profile=2` (standard midrange male). Use `--who all` in `run_cgem_batch.py` to expand across subjects 1–6. The CGEM Fortran subject database (set via `who`) overrides custom physiology when a standard profile is selected.
- **Onset-rate fidelity.** Snap rolls and Cobra-class spikes are represented as 100–250 ms cells, which translates to onset rates 30–60 G/s in CGEM. The model is validated through ~10 G/s onset (Copeland & Whinnery 2023, DOI:10.21949/1524446); behaviour above that ceiling is extrapolated.
- **Scalar Nz only.** CGEM models +Gz / −Gz only. Lateral (Gy) and longitudinal (Gx) loads from snap rolls, flat spins, and Lomcovák-class tumbling are not represented; the +Gz time series underestimates true physiologic stress for those maneuvers.
- **Push-pull effect.** CGEM does include a push-pull delay model (transient HR-response delay after −Gz). Rankings here capture the model's prediction; field measurements from Banks et al. and the FAA OAM tech reports should be used to calibrate operational thresholds.
- **Profile provenance.** New profiles added in this extension were constructed from kinematic-phase reconstruction calibrated against the canonical CGEM samples and standard aerobatic / fighter-doctrine references (FAI/CIVA Aresti catalogue, Shaw 1985, Newman & Callister 2009 DOI:10.3357/asem.2361.2009). They are not flight-test telemetry. See `tools/extension_profiles.py` for per-maneuver source notes.

---

_Generated by `tools/build_hemodynamics_report.py` from `data/batch_results/summary.json`._
