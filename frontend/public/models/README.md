# Extra 300 visual asset

`Extra-300-r03.glb` is an unchanged copy of revision 03 from
[strikerdlm/3d-physiology-webxr](https://github.com/strikerdlm/3d-physiology-webxr/blob/d8f8255f782fd85fe6761e8e6dfd1adc9384bbb0/extra-300l-cad/exports/Extra-300L.glb),
verified against the latest `main` tree on 2026-09-25.

- Source commit: `d8f8255f782fd85fe6761e8e6dfd1adc9384bbb0`
- Source Git blob: `2615715b84f9c519ab657e689049b6b7094c65f6`
- SHA-256: `bc2f6a088931817945d43ceb69eb56058156ca034c2dc62fa72b5f9f3941284d`
- Size: 4,925,744 bytes; 22 parts; 225,116 triangles; 11 materials; embedded paint images.
- Supplied configuration: single cockpit, two-blade propeller, red/white/navy livery.
- Authored bounds: 8.000 m span, 6.613816 m length, 2.530884 m height.

The source is Y-up with its nose toward -X. CGEM applies the proper rotation
`(x, y, z) -> (-x, -z, -y)` and translation `(2.7, 0, 1.3)` to obtain
forward/right/down body coordinates. This illustrative presentation origin is
not a measured centre of gravity. Geometry, UVs, textures, scale and materials
are retained. The propeller's four parts rotate together around the imported
hub centre. Ailerons, elevator and rudder remain part of the fixed wing/tail
meshes. The cockpit camera and live instrument panel are illustrative additions.

CGEM's flight model continues to use its documented Extra 300L parameters.
The supplied visual asset's dimensions and configuration are recorded separately
from aerodynamic and physiological assumptions.

## Source provenance

The source's [revision-03 record](https://github.com/strikerdlm/3d-physiology-webxr/blob/d8f8255f782fd85fe6761e8e6dfd1adc9384bbb0/extra-300l-cad/evidence/revision-03/README.md)
identifies the supplied snapshot-5 CAD, original livery, tessellation and validation.
It records that source redistribution rights remain unverified. This provenance
note is retained; the imported CAD asset is not relabeled as CGEM-authored or
covered by CGEM's software license.
