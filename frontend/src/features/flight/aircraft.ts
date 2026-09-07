import * as THREE from "three";
import type { FlightFrame } from "./types";

/** Photo-fitted Extra 300L, metres, CG-relative body axes: forward/right/down.
 * The surfaces are geometry, including the paint boundaries; no photo billboards.
 */
export function createAircraft() {
  const root = new THREE.Group();
  root.name = "Extra 300L";
  const paint = (color: number) =>
    new THREE.MeshPhysicalMaterial({
      color,
      roughness: 0.27,
      metalness: 0.08,
      clearcoat: 0.8,
      clearcoatRoughness: 0.2,
      side: THREE.DoubleSide,
    });
  const white = paint(0xf3f5f8),
    navy = paint(0x091b4f),
    red = paint(0xd70921);
  const black = new THREE.MeshStandardMaterial({
    color: 0x11171d,
    roughness: 0.75,
    side: THREE.DoubleSide,
  });
  const metal = new THREE.MeshStandardMaterial({
    color: 0x83909a,
    metalness: 0.85,
    roughness: 0.3,
  });
  const glass = new THREE.MeshPhysicalMaterial({
    color: 0xa1d1e1,
    transparent: true,
    opacity: 0.27,
    roughness: 0.08,
    metalness: 0.1,
    clearcoat: 1,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  const colors = [white, navy, red];
  const add = (
    g: THREE.BufferGeometry,
    m: THREE.Material | THREE.Material[],
    name = "",
    parent: THREE.Object3D = root,
  ) => {
    const mesh = new THREE.Mesh(g, m);
    mesh.name = name;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  };
  const ellipsoid = (
    name: string,
    pos: number[],
    scale: number[],
    mat: THREE.Material,
    parent: THREE.Object3D = root,
  ) => {
    const m = add(new THREE.SphereGeometry(1, 32, 20), mat, name, parent);
    m.position.fromArray(pos);
    m.scale.fromArray(scale);
    return m;
  };
  const tube = (
    points: THREE.Vector3[],
    radius: number,
    mat: THREE.Material,
    name = "",
    parent: THREE.Object3D = root,
  ) =>
    add(
      new THREE.TubeGeometry(
        new THREE.CatmullRomCurve3(points),
        Math.max(8, points.length * 3),
        radius,
        8,
        false,
      ),
      mat,
      name,
      parent,
    );
  const grouped = (
    g: THREE.BufferGeometry,
    indices: number[],
    groups: number[],
  ) => {
    const sorted: number[] = [];
    for (let material = 0; material < 3; material++) {
      const start = sorted.length;
      for (let i = 0; i < groups.length; i++)
        if (groups[i] === material)
          sorted.push(...indices.slice(i * 6, i * 6 + 6));
      g.addGroup(start, sorted.length - start, material);
    }
    g.setIndex(sorted);
    g.computeVertexNormals();
  };
  // Section values are x, half width, upper radius, lower radius, centre z.
  const sections = [
    [-3.78, 0.015, 0.02, 0.035, 0.29],
    [-3.48, 0.105, 0.16, 0.13, 0.22],
    [-2.85, 0.18, 0.24, 0.18, 0.16],
    [-2, 0.29, 0.34, 0.25, 0.11],
    [-1.2, 0.405, 0.39, 0.36, 0.055],
    [-0.35, 0.445, 0.42, 0.43, 0],
    [0.7, 0.445, 0.4, 0.44, -0.02],
    [1.7, 0.425, 0.37, 0.43, -0.03],
    [2.25, 0.37, 0.32, 0.34, -0.025],
    [2.61, 0.29, 0.25, 0.27, 0],
  ];
  const section = (x: number) => {
    let i = 0;
    while (i < sections.length - 2 && x > sections[i + 1][0]) i++;
    const a = sections[i],
      b = sections[i + 1],
      u = (x - a[0]) / (b[0] - a[0]);
    const smooth = u * u * (3 - 2 * u);
    return a.map((v, k) =>
      k === 0 ? x : THREE.MathUtils.lerp(v, b[k], smooth),
    );
  };
  const verts: number[] = [],
    idx: number[] = [],
    mats: number[] = [];
  const nx = 110,
    na = 96;
  for (let i = 0; i <= nx; i++) {
    const x = THREE.MathUtils.lerp(-3.78, 2.61, i / nx),
      s = section(x);
    for (let j = 0; j <= na; j++) {
      const t = (j / na) * Math.PI * 2,
        c = Math.cos(t);
      verts.push(x, s[1] * Math.sin(t), s[4] - (c >= 0 ? s[2] : s[3]) * c);
    }
  }
  for (let i = 0; i < nx; i++)
    for (let j = 0; j < na; j++) {
      const x = THREE.MathUtils.lerp(-3.78, 2.61, (i + 0.5) / nx),
        t = ((j + 0.5) / na) * Math.PI * 2,
        c = Math.cos(t);
      // Open cockpit under the separate glass shell, with a real empty interior.
      if (x > -1.18 && x < 0.93 && c > 0.47) continue;
      const k = i * (na + 1) + j;
      idx.push(k, k + na + 2, k + 1, k, k + na + 1, k + na + 2);
      mats.push(c > 0.39 ? 0 : c > 0.06 ? 1 : c > 0 ? 0 : 2);
    }
  const fuselage = new THREE.BufferGeometry();
  fuselage.setAttribute("position", new THREE.Float32BufferAttribute(verts, 3));
  grouped(fuselage, idx, mats);
  add(fuselage, colors, "fuselage");
  // A symmetrical aerodynamic section instead of rectangular wing slabs.
  function wing(
    name: string,
    side: number,
    span0: number,
    span1: number,
    leading: (y: number) => number,
    trailing: (y: number) => number,
    c0: number,
    c1: number,
    z: number,
    parent = root,
    hingeX = 0,
  ) {
    const p: number[] = [],
      indices: number[] = [],
      groups: number[] = [];
    const ns = 30,
      nc = 24;
    for (let face = 0; face < 2; face++)
      for (let s = 0; s <= ns; s++) {
        const y = THREE.MathUtils.lerp(span0, span1, s / ns),
          le = leading(y),
          te = trailing(y),
          chord = le - te;
        for (let k = 0; k <= nc; k++) {
          const c = THREE.MathUtils.lerp(c0, c1, k / nc);
          const thick =
            5 *
            0.105 *
            chord *
            (0.2969 * Math.sqrt(c) -
              0.126 * c -
              0.3516 * c * c +
              0.2843 * c * c * c -
              0.1036 * c * c * c * c);
          // Rounded tip closes down to a thin seam in the last few centimetres.
          const tipEnd =
            name.includes("stabilizer") || name.includes("elevator") ? 1.39 : 4;
          const tip = Math.min(1, (tipEnd - y) / 0.055 + 0.08);
          p.push(
            le - chord * c - hingeX,
            side * y,
            z + (face === 0 ? -1 : 1) * Math.max(0.002, thick) * tip,
          );
        }
      }
    const layer = (ns + 1) * (nc + 1);
    for (let f = 0; f < 2; f++)
      for (let s = 0; s < ns; s++)
        for (let k = 0; k < nc; k++) {
          const a = f * layer + s * (nc + 1) + k;
          indices.push(a, a + 1, a + nc + 2, a, a + nc + 2, a + nc + 1);
          const y = THREE.MathUtils.lerp(span0, span1, (s + 0.5) / ns),
            c = THREE.MathUtils.lerp(c0, c1, (k + 0.5) / nc);
          const paintTip =
            name.includes("stabilizer") || name.includes("elevator") ? 1.39 : 4;
          groups.push(
            y > paintTip - 0.19
              ? 2
              : y > paintTip - 0.225
                ? 0
                : c < 0.57
                  ? 0
                  : c < 0.74
                    ? 1
                    : c < 0.77
                      ? 0
                      : 2,
          );
        }
    for (let s = 0; s < ns; s++)
      for (const k of [0, nc]) {
        const a = s * (nc + 1) + k,
          b = a + nc + 1;
        indices.push(a, b, b + layer, a, b + layer, a + layer);
        groups.push(c0 === 0 && k === 0 ? 0 : 2);
      }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(p, 3));
    grouped(g, indices, groups);
    return add(g, colors, name, parent);
  }
  const le = (y: number) => 0.75 - 0.075 * y,
    te = (y: number) => -1.1 + 0.145 * y;
  const ailerons: { hinge: THREE.Group; axis: THREE.Vector3; side: number }[] =
    [];
  const aileronHingeX = (span: number) =>
    le(span) - (le(span) - te(span)) * 0.777;
  for (const side of [-1, 1]) {
    const label = side === 1 ? "right" : "left";
    wing(`wing-inner-${label}`, side, 0.33, 1.5, le, te, 0, 1, 0.23);
    wing(`wing-outer-${label}`, side, 1.5, 4, le, te, 0, 0.765, 0.23);
    const hinge = new THREE.Group();
    hinge.name = `aileron-${label}`;
    // The swept hinge passes through the section mid-plane, not the body Y axis.
    hinge.position.set(aileronHingeX(1.51), side * 1.51, 0.23);
    const axis = new THREE.Vector3(
      aileronHingeX(3.8) - aileronHingeX(1.51),
      side * (3.8 - 1.51),
      0,
    )
      .normalize()
      .multiplyScalar(side); // Orient both axes toward positive body Y.
    ailerons.push({ hinge, axis, side });
    root.add(hinge);
    const aileronSurface = wing(
      `aileron-surface-${label}`,
      side,
      1.51,
      3.8,
      le,
      te,
      0.777,
      1,
      0.23,
      hinge,
    );
    aileronSurface.geometry.translate(
      -hinge.position.x,
      -hinge.position.y,
      -hinge.position.z,
    );
    wing(`wingtip-${label}`, side, 3.8, 4, le, te, 0.77, 1, 0.23);
    // Spades are characteristic of the Extra's aileron system.
    tube(
      [
        new THREE.Vector3(-0.55, side * 2.65, 0.26).sub(hinge.position),
        new THREE.Vector3(-0.32, side * 2.65, 0.61).sub(hinge.position),
      ],
      0.015,
      metal,
      "spade-arm",
      hinge,
    );
    const spade = add(
      new THREE.BoxGeometry(0.27, 0.18, 0.015),
      black,
      "aileron-spade",
      hinge,
    );
    spade.position.set(-0.24, side * 2.65, 0.61).sub(hinge.position);
  }
  const tailLE = (y: number) => -2.73 - 0.13 * y,
    tailTE = (y: number) => -3.7 + 0.09 * y;
  const elevator = new THREE.Group();
  elevator.name = "elevator";
  elevator.position.x = -3.3;
  root.add(elevator);
  for (const side of [-1, 1]) {
    wing(
      "horizontal-stabilizer",
      side,
      0.1,
      1.39,
      tailLE,
      tailTE,
      0,
      0.61,
      -0.04,
    );
    wing(
      "elevator-surface",
      side,
      0.11,
      1.39,
      tailLE,
      tailTE,
      0.63,
      1,
      -0.04,
      elevator,
      -3.3,
    );
  }
  // Fin and rudder use the side-reference swept outline. Extrude along body Y.
  function fin(
    points: number[][],
    name: string,
    parent: THREE.Group,
    offsetX = 0,
  ) {
    const shape = new THREE.Shape();
    points.forEach((p, i) =>
      i
        ? shape.lineTo(p[0] - offsetX, -p[1])
        : shape.moveTo(p[0] - offsetX, -p[1]),
    );
    shape.closePath();
    const g = new THREE.ExtrudeGeometry(shape, {
      depth: 0.06,
      bevelEnabled: true,
      bevelSegments: 3,
      steps: 1,
      bevelSize: 0.018,
      bevelThickness: 0.015,
    });
    g.rotateX(-Math.PI / 2);
    g.translate(0, -0.03, 0);
    return add(g, white, name, parent);
  }
  fin(
    [
      [-2.53, -0.18],
      [-2.85, -0.37],
      [-3.25, -1.36],
      [-3.5, -1.32],
      [-3.52, 0.18],
    ],
    "vertical-stabilizer",
    root,
  );
  const rudder = new THREE.Group();
  rudder.name = "rudder";
  rudder.position.x = -3.52;
  root.add(rudder);
  fin(
    [
      [-3.53, -1.32],
      [-3.67, -1.29],
      [-3.76, 0.27],
      [-3.53, 0.18],
    ],
    "rudder-surface",
    rudder,
    -3.52,
  );
  for (const side of [-1, 1])
    for (const [z, h, m] of [
      [-0.99, 0.105, navy],
      [-0.85, 0.105, red],
    ] as const) {
      const stripe = add(new THREE.PlaneGeometry(0.38, h), m, "fin-livery");
      stripe.rotation.set(Math.PI / 2, 0, 0);
      stripe.position.set(-3.43, side * 0.052, z);
    }
  // Tandem bubble with a fitted lower lip and a narrow aft rollover frame.
  const canopy = add(
    new THREE.SphereGeometry(1, 48, 28, 0, Math.PI * 2, 0, Math.PI / 2),
    glass,
    "canopy",
  );
  canopy.rotation.x = -Math.PI / 2;
  canopy.scale.set(1.08, 0.64, 0.414);
  canopy.position.set(-0.13, 0, -0.31);
  canopy.castShadow = false;
  const rim: THREE.Vector3[] = [];
  for (let i = 0; i <= 80; i++) {
    const a = (i / 80) * Math.PI * 2;
    rim.push(
      new THREE.Vector3(
        -0.13 + 1.09 * Math.cos(a),
        0.417 * Math.sin(a),
        -0.315,
      ),
    );
  }
  tube(rim, 0.023, white, "canopy-sill");
  const arch: THREE.Vector3[] = [];
  for (let i = 0; i <= 24; i++) {
    const a = (i / 24) * Math.PI;
    arch.push(
      new THREE.Vector3(-1.03, 0.28 * Math.cos(a), -0.31 - 0.35 * Math.sin(a)),
    );
  }
  tube(arch, 0.023, black, "canopy-rear-frame");
  const floor = add(
    new THREE.BoxGeometry(2.1, 0.68, 0.04),
    black,
    "cockpit-floor",
  );
  floor.position.set(-0.15, 0, 0.13);
  for (const x of [-0.78, 0.24]) {
    ellipsoid("empty-seat-cushion", [x, 0, 0.07], [0.28, 0.24, 0.075], black);
    const back = add(
      new THREE.BoxGeometry(0.08, 0.4, 0.39),
      black,
      "empty-seat-back",
    );
    back.position.set(x - 0.22, 0, -0.12);
    back.rotation.y = -0.15;
    tube(
      [
        new THREE.Vector3(x + 0.12, 0, 0.08),
        new THREE.Vector3(x + 0.16, 0, -0.17),
      ],
      0.019,
      metal,
      "control-stick",
    );
  }
  // Cowling air intakes, metal spinner and three individually shaped blades.
  for (const side of [-1, 1]) {
    ellipsoid(
      "cowling-inlet",
      [2.6, side * 0.225, -0.06],
      [0.018, 0.115, 0.105],
      black,
    );
  }
  ellipsoid("lower-inlet", [2.48, 0, 0.235], [0.025, 0.095, 0.058], black);
  const spinner = add(
    new THREE.LatheGeometry(
      [
        new THREE.Vector2(0, 0),
        new THREE.Vector2(0.12, 0.07),
        new THREE.Vector2(0.23, 0.26),
        new THREE.Vector2(0.265, 0.5),
      ],
      48,
    ),
    white,
    "spinner",
  );
  spinner.rotation.z = Math.PI / 2;
  spinner.position.set(3.18, 0, 0);
  const propeller = new THREE.Group();
  propeller.name = "propeller";
  propeller.position.x = 2.69;
  root.add(propeller);
  const bladeMat = new THREE.MeshStandardMaterial({
    color: 0x171b21,
    roughness: 0.35,
    metalness: 0.22,
    side: THREE.DoubleSide,
  });
  for (let i = 0; i < 3; i++) {
    const blade = new THREE.Group();
    blade.name = `propeller-blade-${i + 1}`;
    blade.rotation.x = (i * 2 * Math.PI) / 3;
    propeller.add(blade);
    const shape = new THREE.Shape();
    shape.moveTo(-0.075, 0.2);
    shape.bezierCurveTo(-0.13, 0.48, -0.16, 0.8, -0.07, 1.02);
    shape.bezierCurveTo(-0.015, 1.11, 0.055, 1.1, 0.085, 1.0);
    shape.bezierCurveTo(0.14, 0.66, 0.095, 0.36, 0.075, 0.2);
    shape.closePath();
    const g = new THREE.ExtrudeGeometry(shape, {
      depth: 0.018,
      bevelEnabled: true,
      bevelSize: 0.008,
      bevelThickness: 0.007,
      bevelSegments: 2,
      steps: 1,
    });
    g.rotateY(Math.PI / 2);
    const b = add(g, bladeMat, "blade", blade);
    b.rotation.y = 0.1;
    ellipsoid(
      "blade-red-tip",
      [0.016, 0.99, 0],
      [0.018, 0.1, 0.07],
      red,
      blade,
    );
    const mark = add(
      new THREE.BoxGeometry(0.027, 0.045, 0.15),
      white,
      "blade-tip-stripe",
      blade,
    );
    mark.position.set(0.012, 0.9, 0);
  }
  const blurMat = new THREE.MeshBasicMaterial({
    color: 0xc7d7e1,
    transparent: true,
    opacity: 0.1,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  const blur = add(
    new THREE.RingGeometry(0.28, 1.08, 80),
    blurMat,
    "propeller-blur",
  );
  blur.rotation.y = Math.PI / 2;
  blur.position.x = 2.69;
  blur.castShadow = false;
  // Swept fixed gear, streamlined wheel pants and exposed rubber below them.
  for (const side of [-1, 1]) {
    const label = side === 1 ? "right" : "left";
    tube(
      [
        new THREE.Vector3(0.45, side * 0.3, 0.36),
        new THREE.Vector3(0.52, side * 0.63, 0.65),
        new THREE.Vector3(0.61, side * 1.0, 1.02),
      ],
      0.047,
      red,
      `landing-gear-${label}`,
    );
    ellipsoid(
      `wheel-pants-${label}`,
      [0.57, side * 1.04, 1.04],
      [0.48, 0.18, 0.18],
      red,
    );
    const tire = add(
      new THREE.TorusGeometry(0.18, 0.068, 12, 28),
      black,
      `wheel-${label}`,
    );
    tire.rotation.x = Math.PI / 2;
    tire.position.set(0.55, side * 1.04, 1.16);
    ellipsoid(
      "wheel-pant-highlight",
      [0.65, side * 1.04, 0.908],
      [0.3, 0.016, 0.012],
      white,
    );
  }
  tube(
    [
      new THREE.Vector3(-3.36, 0, 0.33),
      new THREE.Vector3(-3.65, 0, 0.52),
      new THREE.Vector3(-3.66, 0, 0.66),
    ],
    0.026,
    metal,
    "tailwheel-spring",
  );
  const tailwheel = add(
    new THREE.TorusGeometry(0.11, 0.037, 10, 24),
    black,
    "tailwheel",
  );
  tailwheel.rotation.x = Math.PI / 2;
  tailwheel.position.set(-3.63, 0, 0.68);
  tube(
    [new THREE.Vector3(1.55, -0.2, 0.35), new THREE.Vector3(1.39, -0.2, 0.56)],
    0.049,
    metal,
    "exhaust",
  );
  let disposed = false;
  return {
    root,
    update(frame: FlightFrame) {
      const d = THREE.MathUtils.degToRad;
      for (const { hinge, axis, side } of ailerons) {
        // Positive backend roll is right-wing down: right TE up, left TE down.
        hinge.quaternion.setFromAxisAngle(
          axis,
          -side * d(frame.controls.aileron_deg),
        );
      }
      elevator.rotation.y = d(frame.controls.elevator_deg);
      rudder.rotation.z = d(frame.controls.rudder_deg);
      propeller.rotation.x =
        (((frame.t_s * frame.controls.rpm) / 60) % 1) * 2 * Math.PI;
      blur.visible = frame.controls.rpm > 500;
      blurMat.opacity = Math.min(0.12, frame.controls.rpm / 24000);
    },
    dispose() {
      if (disposed) return;
      disposed = true;
      const geometries = new Set<THREE.BufferGeometry>(),
        materials = new Set<THREE.Material>();
      root.traverse((o) => {
        if (o instanceof THREE.Mesh) {
          geometries.add(o.geometry);
          (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) =>
            materials.add(m),
          );
        }
      });
      geometries.forEach((g) => g.dispose());
      materials.forEach((m) => m.dispose());
      root.removeFromParent();
    },
  };
}
