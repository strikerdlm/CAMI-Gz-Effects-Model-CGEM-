# Aerobatic G-Profile Library

This document accompanies `aerobatic_profiles.py` and explains how to work with
aerobatic manoeuvre data inside this repository.

---

## What is an **aerobatic G-profile**?

During an aerobatic manoeuvre a pilot is exposed to rapidly changing vertical
accelerations (\(+G_z\) and \(-G_z\)).  For engineering and medical research
purposes these accelerations can be captured as a time series of discrete
samples:

```
Nz, duration_ms
+4.2,   500   ← 4.2 G sustained for 500 ms
+5.0,   300   ← 5.0 G for 0.3 s
-1.0,  1000   ← –1 G for 1 s
```

Feeding such a series into the **Combined-G Effects Model (CGEM)** allows us to
predict physiological responses of the human body (e.g. blood pressure curves,
visual field loss, G-LOC likelihood).

All sample files are located in `Aerobatics_sample_inputs/` and follow this
layout:

1. **Row count** (integer) on the very first line.
2. One line per sample formatted as `float, int` *(Nz, duration_ms)*.
3. Optional blank lines for readability are ignored by the loader.

## Quick start

```bash
# Print the hammerhead profile as JSON
python3 aerobatic_profiles.py hammerhead

# Load all profiles in Python
>>> from aerobatic_profiles import load_all_profiles
>>> data = load_all_profiles()
>>> data.keys()
 dict_keys(['hammerhead', 'horizontal_rolling_360', ...])
```

## Included manoeuvres

| Identifier | Source file | Short description |
|------------|-------------|-------------------|
| `hammerhead` | `hammerhead.txt` | Vertical climb to zero-airspeed, 180° yaw, vertical descent |
| `horizontal_rolling_360` | `horizontalrolling360.txt` | 360° aileron roll while level |
| `outside_360` | `outside360.txt` | 360° outside loop (sustained −G) |
| `outside_inside_vert8` | `outsideinsidevertical8.txt` | Vertical figure-of-eight: outside loop bottom, inside loop top |
| `quarter_down_roll` | `quarterdownroll.txt` | Quarter outside loop + downline snap roll |
| `snap_45deg_down_roll` | `snap45degdownroll.txt` | 45° downline with a snap roll |
| `half_vert_roll_neg_pull` | `halfverticalrollwnegpullout.txt` | ½ vertical roll ending with a −G pull-out |

Feel free to add new manoeuvres—just drop a suitably formatted text file into
the directory and update the mapping in `aerobatic_profiles.py`.

## Contact

Questions, improvements or bug reports?  Open an issue or ping the maintainer!