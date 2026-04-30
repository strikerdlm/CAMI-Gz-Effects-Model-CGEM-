# Maneuver Index

Categorized index of every maneuver registered in
`aerobatic_profiles.PROFILES` with structured metadata from
`maneuvers_catalog.py`. Sorted within each category by approximate
hemodynamic stress (peak +Gz × duration). Source files live under
`Aerobatics_sample_inputs/`.

For per-maneuver hemodynamic predictions across pilot configurations,
see [`MANEUVER_HEMODYNAMICS.md`](MANEUVER_HEMODYNAMICS.md).

---

## Championship (Aresti / IAC catalogue)

| Identifier | Aresti family | Peak +Gz | Peak -Gz | Onset (G/s) | Duration (s) | Source file |
|---|---:|---:|---:|---:|---:|---|
| `loop_standard` | 7 | 4.5 | 0.0 | 3.0 | 8.5 | `loop_standard.txt` |
| `immelmann_turn` | 8 | 5.0 | 0.0 | 3.5 | 8.0 | `immelmann_turn.txt` |
| `split_s` | 8 | 5.0 | 0.0 | 3.5 | 8.0 | `split_s.txt` |
| `cuban_eight` | 8 | 4.8 | 0.0 | 3.0 | 11.5 | `cuban_eight.txt` |
| `vertical_eight` | 7 | 4.6 | -0.4 | 3.0 | 12.0 | `vertical_eight.txt` |
| `outside_360` | 7 | 0.5 | -3.5 | 2.0 | 9.0 | `outside360.txt` |
| `outside_inside_vert8` | 7 | 4.0 | -3.0 | 2.5 | 18.0 | `outsideinsidevertical8.txt` |
| `hammerhead` | 5 | 2.0 | -2.0 | 2.0 | 22.0 | `hammerhead.txt` |
| `horizontal_rolling_360` | 9 | 2.0 | -1.5 | 2.0 | 4.5 | `horizontalrolling360.txt` |
| `quarter_down_roll` | 8 | 2.0 | -3.0 | 3.0 | 8.0 | `quarterdownroll.txt` |
| `snap_45deg_down_roll` | 9 | 4.0 | -1.5 | 10.0 | 6.0 | `snap45degdownroll.txt` |
| `half_vert_roll_neg_pull` | 8 | 2.0 | -3.0 | 3.0 | 7.0 | `halfverticalrollwnegpullout.txt` |
| `avalanche` | 7 | 6.0 | -1.0 | 3.0 | 9.0 | `avalanche.txt` |
| `tailslide_positive` | 6 | 3.5 | -0.5 | 5.0 | 10.0 | `tailslide_positive.txt` |
| `tailslide_negative` | 6 | 1.0 | -2.5 | 5.0 | 10.0 | `tailslide_negative.txt` |
| `humpty_bump_positive` | 8 | 5.5 | -0.5 | 4.0 | 14.0 | `humpty_bump_positive.txt` |
| `humpty_bump_negative` | 8 | 5.5 | -4.0 | 3.5 | 14.0 | `humpty_bump_negative.txt` |
| `square_loop` | 7 | 6.0 | -0.2 | 5.5 | 15.0 | `square_loop.txt` |
| `reverse_cuban_eight` | 7 | 5.0 | -1.0 | 3.5 | 18.0 | `reverse_cuban_eight.txt` |
| `snap_roll_level` | 9 | 6.0 | -1.0 | 18.0 | 5.0 | `snap_roll_level.txt` |
| `vertical_snap_upline` | 9 | 6.0 | -1.5 | 18.0 | 9.0 | `vertical_snap_upline.txt` |
| `outside_snap_level` | 9 | 1.5 | -4.5 | 18.0 | 5.0 | `outside_snap_level.txt` |
| `hesitation_roll_4pt` | 9 | 1.0 | -1.0 | 2.5 | 6.0 | `hesitation_roll_4pt.txt` |
| `hesitation_roll_8pt` | 9 | 1.0 | -1.0 | 2.0 | 8.0 | `hesitation_roll_8pt.txt` |
| `slow_roll_level` | 9 | 1.0 | -1.0 | 1.5 | 5.0 | `slow_roll_level.txt` |
| `inverted_spin` | 9 | 3.0 | -2.5 | 4.0 | 14.0 | `inverted_spin.txt` |
| `flat_spin_positive` | 9 | 2.5 | -0.5 | 3.0 | 14.0 | `flat_spin_positive.txt` |
| `inverted_flat_spin` | 9 | 2.0 | -2.5 | 4.0 | 14.0 | `inverted_flat_spin.txt` |
| `english_bunt` | 7 | 0.5 | -4.5 | 3.0 | 16.0 | `english_bunt.txt` |
| `torque_roll` | 1 | 2.5 | -0.5 | 3.0 | 10.0 | `torque_roll.txt` |
| `knife_edge_pass_highg` | 1 | 6.0 | -0.3 | 5.0 | 10.0 | `knife_edge_pass_highg.txt` |
| `double_immelmann` | 8 | 5.0 | -0.5 | 3.5 | 16.0 | `double_immelmann.txt` |
| `quarter_clover` | 7 | 5.0 | -0.5 | 3.5 | 12.0 | `quarter_clover.txt` |
| `reverse_half_cuban` | 7 | 5.0 | -1.0 | 3.0 | 10.0 | `reverse_half_cuban.txt` |
| `lazy_eight` | 7 | 2.5 | 0.5 | 0.5 | 24.0 | `lazy_eight.txt` |

## Military ACM / BFM

| Identifier | Aircraft | Peak +Gz | Peak -Gz | Onset (G/s) | Sustained Gz × s | Duration (s) | Source file |
|---|---|---:|---:|---:|---:|---:|---|
| `high_g_turn` | Generic fighter | 6.8 | 0.0 | 4.0 | 6.5 × 4 | 10.0 | `high_g_turn.txt` |
| `defensive_break_9g` | F-16C | 9.0 | 0.0 | 7.0 | 9.0 × 4 | 17.0 | `military_defensive_break_9g.txt` |
| `sustained_9g_turn` | F-16C / F-22A | 9.0 | 0.0 | 6.0 | 9.0 × 25 | 38.0 | `military_sustained_9g_turn.txt` |
| `corner_velocity_turn` | F-16C | 9.0 | 0.0 | 9.0 | 9.0 × 3 | 12.0 | `military_corner_velocity_turn.txt` |
| `high_yoyo_offensive` | F-15C / F-16C | 6.0 | 0.5 | 5.0 | 5.5 × 2 | 13.0 | `military_high_yoyo.txt` |
| `low_yoyo_offensive` | F-16C / F/A-18 | 7.0 | 0.0 | 6.0 | 7.0 × 2.5 | 13.0 | `military_low_yoyo.txt` |
| `barrel_roll_attack` | F-15C / Su-27 | 5.0 | 0.0 | 3.0 | 4.5 × 6 | 14.0 | `military_barrel_roll_attack.txt` |
| `lag_pursuit_roll` | F-16C | 4.0 | 0.0 | 3.0 | 3.5 × 6 | 13.0 | `military_lag_pursuit_roll.txt` |
| `flat_scissors_defensive` | F/A-18 | 4.5 | 0.5 | 4.0 | 4.0 × 1.5 | 16.0 | `military_flat_scissors.txt` |
| `rolling_scissors` | F-16C / F/A-18 | 5.0 | 0.5 | 3.0 | 4.5 × 5 | 18.0 | `military_rolling_scissors.txt` |
| `defensive_jink` | A-10 / F-16C | 6.5 | -0.5 | 10.0 | — | 10.0 | `military_defensive_jink.txt` |
| `last_ditch_break` | F-16C / F/A-18 | 9.5 | -1.0 | 13.0 | — | 6.0 | `military_last_ditch_break.txt` |
| `combat_immelmann` | F-16C / F-15C | 7.0 | 0.0 | 6.0 | 6.5 × 2.5 | 14.0 | `military_combat_immelmann.txt` |
| `combat_split_s` | F-16C / F/A-18 | 8.0 | -0.5 | 7.0 | 7.5 × 2.5 | 14.0 | `military_combat_split_s.txt` |
| `defensive_break_chaff_flare` | F-16C / F-15E | 9.0 | 0.0 | 8.0 | 8.5 × 2.5 | 14.0 | `military_defensive_break_chaff_flare.txt` |
| `strike_turn_strafing_pullout` | A-10C / F-16C | 7.0 | -1.0 | 7.0 | 6.5 × 3 | 16.0 | `military_strike_pullout.txt` |
| `push_pull_missile_evasion` | F-16C / F/A-18 | 7.0 | -1.5 | 6.0 | 6.5 × 3.5 | 13.0 | `military_push_pull_evasion.txt` |
| `defensive_spiral` | F-16C / Su-27 | 7.5 | 0.0 | 6.0 | 7.0 × 12 | 22.0 | `military_defensive_spiral.txt` |
| `rate_fight_sustained` | F-16C / Eurofighter | 8.0 | 0.0 | 6.0 | 7.5 × 18 | 30.0 | `military_rate_fight.txt` |
| `vertical_climb_missile_evasion` | F-15C / F-22A | 7.0 | 0.0 | 6.0 | 6.5 × 2.5 | 22.0 | `military_vertical_climb_evasion.txt` |
| `helicopter_bugout` | F/A-18 / F-16C | 4.5 | -0.7 | 3.0 | 4.0 × 2.5 | 17.0 | `military_helicopter_bugout.txt` |
| `slatted_high_aoa_turn` | F/A-18 | 7.5 | 0.0 | 5.0 | 7.2 × 10 | 22.0 | `military_slatted_high_aoa_turn.txt` |

## Extreme / post-stall

| Identifier | Aircraft / origin | Peak +Gz | Peak -Gz | Onset (G/s) | Duration (s) | Source file |
|---|---|---:|---:|---:|---:|---|
| `pugachev_cobra` | Su-27 / Su-35 | 6.5 | -0.4 | 30.0 | 5.0 | `pugachev_cobra.txt` |
| `kulbit` | Su-37 / Su-30MKI | 8.0 | -1.8 | 35.0 | 7.0 | `kulbit.txt` |
| `lomcovak` | Z-50 / Extra 300 / Su-26 | 6.5 | -5.5 | 45.0 | 6.0 | `lomcovak.txt` |
| `lomcovak_repeats` | Extra 330SC / Su-26 / MX-2 | 6.5 | -5.5 | 50.0 | 14.0 | `lomcovak_repeats.txt` |
| `herbst_jturn` | X-31 / F-22A / F-18 HARV | 3.8 | -0.5 | 12.0 | 12.0 | `herbst_jturn.txt` |
| `helicopter_maneuver` | Su-27 / Su-35 / MiG-29 OVT | 3.5 | -1.2 | 15.0 | 12.0 | `helicopter_maneuver.txt` |
| `falling_leaf` | F-18 HARV / X-31 / Su-35 | 2.5 | -1.2 | 8.0 | 16.0 | `falling_leaf.txt` |
| `tailslide_tumble` | Extra 300 / Su-26 / Edge 540 | 6.0 | -5.0 | 50.0 | 9.0 | `tailslide_tumble.txt` |
| `inverted_cobra` | Theoretical (Extra 300L) | 1.0 | -5.5 | 30.0 | 5.0 | `inverted_cobra.txt` |
| `inverted_spin_recovery` | T-6 / Pitts / Extra 300 | 6.0 | -2.5 | 25.0 | 16.0 | `inverted_spin_recovery.txt` |
| `bell_tailslide` | Sukhoi Su-26 / Extra 300 / MX-2 | 3.5 | -2.0 | 15.0 | 14.0 | `bell_tailslide.txt` |
| `snake_modulated` | F-18 HARV / X-31 | 3.8 | -2.0 | 20.0 | 14.0 | `snake_modulated.txt` |

## Conceptual demo profiles

These are not flight-realistic; they exist to stress-test the CGEM model
for push-pull and high-cycle scenarios.

| Identifier | Description | Source file |
|---|---|---|
| `triple_push_pull_loop` | Three back-to-back push (-G) → pull (+G) loops | `triple_push_pull_loop.txt` |
| `triple_push_pull_immelmann` | Push-pull + half-roll repeated ×3 | `triple_push_pull_immelmann.txt` |
| `triple_push_pull_split_s` | Three consecutive push-pull Split-S entries | `triple_push_pull_split_s.txt` |
