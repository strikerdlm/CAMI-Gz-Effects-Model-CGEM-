/// <reference types="node" />
// @vitest-environment node
import { describe, it, expect, vi } from "vitest";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { createAircraft, EXTRA300_ASSET } from "./aircraft";
import { forceVectors, nedToWorld, bodyToWorld } from "./sceneMath";
import type { FlightFrame } from "./types";

const bytes = readFileSync("public/models/Extra-300-r03.glb");
async function loadSource() {
  const loader = new GLTFLoader();
  // Node has no image decoder. Browser tests exercise the embedded PNGs.
  loader.register(() => ({
    name: "test-image-decoder",
    loadTexture: () => Promise.resolve(new THREE.Texture({ close: vi.fn() })),
  }));
  return (
    await loader.parseAsync(
      bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
      "",
    )
  ).scene;
}
function resourceSpies(source: THREE.Object3D) {
  const resources = new Set<
    THREE.BufferGeometry | THREE.Material | THREE.Texture
  >();
  const images = new Set<{ close: () => void }>();
  source.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return;
    resources.add(object.geometry);
    for (const material of Array.isArray(object.material)
      ? object.material
      : [object.material]) {
      resources.add(material);
      for (const value of Object.values(material))
        if (value instanceof THREE.Texture) {
          resources.add(value);
          images.add(value.image);
        }
    }
  });
  return [...resources]
    .map((r) => vi.spyOn(r, "dispose"))
    .concat([...images].map((image) => vi.mocked(image.close)));
}
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
describe("imported aircraft and rendering basis", () => {
  it("pins the self-contained revision with two propeller blades and embedded images", () => {
    expect(createHash("sha256").update(bytes).digest("hex")).toBe(
      EXTRA300_ASSET.sha256,
    );
    const gltf = JSON.parse(
      bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString(),
    );
    expect(gltf.nodes).toHaveLength(22);
    expect(
      gltf.nodes.filter((n: { name: string }) =>
        n.name.startsWith("propeller-blade-"),
      ),
    ).toHaveLength(2);
    expect(gltf.images.length).toBeGreaterThan(0);
    expect(
      gltf.images.every(
        (i: { bufferView?: number; uri?: string }) =>
          i.bufferView !== undefined && !i.uri,
      ),
    ).toBe(true);
    expect(gltf.buffers.every((b: { uri?: string }) => !b.uri)).toBe(true);
  });
  it("retains geometry and materials in an 8 m, right-handed body frame", async () => {
    const source = await loadSource();
    const meshes: THREE.Mesh[] = [];
    source.traverse((o) => {
      if (o instanceof THREE.Mesh) meshes.push(o);
    });
    const authored = meshes.map((m) => [m.geometry, m.material]);
    const a = createAircraft(() => Promise.resolve(source));
    await a.ready;
    const size = new THREE.Box3()
      .setFromObject(a.root)
      .getSize(new THREE.Vector3());
    expect(size.toArray()).toEqual(
      expect.arrayContaining([expect.any(Number)]),
    );
    expect(size.x).toBeCloseTo(EXTRA300_ASSET.length, 5);
    expect(size.y).toBeCloseTo(EXTRA300_ASSET.span, 5);
    expect(size.z).toBeCloseTo(EXTRA300_ASSET.height, 5);
    expect(meshes.map((m) => [m.geometry, m.material])).toEqual(authored);
    const centre = (name: string) =>
      new THREE.Box3()
        .setFromObject(a.root.getObjectByName(name)!)
        .getCenter(new THREE.Vector3());
    expect(centre("spinner").x).toBeGreaterThan(2);
    expect(centre("vertical-tail").x).toBeLessThan(-2);
    expect(centre("canopy-glazing").z).toBeLessThan(0);
    expect(centre("main-tyre-port").z).toBeGreaterThan(0);
    expect(
      a.root.getObjectByName("extra-300-body-frame")!.matrixWorld.determinant(),
    ).toBeCloseTo(1);
    a.dispose();
  });
  it("uses absolute propeller phase and leaves the integrated wings/tail fixed", async () => {
    const a = createAircraft(loadSource);
    const f = {
      ...frame,
      t_s: 1.123,
      controls: { ...frame.controls, rpm: 2100, aileron_deg: 12 },
    };
    a.update(f); // A seek while loading is applied on installation.
    await a.ready;
    const propeller = a.root.getObjectByName("propeller")!;
    const snapshot = propeller.quaternion.toArray();
    expect(propeller.children.map((c) => c.name).sort()).toEqual([
      "propeller-blade-a",
      "propeller-blade-b",
      "propeller-hub",
      "spinner",
    ]);
    expect(propeller.rotation.x).not.toBe(0);
    a.update({ ...f, t_s: 8 });
    a.update(f);
    expect(propeller.quaternion.toArray()).toEqual(snapshot);
    for (const name of [
      "wing-port",
      "wing-starboard",
      "horizontal-tail-port",
      "vertical-tail",
    ])
      expect(a.root.getObjectByName(name)!.quaternion.toArray()).toEqual([
        0, 0, 0, 1,
      ]);
    a.dispose();
  });
  it("disposes owned resources once without disposing another scene's assets or instruments", async () => {
    const source = await loadSource();
    const otherSource = await loadSource();
    const own = resourceSpies(source),
      other = resourceSpies(otherSource);
    const a = createAircraft(() => Promise.resolve(source));
    const b = createAircraft(() => Promise.resolve(otherSource));
    await Promise.all([a.ready, b.ready]);
    const panel = new THREE.Mesh(
      new THREE.PlaneGeometry(),
      new THREE.MeshBasicMaterial(),
    );
    const panelDisposal = vi.spyOn(panel.material, "dispose");
    a.root.add(panel);
    a.dispose();
    a.dispose();
    own.forEach((spy) => expect(spy).toHaveBeenCalledTimes(1));
    other.forEach((spy) => expect(spy).not.toHaveBeenCalled());
    expect(panelDisposal).not.toHaveBeenCalled();
    b.dispose();
    panel.geometry.dispose();
    panel.material.dispose();
  });
  it("releases a late load after disposal and never installs it", async () => {
    const source = await loadSource();
    const spies = resourceSpies(source);
    let resolve!: (value: THREE.Group) => void;
    const pending = new Promise<THREE.Group>((r) => {
      resolve = r;
    });
    const a = createAircraft(() => pending);
    const root = a.root;
    a.dispose();
    resolve(source);
    await a.ready;
    expect(a.root).toBe(root);
    expect(root.children).toHaveLength(0);
    expect(root.visible).toBe(false);
    spies.forEach((spy) => expect(spy).toHaveBeenCalledTimes(1));
  });
  it("rejects missing parts with cleanup and reports network failures", async () => {
    const source = await loadSource();
    const spies = resourceSpies(source);
    source.getObjectByName("spinner")!.userData.part_id = "unexpected-part";
    const a = createAircraft(() => Promise.resolve(source));
    await expect(a.ready).rejects.toThrow("Extra 300 model could not load");
    a.dispose();
    spies.forEach((spy) => expect(spy).toHaveBeenCalledTimes(1));
    const failed = createAircraft(() => Promise.reject(new Error("HTTP 404")));
    await expect(failed.ready).rejects.toThrow("Reload the page");
    expect(failed.root.visible).toBe(false);
    failed.dispose();
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
