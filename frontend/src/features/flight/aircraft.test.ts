import { describe, it, expect } from "vitest";
import * as THREE from "three";
import { createAircraft } from "./aircraft";
import { forceVectors, nedToWorld, bodyToWorld } from "./sceneMath";
import type { FlightFrame } from "./types";
const frame: FlightFrame = {
  t_s: 0,
  position_m: [0, 0, -1828.8],
  velocity_mps: [60, 0, 0],
  quaternion: [0, 0, 0, 1],
  ias_kts: 120,
  tas_kts: 130,
  altitude_ft: 6000,
  vertical_speed_fpm: 0,
  heading_deg: 0,
  pitch_deg: 0,
  roll_deg: 0,
  alpha_deg: 0,
  gz: 1,
  phase: "Entry",
  controls: {
    aileron_deg: 0,
    elevator_deg: 0,
    rudder_deg: 0,
    throttle: 0.5,
    rpm: 2400,
  },
  forces_n: { lift: 8000, drag: 400, thrust: 400, weight: 8000 },
};
describe("physical aircraft and rendering basis", () => {
  it("fits the 8 m span / 6.96 m length with X forward, Y right, Z down", () => {
    const aircraft = createAircraft();
    const bounds = new THREE.Box3().setFromObject(aircraft.root);
    const size = bounds.getSize(new THREE.Vector3());
    expect(size.y).toBeCloseTo(8, 2);
    expect(size.x).toBeCloseTo(6.96, 2);
    expect(
      aircraft.root.getObjectByName("spinner")!.position.x,
    ).toBeGreaterThan(2);
    expect(aircraft.root.getObjectByName("canopy")!.position.z).toBeLessThan(0);
    expect(
      aircraft.root.getObjectByName("wheel-pants-right")!.position.z,
    ).toBeGreaterThan(0);
    aircraft.dispose();
  });
  it("animates opposed ailerons and actual hinges with absolute-time seek equivalence", () => {
    const a = createAircraft();
    const f = {
      ...frame,
      t_s: 1.123,
      controls: {
        ...frame.controls,
        aileron_deg: 12,
        elevator_deg: -8,
        rudder_deg: 5,
      },
    };
    a.update(f);
    const snapshots = () =>
      ["aileron-right", "aileron-left", "elevator", "rudder", "propeller"].map(
        (n) => a.root.getObjectByName(n)!.quaternion.toArray(),
      );
    const first = snapshots();
    expect(a.root.getObjectByName("elevator")!.rotation.y).not.toBe(0);
    a.update({ ...f, t_s: 8 });
    a.update(f);
    expect(snapshots()).toEqual(first);
    a.update(f);
    expect(snapshots()).toEqual(first);
    a.dispose();
  });
  it("raises the right trailing edge for positive right-roll command and reverses for left roll", () => {
    const aircraft = createAircraft();
    const edges = ["right", "left"].map((side) => {
      const mesh = aircraft.root.getObjectByName(
        `aileron-surface-${side}`,
      ) as THREE.Mesh;
      const p = mesh.geometry.attributes.position;
      const middleY = (p.getY(0) + p.getY(p.count / 2 - 1)) / 2;
      const atMidspan = Array.from({ length: p.count }, (_, i) =>
        new THREE.Vector3().fromBufferAttribute(p, i),
      ).filter((v) => Math.abs(v.y - middleY) < 1e-5);
      const trailingX = Math.min(...atMidspan.map((v) => v.x));
      const points = atMidspan.filter((v) => Math.abs(v.x - trailingX) < 1e-6);
      const local = points
        .reduce((sum, v) => sum.add(v), new THREE.Vector3())
        .divideScalar(points.length);
      return { mesh, local, rest: mesh.localToWorld(local.clone()) };
    });
    for (const command of [30, -30]) {
      aircraft.update({
        ...frame,
        controls: { ...frame.controls, aileron_deg: command },
      });
      aircraft.root.updateMatrixWorld(true);
      const right =
        edges[0].mesh.localToWorld(edges[0].local.clone()).z - edges[0].rest.z;
      const left =
        edges[1].mesh.localToWorld(edges[1].local.clone()).z - edges[1].rest.z;
      // Body Z points down: a positive backend roll rate requires right TE up.
      expect(right * Math.sign(command)).toBeLessThan(-0.1);
      expect(left * Math.sign(command)).toBeGreaterThan(0.1);
    }
    aircraft.dispose();
  });
  it("keeps the swept leading-edge centreline attached at root, middle and tip through ±30°", () => {
    const aircraft = createAircraft();
    const samples = ["right", "left"].flatMap((side) => {
      const mesh = aircraft.root.getObjectByName(
        `aileron-surface-${side}`,
      ) as THREE.Mesh;
      const p = mesh.geometry.attributes.position;
      const points = Array.from({ length: p.count }, (_, i) =>
        new THREE.Vector3().fromBufferAttribute(p, i),
      );
      const ys = [...new Set(points.map((v) => v.y))].sort((a, b) => a - b);
      return [ys[0], ys[Math.floor(ys.length / 2)], ys.at(-1)!].map((y) => {
        const row = points.filter((v) => v.y === y),
          leadingX = Math.max(...row.map((v) => v.x));
        const skin = row.filter((v) => Math.abs(v.x - leadingX) < 1e-6);
        const centre = skin
          .reduce((sum, v) => sum.add(v), new THREE.Vector3())
          .divideScalar(skin.length);
        return {
          mesh,
          centre,
          skin,
          rest: mesh.localToWorld(centre.clone()),
          skinRest: skin.map((v) => mesh.localToWorld(v.clone())),
        };
      });
    });
    for (const command of [-30, 0, 30]) {
      aircraft.update({
        ...frame,
        controls: { ...frame.controls, aileron_deg: command },
      });
      aircraft.root.updateMatrixWorld(true);
      for (const sample of samples) {
        expect(
          sample.mesh
            .localToWorld(sample.centre.clone())
            .distanceTo(sample.rest),
        ).toBeLessThan(1e-6);
        // The finite-thickness skin rotates around its hinge, moving <22 mm,
        // rather than translating the whole leading edge away from the wing.
        sample.skin.forEach((v, i) =>
          expect(
            sample.mesh.localToWorld(v.clone()).distanceTo(sample.skinRest[i]),
          ).toBeLessThan(0.022),
        );
      }
    }
    aircraft.dispose();
  });
  it("releases each allocated geometry and material once", () => {
    const a = createAircraft();
    const resources = new Set<THREE.BufferGeometry | THREE.Material>();
    a.root.traverse((o) => {
      if (o instanceof THREE.Mesh) {
        resources.add(o.geometry);
        for (const m of Array.isArray(o.material) ? o.material : [o.material])
          resources.add(m);
      }
    });
    let disposed = 0;
    resources.forEach((r) => r.addEventListener("dispose", () => disposed++));
    a.dispose();
    expect(disposed).toBe(resources.size);
    a.dispose();
    expect(disposed).toBe(resources.size);
  });
  it("rotates body axes into east/up/south without a reflection", () => {
    expect(nedToWorld([10, 20, -30]).toArray()).toEqual([20, 30, -10]);
    const q = bodyToWorld(frame.quaternion);
    expect(
      new THREE.Vector3(1, 0, 0)
        .applyQuaternion(q)
        .distanceTo(new THREE.Vector3(0, 0, -1)),
    ).toBeLessThan(1e-8);
  });
  it("uses world gravity and wind-normal lift, including inverted negative lift", () => {
    const a = forceVectors(frame);
    expect(a.lift.y).toBeCloseTo(8000);
    expect(a.weight.y).toBe(-8000);
    expect(a.drag.z).toBe(400);
    const inverted = {
      ...frame,
      quaternion: [1, 0, 0, 0] as [number, number, number, number],
      forces_n: { ...frame.forces_n, lift: -8000 },
    };
    const b = forceVectors(inverted);
    expect(b.lift.y).toBeCloseTo(8000);
    expect(b.weight.y).toBe(-8000);
    const pitched = {
      ...frame,
      quaternion: new THREE.Quaternion()
        .setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0.2)
        .toArray() as [number, number, number, number],
    };
    const c = forceVectors(pitched);
    expect(c.lift.dot(nedToWorld(pitched.velocity_mps))).toBeCloseTo(0);
    expect(c.thrust.y).toBeGreaterThan(0);
  });
});
