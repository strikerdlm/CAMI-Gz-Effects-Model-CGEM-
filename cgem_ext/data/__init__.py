"""Synthetic-dataset generation and train/val/test splitting.

Phase 1 deliverables:

- ``generate_dataset``  cross-product CGEM runner that materialises a
  reproducible parquet of (input features, CGEM outputs) rows.
- ``splits``            stratified and leave-one-group-out splitters keyed
  on the maneuver category metadata in ``maneuvers_catalog``.

Modules will be filled in during Phase 1 of the roadmap; this package
exists at Phase 0 so the imports needed by the CI test matrix already
resolve.
"""
