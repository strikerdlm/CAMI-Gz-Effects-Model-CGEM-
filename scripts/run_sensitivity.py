"""Generate the Phase-4 Sobol + Morris CSVs for paper 1.

Runs Sobol (first-, total-, second-order with bootstrap CIs) and
Morris (mu*, sigma) for each of the five surrogate targets. Output:

    data/results/sensitivity/sobol_first_total.csv
    data/results/sensitivity/sobol_second_order.csv
    data/results/sensitivity/morris.csv
    data/results/sensitivity/manifest.json

The CSVs concatenate per-target rows so a single read+pivot rebuilds
the per-target tables. ``manifest.json`` carries the run metadata
(dataset hash, seed, n_base, n_evaluations, fixed who_profile, ISO
timestamp) for paper-1 supplementary.

Usage:
    python -m scripts.run_sensitivity
    python -m scripts.run_sensitivity --n-base 1024 --who-profile custom
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

import cgem_ext  # noqa: F401  triggers sys.path injection
from cgem_ext.data.splits import stratified_split
from cgem_ext.sensitivity import MorrisAnalyzer, SobolAnalyzer
from cgem_ext.surrogate import TARGETS, build_surrogate


def _resolve_dataset(repo_root: Path) -> Path:
    path = repo_root / "data" / "datasets" / "cgem_synthetic_v1.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"{path} not found; run cgem_ext.data.generate_dataset first")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-base", type=int, default=1024,
                        help="Saltelli base sample size (Sobol). Default 1024.")
    parser.add_argument("--n-trajectories", type=int, default=200,
                        help="Morris trajectory count. Default 200.")
    parser.add_argument("--who-profile", default="custom",
                        help="Held-fixed WHO setting (1..6 or 'custom'). Default 'custom'.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", type=Path,
                        default=Path("data/results/sensitivity"),
                        help="Output directory.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    parquet_path = _resolve_dataset(repo_root)
    df = pd.read_parquet(parquet_path)
    sp = stratified_split(df, seed=args.seed)
    train_df, _val, _test = sp.apply(df)

    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    sobol_first_rows: list[dict] = []
    sobol_second_rows: list[dict] = []
    morris_rows: list[dict] = []

    who_arg: int | str = int(args.who_profile) if args.who_profile.isdigit() else args.who_profile

    start = time.time()
    for spec in TARGETS:
        print(f"==> {spec.name}", flush=True)
        surrogate = build_surrogate(spec.name).fit(train_df)

        sobol_res = SobolAnalyzer(
            surrogate,
            target=spec.name,
            n_base=args.n_base,
            seed=args.seed,
            who_profile=who_arg,
        ).run()
        for _, r in sobol_res.dataframe().iterrows():
            sobol_first_rows.append(
                {
                    "target": spec.name,
                    "censored": spec.censored,
                    "feature": r.feature,
                    "S1": float(r.S1),
                    "S1_conf": float(r.S1_conf),
                    "ST": float(r.ST),
                    "ST_conf": float(r.ST_conf),
                }
            )
        for _, r in sobol_res.second_order_dataframe().iterrows():
            sobol_second_rows.append(
                {
                    "target": spec.name,
                    "censored": spec.censored,
                    "feature_i": r.feature_i,
                    "feature_j": r.feature_j,
                    "S2": float(r.S2),
                    "S2_conf": float(r.S2_conf),
                }
            )

        morris_res = MorrisAnalyzer(
            surrogate,
            target=spec.name,
            n_trajectories=args.n_trajectories,
            seed=args.seed,
            who_profile=who_arg,
        ).run()
        for _, r in morris_res.dataframe().iterrows():
            morris_rows.append(
                {
                    "target": spec.name,
                    "censored": spec.censored,
                    "feature": r.feature,
                    "mu": float(r.mu),
                    "mu_star": float(r.mu_star),
                    "sigma": float(r.sigma),
                    "mu_star_conf": float(r.mu_star_conf),
                }
            )

    elapsed = time.time() - start

    sobol_first_df = pd.DataFrame(sobol_first_rows)
    sobol_second_df = pd.DataFrame(sobol_second_rows)
    morris_df = pd.DataFrame(morris_rows)

    sobol_first_path = out_dir / "sobol_first_total.csv"
    sobol_second_path = out_dir / "sobol_second_order.csv"
    morris_path = out_dir / "morris.csv"
    sobol_first_df.to_csv(sobol_first_path, index=False)
    sobol_second_df.to_csv(sobol_second_path, index=False)
    morris_df.to_csv(morris_path, index=False)

    # Sidecar metadata
    manifest = {
        "package_version": getattr(cgem_ext, "__version__", "unknown"),
        "dataset": parquet_path.name,
        "seed": args.seed,
        "fixed_who_profile": who_arg,
        "sobol_n_base": args.n_base,
        "sobol_n_evaluations_per_target": args.n_base * (2 * 9 + 2),
        "morris_n_trajectories": args.n_trajectories,
        "morris_n_evaluations_per_target": args.n_trajectories * (9 + 1),
        "n_targets": len(TARGETS),
        "wall_clock_s": round(elapsed, 2),
        "outputs": {
            "sobol_first_total": str(sobol_first_path.relative_to(repo_root)),
            "sobol_second_order": str(sobol_second_path.relative_to(repo_root)),
            "morris": str(morris_path.relative_to(repo_root)),
        },
        "generation_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))

    print(f"\nWrote {len(sobol_first_df)} sobol rows to {sobol_first_path}")
    print(f"Wrote {len(sobol_second_df)} second-order rows to {sobol_second_path}")
    print(f"Wrote {len(morris_df)} Morris rows to {morris_path}")
    print(f"Manifest -> {manifest_path}")
    print(f"Wall clock: {elapsed:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
