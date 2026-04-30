"""
Maneuvers Catalog
=================

Structured metadata for every aerobatic / military maneuver registered in
``aerobatic_profiles.PROFILES``. Provides categorization (championship vs.
military vs. extreme), Aresti coding, expected G envelope, onset rates,
durations, and source citations.

This module is the single source of truth for maneuver classification used by
the UI, batch runner, and hemodynamic analysis layer.

Schema
------

``ManeuverMeta`` describes one maneuver:

* ``identifier`` — must match a key in ``aerobatic_profiles.PROFILES``.
* ``category`` — one of ``ManeuverCategory`` (championship, military_acm,
  extreme_post_stall, training, conceptual).
* ``aresti_family`` — Aresti CIVA family number 1–9 (None for non-aerobatic).
* ``aresti_code`` — Aresti symbolic code if known (e.g., "7.4.1.2").
* ``aircraft`` — typical airframe context (e.g., "Extra 330", "F-16C", "Su-27").
* ``peak_pos_gz`` / ``peak_neg_gz`` — peak normal acceleration in g.
* ``onset_rate_g_per_s`` — typical G-onset rate at the principal corner.
* ``sustained_gz`` / ``sustained_duration_s`` — sustained-G plateau (None if
  the maneuver is purely transient).
* ``total_duration_s`` — approximate total maneuver duration.
* ``description`` — one-paragraph human-readable description.
* ``hemodynamic_concern`` — short note on why the maneuver stresses
  cerebral perfusion (push-pull, sustained +Gz, axis-switching, etc.).
* ``source`` — citation / DOI / URL.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ManeuverCategory(str, Enum):
    CHAMPIONSHIP = "championship"
    MILITARY_ACM = "military_acm"
    EXTREME_POST_STALL = "extreme_post_stall"
    TRAINING = "training"
    CONCEPTUAL = "conceptual"


@dataclass(frozen=True)
class ManeuverMeta:
    identifier: str
    category: ManeuverCategory
    description: str
    aircraft: str
    peak_pos_gz: float
    peak_neg_gz: float
    onset_rate_g_per_s: float
    total_duration_s: float
    aresti_family: Optional[int] = None
    aresti_code: Optional[str] = None
    sustained_gz: Optional[float] = None
    sustained_duration_s: Optional[float] = None
    hemodynamic_concern: str = ""
    source: str = ""
    tags: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Registry — populated below with every maneuver in aerobatic_profiles.PROFILES
# ---------------------------------------------------------------------------

CATALOG: Dict[str, ManeuverMeta] = {}


def register(meta: ManeuverMeta) -> None:
    """Idempotent registration; later registrations replace earlier ones."""
    CATALOG[meta.identifier] = meta


# ---------------------------------------------------------------------------
# Existing maneuvers (pre-extension baseline)
# ---------------------------------------------------------------------------

register(ManeuverMeta(
    identifier="hammerhead",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=5,
    description="Vertical climb to zero airspeed, 180° yaw (stall turn), vertical descent.",
    aircraft="Extra 330 / Sukhoi Su-26 (Unlimited)",
    peak_pos_gz=2.0,
    peak_neg_gz=-2.0,
    onset_rate_g_per_s=2.0,
    total_duration_s=22.0,
    hemodynamic_concern="Brief push-pull during pivot.",
    source="IAC catalogue family 5; existing CGEM sample input.",
))

register(ManeuverMeta(
    identifier="loop_standard",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=7,
    description="Standard inside loop with 3–5 G pull-up and pull-out.",
    aircraft="Generic aerobatic",
    peak_pos_gz=4.5,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=8.5,
    hemodynamic_concern="Sustained +G during entry pull.",
    source="IAC catalogue family 7.",
))

register(ManeuverMeta(
    identifier="immelmann_turn",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=8,
    description="Half-loop to half-roll Immelmann with high +G pull-up.",
    aircraft="Generic / fighter",
    peak_pos_gz=5.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=3.5,
    total_duration_s=8.0,
    hemodynamic_concern="High sustained +G during pull-up.",
    source="IAC catalogue family 8.",
))

register(ManeuverMeta(
    identifier="split_s",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=8,
    description="Roll inverted then descending half-loop with high +G pull-out.",
    aircraft="Generic / fighter",
    peak_pos_gz=5.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=3.5,
    total_duration_s=8.0,
    hemodynamic_concern="High +G recovery from inverted; risk at low altitude.",
    source="IAC catalogue family 8.",
))

register(ManeuverMeta(
    identifier="cuban_eight",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=8,
    description="Two looping segments joined by 45° down half-rolls.",
    aircraft="Generic aerobatic",
    peak_pos_gz=4.8,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=11.5,
    hemodynamic_concern="Repeated sustained +G with brief unloads.",
    source="IAC catalogue family 8.",
))

register(ManeuverMeta(
    identifier="vertical_eight",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=7,
    description="Vertical figure-8 with repeated +G exposures and brief −G transitions.",
    aircraft="Generic aerobatic",
    peak_pos_gz=4.6,
    peak_neg_gz=-0.4,
    onset_rate_g_per_s=3.0,
    total_duration_s=12.0,
    hemodynamic_concern="Push-pull cycle.",
    source="IAC catalogue family 7.",
))

register(ManeuverMeta(
    identifier="outside_360",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=7,
    description="360° outside loop sustaining −G throughout.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=0.5,
    peak_neg_gz=-3.5,
    onset_rate_g_per_s=2.0,
    total_duration_s=9.0,
    hemodynamic_concern="Sustained −Gz: red-out / cerebral congestion risk.",
    source="IAC catalogue; existing CGEM sample input.",
))

register(ManeuverMeta(
    identifier="outside_inside_vert8",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=7,
    description="Vertical 8 — outside loop on bottom, inside loop on top.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=4.0,
    peak_neg_gz=-3.0,
    onset_rate_g_per_s=2.5,
    total_duration_s=18.0,
    hemodynamic_concern="Strong push-pull transitions between loop halves.",
    source="IAC catalogue; existing CGEM sample input.",
))

register(ManeuverMeta(
    identifier="horizontal_rolling_360",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=9,
    description="360° aileron roll while maintaining level flight.",
    aircraft="Generic aerobatic",
    peak_pos_gz=2.0,
    peak_neg_gz=-1.5,
    onset_rate_g_per_s=2.0,
    total_duration_s=4.5,
    hemodynamic_concern="Modest oscillating G; lateral stress.",
    source="IAC catalogue family 9; existing CGEM sample input.",
))

register(ManeuverMeta(
    identifier="quarter_down_roll",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=8,
    description="Quarter outside loop followed by 90° downline snap roll.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=2.0,
    peak_neg_gz=-3.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=8.0,
    hemodynamic_concern="−G entry then snap-induced lateral G.",
    source="Existing CGEM sample input.",
))

register(ManeuverMeta(
    identifier="snap_45deg_down_roll",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=9,
    description="45° downline with a snap roll.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=4.0,
    peak_neg_gz=-1.5,
    onset_rate_g_per_s=10.0,  # snap roll spike
    total_duration_s=6.0,
    hemodynamic_concern="Snap-roll high-onset transient; lateral asymmetric loading.",
    source="Existing CGEM sample input.",
))

register(ManeuverMeta(
    identifier="half_vert_roll_neg_pull",
    category=ManeuverCategory.CHAMPIONSHIP,
    aresti_family=8,
    description="½ vertical roll ending with a negative G pull-out.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=2.0,
    peak_neg_gz=-3.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=7.0,
    hemodynamic_concern="−G pull-out: classic push-pull setup.",
    source="Existing CGEM sample input.",
))

register(ManeuverMeta(
    identifier="triple_push_pull_loop",
    category=ManeuverCategory.CONCEPTUAL,
    description="Triple push–pull loop: −G push then +G pull, repeated ×3.",
    aircraft="Conceptual demo",
    peak_pos_gz=5.0,
    peak_neg_gz=-3.0,
    onset_rate_g_per_s=4.0,
    total_duration_s=24.0,
    hemodynamic_concern="Maximal push-pull stress; baroreflex disruption.",
    source="Demo profile (CGEM repository).",
))

register(ManeuverMeta(
    identifier="triple_push_pull_immelmann",
    category=ManeuverCategory.CONCEPTUAL,
    description="Push–pull + half-roll repeated ×3.",
    aircraft="Conceptual demo",
    peak_pos_gz=6.0,
    peak_neg_gz=-3.0,
    onset_rate_g_per_s=4.0,
    total_duration_s=27.0,
    hemodynamic_concern="Repeated push-pull; severe G-LOC risk per FAA reports.",
    source="Demo profile (CGEM repository).",
))

register(ManeuverMeta(
    identifier="triple_push_pull_split_s",
    category=ManeuverCategory.CONCEPTUAL,
    description="Three consecutive push–pull Split-S entries.",
    aircraft="Conceptual demo",
    peak_pos_gz=6.0,
    peak_neg_gz=-3.0,
    onset_rate_g_per_s=4.0,
    total_duration_s=27.0,
    hemodynamic_concern="Repeated push-pull at high +G; near worst-case for unprotected pilot.",
    source="Demo profile (CGEM repository).",
))

register(ManeuverMeta(
    identifier="high_g_turn",
    category=ManeuverCategory.MILITARY_ACM,
    description="Sustained high-G level turn with 6–7 G plateau and on/off modulation.",
    aircraft="Generic fighter",
    peak_pos_gz=6.8,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=4.0,
    sustained_gz=6.5,
    sustained_duration_s=4.0,
    total_duration_s=10.0,
    hemodynamic_concern="Sustained +G plateau; baseline AGSM endurance test.",
    source="Existing CGEM sample input.",
))


# ---------------------------------------------------------------------------
# NEW: extension entries appended by research-driven additions go below.
# Generated automatically from `tools/append_catalog.py` once research
# subagents return; keep this file under version control.
# ---------------------------------------------------------------------------

register(ManeuverMeta(
    identifier="avalanche",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Inside loop with a horizontal positive snap roll at the apex; adds asymmetric high-G transient.",
    aircraft="Unlimited (Extra 330 / Su-26)",
    peak_pos_gz=6.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=9.0,
    aresti_family=7,
    hemodynamic_concern="Loop sustained +G plus brief snap-roll spike (~250 ms).",
    source="FAI/CIVA Aresti family 7 + 9 (snap subfamily); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="tailslide_positive",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Vertical climb to zero airspeed, brief rearward slide, canopy-back nose-over with positive-G recovery.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=3.5,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=5.0,
    total_duration_s=10.0,
    aresti_family=6,
    hemodynamic_concern="Long zero-G phase before positive recovery pull (mild push-pull).",
    source="FAI/CIVA Aresti family 6; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="tailslide_negative",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Vertical climb, rearward slide, canopy-forward nose-over with negative-G recovery.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=1.0,
    peak_neg_gz=-2.5,
    onset_rate_g_per_s=5.0,
    total_duration_s=10.0,
    aresti_family=6,
    hemodynamic_concern="Sustained negative-G recovery; cephalad blood pooling.",
    source="FAI/CIVA Aresti family 6; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="humpty_bump_positive",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Quarter-loop up, vertical line, half-loop forward (positive over the top), vertical line down, quarter-loop pull.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=5.5,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=4.0,
    total_duration_s=14.0,
    aresti_family=8,
    hemodynamic_concern="Two large +G corners bracketing brief negative apex.",
    source="FAI/CIVA Aresti family 8; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="humpty_bump_negative",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Quarter-loop up, pushed (outside) half-loop over the top loading the pilot negatively, vertical down.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=5.5,
    peak_neg_gz=-4.0,
    onset_rate_g_per_s=3.5,
    total_duration_s=14.0,
    aresti_family=8,
    hemodynamic_concern="Sustained -3 to -4 G across pushed half-loop; severe push-pull risk.",
    source="FAI/CIVA Aresti family 8; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="square_loop",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Four 90° corner pulls (~5–6 G) linked by 1-G straight lines.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=6.0,
    peak_neg_gz=-0.2,
    onset_rate_g_per_s=5.5,
    total_duration_s=15.0,
    aresti_family=7,
    hemodynamic_concern="Four high-onset +6 G corners in sequence; AGSM endurance test.",
    source="FAI/CIVA Aresti family 7 (square loop); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="reverse_cuban_eight",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Mirror of standard Cuban eight: 5/8-loop entry then 45° upline half-rolls and pulls.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=5.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=3.5,
    total_duration_s=18.0,
    aresti_family=7,
    hemodynamic_concern="Two large +G pulls separated by brief negative half-roll segments.",
    source="FAI/CIVA Aresti family 7 (eights); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="snap_roll_level",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Autorotative aileron-rudder snap on level line; brief asymmetric high-G spike.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=6.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=18.0,
    total_duration_s=5.0,
    aresti_family=9,
    hemodynamic_concern="Sub-300 ms +6 G spike; onset rate exceeds AGSM time constant.",
    source="FAI/CIVA Aresti family 9 (snap subfamily); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="vertical_snap_upline",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Quarter-loop pull to vertical, snap roll executed during the climb at decaying airspeed.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=6.0,
    peak_neg_gz=-1.5,
    onset_rate_g_per_s=18.0,
    total_duration_s=9.0,
    aresti_family=9,
    hemodynamic_concern="Snap-G spike on top of 1-G vertical baseline.",
    source="FAI/CIVA Aresti family 9 (snap on family-1 line); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="outside_snap_level",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Snap roll initiated by forward stick (negative AOA stall); brief negative-G spike.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=1.5,
    peak_neg_gz=-4.5,
    onset_rate_g_per_s=18.0,
    total_duration_s=5.0,
    aresti_family=9,
    hemodynamic_concern="Sub-300 ms -4.5 G spike; rare physiologic challenge.",
    source="FAI/CIVA Aresti family 9 (outside snap); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="hesitation_roll_4pt",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Aileron roll executed in four 90° increments with brief stops.",
    aircraft="Aerobatic competition",
    peak_pos_gz=1.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=2.5,
    total_duration_s=6.0,
    aresti_family=9,
    hemodynamic_concern="Mild oscillating G; knife-edge unloads to ~0 G.",
    source="FAI/CIVA Aresti family 9; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="hesitation_roll_8pt",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Eight-stop slow roll (45° increments).",
    aircraft="Aerobatic competition",
    peak_pos_gz=1.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=2.0,
    total_duration_s=8.0,
    aresti_family=9,
    hemodynamic_concern="Finer-granularity oscillation; mild stress.",
    source="FAI/CIVA Aresti family 9; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="slow_roll_level",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Continuous full-360° aileron roll on level line; smooth Nz transition through ±1 G.",
    aircraft="Aerobatic competition",
    peak_pos_gz=1.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=1.5,
    total_duration_s=5.0,
    aresti_family=9,
    hemodynamic_concern="Smooth ±1 G sinusoid; mild physiologic load.",
    source="FAI/CIVA Aresti family 9; idealised slow-roll Nz profile.",
))

register(ManeuverMeta(
    identifier="inverted_spin",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Sustained autorotation at negative AOA; -1.5 to -2.5 G sustained, +G recovery pull.",
    aircraft="Aerobatic / military trainer",
    peak_pos_gz=3.0,
    peak_neg_gz=-2.5,
    onset_rate_g_per_s=4.0,
    total_duration_s=14.0,
    aresti_family=9,
    hemodynamic_concern="Sustained -G with Coriolis stress; recovery pull on deconditioned baroreflex.",
    source="FAI/CIVA Aresti family 9 (inverted spin subcode); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="flat_spin_positive",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="High-AOA flat-attitude spin; modest +Gz dominated by centripetal yaw rate.",
    aircraft="Aerobatic / fighter",
    peak_pos_gz=2.5,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=3.0,
    total_duration_s=14.0,
    aresti_family=9,
    hemodynamic_concern="Dominant rotational/Gy stress (not modeled); +Gz modest.",
    source="FAI/CIVA Aresti family 9 (flat spin subcode); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="inverted_flat_spin",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Flat spin in inverted attitude; sustained -1.5 to -2.5 G.",
    aircraft="Aerobatic / fighter",
    peak_pos_gz=2.0,
    peak_neg_gz=-2.5,
    onset_rate_g_per_s=4.0,
    total_duration_s=14.0,
    aresti_family=9,
    hemodynamic_concern="Most stressful Unlimited spin; sustained -G + rotational stress.",
    source="FAI/CIVA Aresti family 9; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="english_bunt",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Full outside loop pushed from level upright; sustained negative G throughout.",
    aircraft="Unlimited aerobatic",
    peak_pos_gz=0.5,
    peak_neg_gz=-4.5,
    onset_rate_g_per_s=3.0,
    total_duration_s=16.0,
    aresti_family=7,
    hemodynamic_concern="Sustained -3 to -4.5 G for 12+ seconds; cerebral congestion / red-out risk.",
    source="FAI/CIVA Aresti family 7 (outside loop variant); kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="torque_roll",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Vertical zero-airspeed rotation under engine torque; ~0 G hang then recovery.",
    aircraft="Showpiece (Sean Tucker / Mike Goulian)",
    peak_pos_gz=2.5,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=3.0,
    total_duration_s=10.0,
    aresti_family=1,
    hemodynamic_concern="Long zero-G float; mild push-pull on recovery.",
    source="Airshow figure; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="knife_edge_pass_highg",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="High-G level turn into 90° bank knife-edge with rudder; sustained +G then sudden offload.",
    aircraft="Showpiece",
    peak_pos_gz=6.0,
    peak_neg_gz=-0.3,
    onset_rate_g_per_s=5.0,
    total_duration_s=10.0,
    aresti_family=1,
    hemodynamic_concern="Sudden +6 → 0 G offload (~10 G/s); abrupt baroreflex demand.",
    source="Airshow figure; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="double_immelmann",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Two consecutive Immelmann turns flown back-to-back without level segment between.",
    aircraft="Generic / fighter",
    peak_pos_gz=5.0,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=3.5,
    total_duration_s=16.0,
    aresti_family=8,
    hemodynamic_concern="Two sustained +5 G pulls within 16 s; AGSM endurance.",
    source="FAI/CIVA Aresti family 8; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="quarter_clover",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Looping segment combined with 90° heading change; classical clover-leaf training figure.",
    aircraft="Generic / fighter",
    peak_pos_gz=5.0,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=3.5,
    total_duration_s=12.0,
    aresti_family=7,
    hemodynamic_concern="Single sustained +5 G pull with mild post-roll segment.",
    source="FAA-H-8083-9 Aerobatic Flying Handbook; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="reverse_half_cuban",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Half-Cuban entered from the top: pull up to 45° upline, half-roll to inverted, then 5/8 loop.",
    aircraft="Aerobatic competition",
    peak_pos_gz=5.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=10.0,
    aresti_family=7,
    hemodynamic_concern="Single +5 G pull preceded by brief inverted segment.",
    source="FAI/CIVA Aresti family 7; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="lazy_eight",
    category=ManeuverCategory.CHAMPIONSHIP,
    description="Gentle commercial-pilot/training maneuver: undulating coordinated turns in horizontal figure-eight.",
    aircraft="Trainer / GA",
    peak_pos_gz=2.5,
    peak_neg_gz=0.5,
    onset_rate_g_per_s=0.5,
    total_duration_s=24.0,
    aresti_family=7,
    hemodynamic_concern="Mild; no negative phase. Reference low-stress profile.",
    source="FAA-H-8083-3 Airplane Flying Handbook; kinematic synthesis.",
))

register(ManeuverMeta(
    identifier="defensive_break_9g",
    category=ManeuverCategory.MILITARY_ACM,
    description="Maximum-performance 9-G defensive break turn to spoil a bandit's tracking solution.",
    aircraft="F-16C",
    peak_pos_gz=9.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=7.0,
    total_duration_s=17.0,
    sustained_gz=9.0,
    sustained_duration_s=4.0,
    hemodynamic_concern="Maximum sustained +Gz with fast onset; AGSM critical.",
    source="Shaw, Fighter Combat Ch.4; Newman & Callister 2009 DOI:10.3357/asem.2361.2009.",
))

register(ManeuverMeta(
    identifier="sustained_9g_turn",
    category=ManeuverCategory.MILITARY_ACM,
    description="9-G structural-limit turn held for 25–30 s (qualification SACM standard).",
    aircraft="F-16C / F-22A",
    peak_pos_gz=9.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=6.0,
    total_duration_s=38.0,
    sustained_gz=9.0,
    sustained_duration_s=25.0,
    hemodynamic_concern="G-tolerance endurance test; cumulative AGSM fatigue.",
    source="USAF AFMAN 11-2F-16; NATO HFM-251 lineage SACM 9G/30s standard.",
))

register(ManeuverMeta(
    identifier="corner_velocity_turn",
    category=ManeuverCategory.MILITARY_ACM,
    description="Brief instantaneous-rate turn at corner velocity (max G/min radius) with rapid energy bleed.",
    aircraft="F-16C @ ~430 KCAS SL",
    peak_pos_gz=9.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=9.0,
    total_duration_s=12.0,
    sustained_gz=9.0,
    sustained_duration_s=3.0,
    hemodynamic_concern="Aggressive 9 G/s onset; high G-LOC risk if AGSM late.",
    source="Shaw Ch.3; F-16 corner-velocity charts.",
))

register(ManeuverMeta(
    identifier="high_yoyo_offensive",
    category=ManeuverCategory.MILITARY_ACM,
    description="Offensive 3-D maneuver: climb out of plane, trade airspeed, dive back into bandit's plane.",
    aircraft="F-15C / F-16C",
    peak_pos_gz=6.0,
    peak_neg_gz=0.5,
    onset_rate_g_per_s=5.0,
    total_duration_s=13.0,
    sustained_gz=5.5,
    sustained_duration_s=2.0,
    hemodynamic_concern="Dual +5–6 G pulls separated by brief unload.",
    source="Shaw Ch.4 (offensive BFM); USAF AFMAN 11-2F-16.",
))

register(ManeuverMeta(
    identifier="low_yoyo_offensive",
    category=ManeuverCategory.MILITARY_ACM,
    description="Offensive maneuver: roll-and-dive below bandit's plane to gain closure, then hard pull-up.",
    aircraft="F-16C / F/A-18",
    peak_pos_gz=7.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=6.0,
    total_duration_s=13.0,
    sustained_gz=7.0,
    sustained_duration_s=2.5,
    hemodynamic_concern="Hard +7 G pull-up after low-G dive; mild push-pull.",
    source="Shaw Ch.4; Newman & Callister 2009.",
))

register(ManeuverMeta(
    identifier="barrel_roll_attack",
    category=ManeuverCategory.MILITARY_ACM,
    description="Rolling, vertically-displaced helical maneuver to control closure on a slower bandit.",
    aircraft="F-15C / Su-27",
    peak_pos_gz=5.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=14.0,
    sustained_gz=4.5,
    sustained_duration_s=6.0,
    hemodynamic_concern="Sustained +4–5 G with continuous body-axis rotation (Gy stress).",
    source="Shaw Ch.4 (rolling maneuvers).",
))

register(ManeuverMeta(
    identifier="lag_pursuit_roll",
    category=ManeuverCategory.MILITARY_ACM,
    description="Rolling-displacement maneuver to convert excess closure into angles.",
    aircraft="F-16C",
    peak_pos_gz=4.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=3.0,
    total_duration_s=13.0,
    sustained_gz=3.5,
    sustained_duration_s=6.0,
    hemodynamic_concern="Sustained +3–4 G with rolling component.",
    source="Shaw Ch.4 (pursuit curves); USAF AFMAN 11-2F-16.",
))

register(ManeuverMeta(
    identifier="flat_scissors_defensive",
    category=ManeuverCategory.MILITARY_ACM,
    description="Defensive horizontal-plane rolling reversals to force bandit overshoot.",
    aircraft="F/A-18",
    peak_pos_gz=4.5,
    peak_neg_gz=0.5,
    onset_rate_g_per_s=4.0,
    total_duration_s=16.0,
    sustained_gz=4.0,
    sustained_duration_s=1.5,
    hemodynamic_concern="Multiple +4–4.5 G reversal pulses; AGSM cycle stress.",
    source="Shaw Ch.4; Newman & Callister 2009 (F/A-18 reversal G profiles).",
))

register(ManeuverMeta(
    identifier="rolling_scissors",
    category=ManeuverCategory.MILITARY_ACM,
    description="Vertical scissors with rolling component; sustained 3–5 G alternating.",
    aircraft="F-16C / F/A-18",
    peak_pos_gz=5.0,
    peak_neg_gz=0.5,
    onset_rate_g_per_s=3.0,
    total_duration_s=18.0,
    sustained_gz=4.5,
    sustained_duration_s=5.0,
    hemodynamic_concern="Sustained +4–5 G with rolling/vertical component over 18 s.",
    source="Shaw Ch.4; Newman & Callister 2009.",
))

register(ManeuverMeta(
    identifier="defensive_jink",
    category=ManeuverCategory.MILITARY_ACM,
    description="Rapid out-of-plane G excursions to defeat tracking-gun / IR-missile lock-on.",
    aircraft="A-10 / F-16C",
    peak_pos_gz=6.5,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=10.0,
    total_duration_s=10.0,
    hemodynamic_concern="High-onset (~10 G/s) pulses with brief unloads; mild push-pull.",
    source="Shaw Ch.5 (gun defense); A-10 BFM doctrine.",
))

register(ManeuverMeta(
    identifier="last_ditch_break",
    category=ManeuverCategory.MILITARY_ACM,
    description="Final maximum-G out-of-plane break ~1.5–3 s before missile impact, often combined with chaff/flare.",
    aircraft="F-16C / F/A-18",
    peak_pos_gz=9.5,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=13.0,
    total_duration_s=6.0,
    hemodynamic_concern="Onset >12 G/s exceeds standard envelope; pilot accepts grey-out risk.",
    source="Shaw Ch.5; NATO HFM-251 rapid-onset tolerance discussions.",
))

register(ManeuverMeta(
    identifier="combat_immelmann",
    category=ManeuverCategory.MILITARY_ACM,
    description="Combat-power half-loop with half-roll on top; 6–7 G entry pull.",
    aircraft="F-16C / F-15C",
    peak_pos_gz=7.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=6.0,
    total_duration_s=14.0,
    sustained_gz=6.5,
    sustained_duration_s=2.5,
    hemodynamic_concern="Higher peak than aerobatic Immelmann (5G); 6 G/s onset.",
    source="Shaw Ch.4; USAF AFMAN BFM.",
))

register(ManeuverMeta(
    identifier="combat_split_s",
    category=ManeuverCategory.MILITARY_ACM,
    description="Inverted half-loop reversal at low altitude with 7–8 G pull-out.",
    aircraft="F-16C / F/A-18",
    peak_pos_gz=8.0,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=7.0,
    total_duration_s=14.0,
    sustained_gz=7.5,
    sustained_duration_s=2.5,
    hemodynamic_concern="High +G recovery from inverted at low altitude; minimal margin.",
    source="Shaw Ch.4; Newman & Callister 2009.",
))

register(ManeuverMeta(
    identifier="defensive_break_chaff_flare",
    category=ManeuverCategory.MILITARY_ACM,
    description="Max-G break with brief unload at decoy release to favor seduction, then re-pull.",
    aircraft="F-16C / F-15E / Eurofighter",
    peak_pos_gz=9.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=8.0,
    total_duration_s=14.0,
    sustained_gz=8.5,
    sustained_duration_s=2.5,
    hemodynamic_concern="Two high-G pulses with abrupt unload; AGSM cycle disruption.",
    source="Shaw Ch.5; Bürkle et al. (Eurofighter G-LOC, by topic).",
))

register(ManeuverMeta(
    identifier="strike_turn_strafing_pullout",
    category=ManeuverCategory.MILITARY_ACM,
    description="Ground-attack profile: shallow dive at -1 G push, strafing pass, 7 G pull-out.",
    aircraft="A-10C / F-16C strike",
    peak_pos_gz=7.0,
    peak_neg_gz=-1.0,
    onset_rate_g_per_s=7.0,
    total_duration_s=16.0,
    sustained_gz=6.5,
    sustained_duration_s=3.0,
    hemodynamic_concern="Push-pull: -1 G dive bunt for 2 s then +7 G pull-out.",
    source="USAF A-10 BFM/CAS doctrine; Shaw Ch.6.",
))

register(ManeuverMeta(
    identifier="push_pull_missile_evasion",
    category=ManeuverCategory.MILITARY_ACM,
    description="Negative-G push to displace velocity vector, immediately followed by max +G inside pull.",
    aircraft="F-16C / F/A-18",
    peak_pos_gz=7.0,
    peak_neg_gz=-1.5,
    onset_rate_g_per_s=6.0,
    total_duration_s=13.0,
    sustained_gz=6.5,
    sustained_duration_s=3.5,
    hemodynamic_concern="Classical push-pull: 2.5 s -1.5 G push then 7 G pull. Tolerance ↓1–2 G.",
    source="Banks et al. push-pull effect literature; Shaw Ch.5.",
))

register(ManeuverMeta(
    identifier="defensive_spiral",
    category=ManeuverCategory.MILITARY_ACM,
    description="Descending high-G spiral (corkscrew) to bleed bandit's energy.",
    aircraft="F-16C / Su-27",
    peak_pos_gz=7.5,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=6.0,
    total_duration_s=22.0,
    sustained_gz=7.0,
    sustained_duration_s=12.0,
    hemodynamic_concern="Sustained +6.5–7.5 G across multiple spiral turns.",
    source="Shaw Ch.4 (vertical maneuvers); Zhang et al. Su-27 +Gz exposure.",
))

register(ManeuverMeta(
    identifier="rate_fight_sustained",
    category=ManeuverCategory.MILITARY_ACM,
    description="Two-circle sustained turning engagement at corner velocity; 7–8 G plateau for 22 s.",
    aircraft="F-16C / Eurofighter",
    peak_pos_gz=8.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=6.0,
    total_duration_s=30.0,
    sustained_gz=7.5,
    sustained_duration_s=18.0,
    hemodynamic_concern="G-tolerance endurance test; major AGSM fatigue scenario.",
    source="Shaw Ch.4 (one-circle vs two-circle); Sauvet et al. F-16 ACM HRV.",
))

register(ManeuverMeta(
    identifier="vertical_climb_missile_evasion",
    category=ManeuverCategory.MILITARY_ACM,
    description="Zoom climb to drag missile into thin air; high-G pull-up then near-1 G climb.",
    aircraft="F-15C / F-22A",
    peak_pos_gz=7.0,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=6.0,
    total_duration_s=22.0,
    sustained_gz=6.5,
    sustained_duration_s=2.5,
    hemodynamic_concern="Initial high-G pull then prolonged low-G climb; mild post-G-pull recovery.",
    source="Shaw Ch.4; USAF AFMAN 11-2F-15.",
))

register(ManeuverMeta(
    identifier="helicopter_bugout",
    category=ManeuverCategory.MILITARY_ACM,
    description="Low-energy disengagement: nose-high, decelerate, pivot and pitch over into dive.",
    aircraft="F/A-18 / F-16C",
    peak_pos_gz=4.5,
    peak_neg_gz=-0.7,
    onset_rate_g_per_s=3.0,
    total_duration_s=17.0,
    sustained_gz=4.0,
    sustained_duration_s=2.5,
    hemodynamic_concern="Low-energy push-pull: -0.7 G pitchover then +4.5 G recovery.",
    source="Shaw Ch.4 (low-speed maneuvers); Newman & Callister 2009.",
))

register(ManeuverMeta(
    identifier="slatted_high_aoa_turn",
    category=ManeuverCategory.MILITARY_ACM,
    description="Sustained 7-G turn at high AOA with leading-edge slats deployed.",
    aircraft="F/A-18C/D",
    peak_pos_gz=7.5,
    peak_neg_gz=0.0,
    onset_rate_g_per_s=5.0,
    total_duration_s=22.0,
    sustained_gz=7.2,
    sustained_duration_s=10.0,
    hemodynamic_concern="Long sustained 7 G plateau at high AOA.",
    source="Newman & Callister 2009 DOI:10.3357/asem.2361.2009.",
))

register(ManeuverMeta(
    identifier="pugachev_cobra",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Dynamic post-stall pitch-up to ~110–120° AOA, decelerate, pitch forward and recover.",
    aircraft="Su-27 / Su-35",
    peak_pos_gz=6.5,
    peak_neg_gz=-0.4,
    onset_rate_g_per_s=30.0,
    total_duration_s=5.0,
    hemodynamic_concern="Pitch-up Gz spike (~150 ms) too short for AGSM; brief float.",
    source="Herbst W.B. (1980) Dynamics of Air Combat, J. Aircraft 17(8); kinematic estimate.",
))

register(ManeuverMeta(
    identifier="kulbit",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Cobra continued through full 360° backflip about pitch axis at low translational velocity.",
    aircraft="Su-37 / Su-30MKI / Su-35",
    peak_pos_gz=8.0,
    peak_neg_gz=-1.8,
    onset_rate_g_per_s=35.0,
    total_duration_s=7.0,
    hemodynamic_concern="Textbook push-pull: +6–8 G then sustained -1.8 G then +6–7 G recovery.",
    source="Sukhoi flight-demo materials; cross-reference Banks et al. push-pull literature.",
))

register(ManeuverMeta(
    identifier="lomcovak",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Czech autorotative tumbling maneuver; gyroscopically coupled rotation about all three body axes.",
    aircraft="Zlín Z-50 / Extra 300 / Su-26",
    peak_pos_gz=6.5,
    peak_neg_gz=-5.5,
    onset_rate_g_per_s=45.0,
    total_duration_s=6.0,
    hemodynamic_concern="Highest per-unit-time CV demand; alternating ±5+ G defeats AGSM.",
    source="FAI/CIVA Aresti family 9 tumble; Walter Extra airframe ±10G; kinematic estimate.",
))

register(ManeuverMeta(
    identifier="herbst_jturn",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Post-stall yaw-reversal: pitch-up to ~70° AOA, 180° body-axis yaw, pitch-down recovery.",
    aircraft="X-31 / F-22A / F-18 HARV",
    peak_pos_gz=3.8,
    peak_neg_gz=-0.5,
    onset_rate_g_per_s=12.0,
    total_duration_s=12.0,
    hemodynamic_concern="Body-axis Nz modest; lateral Gy + longitudinal Gx unmodeled by CGEM.",
    source="NASA Dryden / Langley X-31 EFM publications (Smith, Foster).",
))

register(ManeuverMeta(
    identifier="helicopter_maneuver",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Near-vertical attitude at low airspeed (Russian 'Bell'); rearward drift, nose-over, recovery.",
    aircraft="Su-27 / Su-35 / MiG-29 OVT",
    peak_pos_gz=3.5,
    peak_neg_gz=-1.2,
    onset_rate_g_per_s=15.0,
    total_duration_s=12.0,
    hemodynamic_concern="Long zero-G phase causes cephalad shift; -G nose-over then mild +G pull.",
    source="Sukhoi public demo literature; F-18 HARV high-alpha analog.",
))

register(ManeuverMeta(
    identifier="falling_leaf",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Sustained high-AOA flight with alternating yaw/pitch oscillations resembling a falling leaf.",
    aircraft="F-18 HARV / X-31 / Su-35",
    peak_pos_gz=2.5,
    peak_neg_gz=-1.2,
    onset_rate_g_per_s=8.0,
    total_duration_s=16.0,
    hemodynamic_concern="10+ s vestibular-baroreflex coupling; mild but cumulative.",
    source="NASA Langley wing-rock and falling-leaf literature (Foster).",
))

register(ManeuverMeta(
    identifier="tailslide_tumble",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Tailslide entering autorotative tumble during recovery; compound sustained-G then alternating ±G.",
    aircraft="Unlimited (Extra 300 / Su-26 / Edge 540)",
    peak_pos_gz=6.0,
    peak_neg_gz=-5.0,
    onset_rate_g_per_s=50.0,
    total_duration_s=9.0,
    hemodynamic_concern="Longest combined push-pull pattern in catalog; highest aggregate risk.",
    source="Pilot incident reports (CIVA / IAC); kinematic estimate.",
))

register(ManeuverMeta(
    identifier="inverted_cobra",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Theoretical negative-G mirror of Pugachev's Cobra; sustained -Gz spike and recovery from inverted.",
    aircraft="Theoretical / Extra 300L kinematic equivalent",
    peak_pos_gz=1.0,
    peak_neg_gz=-5.5,
    onset_rate_g_per_s=30.0,
    total_duration_s=5.0,
    hemodynamic_concern="Peak -5 G ~ 1 s; conjunctival hemorrhage / red-out risk; airframe-limited.",
    source="Burton USAFSAM -Gz literature; theoretical envelope extension.",
))

register(ManeuverMeta(
    identifier="lomcovak_repeats",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Two to three Lomcováks back-to-back; cumulative axis-switching ±G.",
    aircraft="Extra 330SC / Su-26 / Edge 540 / MX-2",
    peak_pos_gz=6.5,
    peak_neg_gz=-5.5,
    onset_rate_g_per_s=50.0,
    total_duration_s=14.0,
    hemodynamic_concern="Cumulative baroreflex exhaustion; CGEM lacks fatigue term — likely under-predicts.",
    source="Competition aerobatic flight literature; kinematic estimate.",
))

register(ManeuverMeta(
    identifier="inverted_spin_recovery",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Developed inverted spin → 2–3 s -G recovery dive → hard symmetric +G pull.",
    aircraft="T-6 / Pitts / Extra 300 / Su-26",
    peak_pos_gz=6.0,
    peak_neg_gz=-2.5,
    onset_rate_g_per_s=25.0,
    total_duration_s=16.0,
    hemodynamic_concern="Most clinically realistic push-pull; sustained -G unloads carotid baroreflex before +6 G pull.",
    source="NASA SP-2009-575 (Chambers); Bihrle Applied Research; Banks push-pull literature.",
))

register(ManeuverMeta(
    identifier="bell_tailslide",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Vertical climb, full backslide, negative-G nose-over at apex, forward dive recovery.",
    aircraft="Sukhoi Su-26/29 / Extra 300 / MX-2",
    peak_pos_gz=3.5,
    peak_neg_gz=-2.0,
    onset_rate_g_per_s=15.0,
    total_duration_s=14.0,
    hemodynamic_concern="Sustained low-G then -2 G nose-over; classical push-pull setup.",
    source="Russian aerobatic literature ('Bell' / Колокол); CIVA Aresti.",
))

register(ManeuverMeta(
    identifier="snake_modulated",
    category=ManeuverCategory.EXTREME_POST_STALL,
    description="Falling leaf with intentional pitch-rate forcing producing phased ±G modulation.",
    aircraft="F-18 HARV / X-31",
    peak_pos_gz=3.8,
    peak_neg_gz=-2.0,
    onset_rate_g_per_s=20.0,
    total_duration_s=14.0,
    hemodynamic_concern="~2–3 s push-pull period close to baroreflex resonance frequency.",
    source="NASA F-18 HARV and X-31 high-AOA flight-test pilot reports.",
))



# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get(identifier: str) -> ManeuverMeta:
    return CATALOG[identifier]


def by_category(category: ManeuverCategory) -> List[ManeuverMeta]:
    return [m for m in CATALOG.values() if m.category == category]


def all_identifiers() -> List[str]:
    return list(CATALOG.keys())


if __name__ == "__main__":
    import json
    print(json.dumps({k: v.__dict__ | {"category": v.category.value}
                       for k, v in CATALOG.items()}, indent=2, default=str))
