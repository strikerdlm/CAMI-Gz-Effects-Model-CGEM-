# §3.1 Dataset Descriptives Correction

## Source data

- **Parquet path:** `/root/repos/CAMI-Gz-Effects-Model-CGEM-/data/datasets/cgem_synthetic_v1.parquet`
- **Row count:** 3,240 (all `status = "ok"`, no `error` rows)
- **Parquet SHA-256:** `a4814850b36069ade29d3bbb0f048443ada80e613ae73a00912e93cdbf95989f`
- **Metadata sidecar:** `data/datasets/cgem_synthetic_v1.meta.json` (run_id `45e8dc24dce14afaa09dd604df21805e`, master_seed 42, binary_sha256 `a6f57c67616b78f5fee757cb066f356bd8ea9856cd1a941cc304c343334b7da7`, generated 2026-04-30T12:00:00Z, host `asterphysiology`)
- **Verification commands:**
  ```bash
  sha256sum data/datasets/cgem_synthetic_v1.parquet
  python -c "import pandas as pd; df=pd.read_parquet('data/datasets/cgem_synthetic_v1.parquet'); print(df.shape, df['maneuver_category'].value_counts().sort_index())"
  python -c "import pandas as pd; df=pd.read_parquet('data/datasets/cgem_synthetic_v1.parquet'); print(df.groupby('maneuver_category')[['event_greyout','event_blackout','event_gloc']].mean()*100)"
  ```
- **Computed descriptives (data-truth):**

  | maneuver_category   | n_maneuvers | n_rows | %     | greyout % | blackout % | G-LOC % | mean G-peak | mean dG/dt | mean duration s |
  |---------------------|------------:|-------:|------:|----------:|-----------:|--------:|------------:|-----------:|----------------:|
  | championship        | 35          | 1,575  | 48.6  | 4.8       | 0.4        | 0.1     | 4.16        | 5.97       | 13.39           |
  | conceptual          | 3           |   135  |  4.2  | 1.5       | 0.0        | 0.0     | 3.23        | 3.09       | 14.67           |
  | extreme_post_stall  | 12          |   540  | 16.7  | 7.6       | 1.1        | 0.4     | 5.22        | 13.59      |  9.21           |
  | military_acm        | 22          |   990  | 30.6  | 49.6      | 36.1       | 20.3    | 6.99        |  8.70      | 15.80           |
  | **Overall**         | **72**      | **3,240** | 100.0 | **18.8** | **11.4**   | **6.3** | 5.16        |  7.95      | 13.48           |

  Continuous targets (overall): `hlap_min` mean 97.17 mmHg (SD 8.07; IQR [94.75, 100.00]; range [80.00, 110.06]); `c_bank_min` mean 6.52 cm/s (SD 3.81; IQR [4.73, 7.10]; range [−1.35, 15.00]).

  Pilot-configuration distribution: standard arm 1,296 rows (40.0 %) — 216 rows per FAA `who_profile` 1–6 (6 × 216 = 1,296); custom arm (`who_custom`) 1,944 rows (60.0 %), spanning the full 3 × 3 × 3 grid (g_tolerance_multiplier × dehydration_level × countermeasure tier). Countermeasure-tier counts (across both arms): 1,080 per tier (`none`, `agsm`, `suit_agsm`). Dehydration levels: 1,944 rows at 0.0, 648 at 0.3 (`mild`), 648 at 0.7 (`severe`).

## Original (incorrect) text — quoted from manuscript.md

Lines 121–123:

```
### 3.1 Dataset characteristics

The synthetic dataset comprises 3,240 rows over 72 maneuvers and 45 pilot configurations, with category sizes of 720 (championship, 22.2 %), 720 (conceptual, 22.2 %), 720 (extreme post-stall, 22.2 %), and 1,080 (military ACM, 33.3 %); event rates were 64.8 % (greyout), 58.3 % (blackout), and 50.6 % (G-LOC), lowest in the conceptual category (low-G, short-duration) and highest in military ACM (sustained 7–9 G turns).
```

## Corrected text — drop-in replacement

```
### 3.1 Dataset characteristics

The synthetic dataset comprises 3,240 rows over 72 maneuvers and 45 pilot configurations per maneuver, with unbalanced category sizes reflecting the maneuver-catalogue census: 1,575 rows (championship, 48.6 %; 35 maneuvers), 135 rows (conceptual, 4.2 %; 3 maneuvers), 540 rows (extreme post-stall, 16.7 %; 12 maneuvers), and 990 rows (military ACM, 30.6 %; 22 maneuvers). Overall event rates were 18.8 % (greyout), 11.4 % (blackout), and 6.3 % (G-LOC), concentrated almost entirely in the military-ACM category (49.6 % greyout, 36.1 % blackout, 20.3 % G-LOC; mean G-peak 6.99, mean profile duration 15.8 s) — the sustained 7–9 G turns that dominate the sustained-+Gz training distribution. The championship (G-LOC 0.1 %), conceptual (G-LOC 0.0 %), and extreme-post-stall (G-LOC 0.4 %) categories sit at the low-event-rate, low-/non-sustained-G end of the distribution and contribute to the censoring rate (overall 93.7 % G-LOC-censored, 88.6 % blackout-censored, 81.2 % greyout-censored). This unbalanced structure motivates the per-`maneuver_category` Mondrian conformal stratification in §2.4 and is reflected in the per-stratum sample sizes that drive the §3.3 coverage table.
```

## Per-claim audit

| Claim in original §3.1 | Actual value (data-truth) | Source | Change |
|---|---|---|---|
| "3,240 rows over 72 maneuvers and 45 pilot configurations" | 3,240 rows, 72 maneuvers, 45 configurations per maneuver | `df.shape`, `df['maneuver'].nunique()`, rows/maneuver = 3240/72 = 45 | Kept (correct). Reworded to "45 pilot configurations per maneuver" for unambiguity. |
| "720 (championship, 22.2 %)" | 1,575 (championship, 48.6 %) | `df['maneuver_category'].value_counts()` | **CORRECTED.** |
| "720 (conceptual, 22.2 %)" | 135 (conceptual, 4.2 %) | same | **CORRECTED.** |
| "720 (extreme post-stall, 22.2 %)" | 540 (extreme post-stall, 16.7 %) | same | **CORRECTED.** |
| "1,080 (military ACM, 33.3 %)" | 990 (military ACM, 30.6 %) | same | **CORRECTED.** |
| "event rates were 64.8 % (greyout)" | 18.8 % overall | `df['event_greyout'].mean()` | **CORRECTED.** |
| "58.3 % (blackout)" | 11.4 % overall | `df['event_blackout'].mean()` | **CORRECTED.** |
| "50.6 % (G-LOC)" | 6.3 % overall | `df['event_gloc'].mean()` | **CORRECTED.** |
| "lowest in the conceptual category (low-G, short-duration)" | Conceptual is low-G (mean G-peak 3.23) but mean duration 14.67 s — *longer* than championship (13.39 s) and extreme-post-stall (9.21 s). | `df.groupby('maneuver_category')[['profile_duration_s','g_peak_abs']].mean()` | **CORRECTED.** "Short-duration" claim removed; replaced by accurate per-category G-LOC rate enumeration. |
| "highest in military ACM (sustained 7–9 G turns)" | Mean G-peak 6.99 (range [4.0, 9.5]) in military ACM; mean duration 15.80 s. The descriptor is accurate. | same | Kept (correct, slightly tightened). |

Additionally, the corrected text adds per-category event rates explicitly — closing the reviewer's "~315 G-LOC events implied" vs "n = 36 G-LOC events in Table 2" loop (the actual G-LOC event count is 205 across the full dataset and 36 in the test split, with 35 of those 36 in the military-ACM stratum). The corrected text also adds the overall censoring rates (81.2 / 88.6 / 93.7 %), which are operationally meaningful and were absent from the original.

## Additional findings

1. **§3.5 LOGO holdout table (Table 4) is consistent with the data.** The reviewer's assumption is correct. Re-verifying directly against the Parquet:

   | Held-out category | §3.5 reports n_train / n_test | Data-implied n_train / n_test | Match |
   |---|---|---|---|
   | championship       | 1,665 / 1,575 | (3240 − 1575) / 1575 = 1,665 / 1,575 | ✓ |
   | conceptual         | 3,105 / 135   | (3240 − 135) / 135   = 3,105 / 135   | ✓ |
   | extreme_post_stall | 2,700 / 540   | (3240 − 540) / 540   = 2,700 / 540   | ✓ |
   | military_acm       | 2,250 / 990   | (3240 − 990) / 990   = 2,250 / 990   | ✓ |

   The same n_test column matches the actual `maneuver_category.value_counts()`. §3.5 (and the §2.3 LOGO sentence on line 67) do not need correction.

2. **§2.3 split sizes — minor wording inaccuracy worth flagging.** Line 65 currently says: "the test split (15 %, **~486 rows**) is held out for all Section 3 metrics." Re-running `cgem_ext.data.splits.stratified_split(df, seed=42)` reproduces sizes `train=2,267, val=486, test=487`. The **validation** split is exactly 486; the **test** split is 487. Table 2 in §3.3 correctly cites "Overall (n = 487)" in every classifier row, so the §2.3 ~486 is the small inconsistency. Recommend either (a) softening to "approximately 486" (already softened) and treating as no-change, or (b) updating §2.3 to "the test split (15 %, n = 487 rows)". This is not a §3.1 fix — flagging it for the main session.

3. **Pilot-configuration counts cross-check.** §2.2 states "Standard arm: 6 × 3 = 18 rows per maneuver, 1,296 rows total" and "Custom arm: 27 rows per maneuver, 1,944 rows total." Both reproduce exactly from the Parquet (`arm == 'standard'` → 1,296; `arm == 'custom'` → 1,944; row totals 18 × 72 = 1,296 and 27 × 72 = 1,944).

4. **The original §3.1 paragraph appears to be carry-over from a balanced-grid earlier dataset version.** The 720/720/720/1,080 split corresponds to 16/16/16/24 maneuvers × 45 configurations — a balanced-by-category grid of 72 maneuvers (16 + 16 + 16 + 24 = 72). The committed catalogue is 35/3/12/22 maneuvers per category, so the original paragraph was last refreshed when the catalogue was still balanced. The reviewer's hypothesis about pre-PMEA-pivot drift is correct.

5. **Reviewer's 6.3 % G-LOC-rate footnote in the table on line 37 is correct;** the manuscript's "50.6 %" cannot be reproduced from any subset of the committed Parquet (event_gloc = 1 fraction at 6.3 % overall, 0.1 / 0.0 / 0.4 / 20.3 % per category, maximum stratum rate = 20.3 % for military ACM).

6. **Recommend committing `scripts/audit_section_3_1.py` as the reviewer suggested** — would prevent recurrence. The compute is < 1 s; the script can `assert` each numerical claim against the Parquet at render time. Out of scope for this fix but logged for the main session.
