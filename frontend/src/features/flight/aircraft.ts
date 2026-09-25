import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import type { FlightFrame } from "./types";

export const EXTRA300_ASSET = {
  file: "Extra-300-r03.glb",
  revision: "03",
  sha256: "bc2f6a088931817945d43ceb69eb56058156ca034c2dc62fa72b5f9f3941284d",
  parts: 22,
  span: 8,
  length: 6.613816260705852,
  height: 2.5308836962540227,
} as const;

/** Presentation anchors in forward/right/down metres, fitted to the supplied cockpit.
 * The origin is illustrative, not a measured centre of gravity.
 */
export const EXTRA300_COCKPIT = {
  eye: [-0.78, 0, -0.52],
  lookAt: [4, 0, 0.65],
  panel: [-0.05, 0, -0.29],
} as const;

async function loadAircraftSource(): Promise<THREE.Group> {
  return (
    await new GLTFLoader().loadAsync(
      `${import.meta.env.BASE_URL}models/${EXTRA300_ASSET.file}`,
    )
  ).scene;
}

/** Each scene owns its imported resources, including embedded image bitmaps. */
function disposeResources(root: THREE.Object3D) {
  const geometries = new Set<THREE.BufferGeometry>();
  const materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>();
  root.traverse((object) => {
    if (object instanceof THREE.Mesh) {
      geometries.add(object.geometry);
      for (const material of Array.isArray(object.material)
        ? object.material
        : [object.material])
        materials.add(material);
    }
  });
  for (const material of materials)
    for (const value of Object.values(material))
      if (value instanceof THREE.Texture) textures.add(value);
  geometries.forEach((geometry) => geometry.dispose());
  materials.forEach((material) => material.dispose());
  const images = new Set<{ close?: () => void }>();
  textures.forEach((texture) => {
    if (texture.image) images.add(texture.image);
    texture.dispose();
  });
  images.forEach((image) => image.close?.());
}

/** Stable body root while the self-contained GLB loads. Vertex data and paint are
 * retained; only a rigid frame transform and the propeller pivot are added.
 */
export function createAircraft(loadSource = loadAircraftSource) {
  const root = new THREE.Group();
  root.name = "Extra 300";
  root.visible = false;
  root.userData = {
    assetRevision: EXTRA300_ASSET.revision,
    assetSha256: EXTRA300_ASSET.sha256,
    configuration: "supplied-single-cockpit-two-blade",
  };
  let source: THREE.Group | undefined;
  let propeller: THREE.Group | undefined;
  let disposed = false;
  let latestFrame: FlightFrame | undefined;
  const update = (frame: FlightFrame) => {
    if (disposed) return;
    latestFrame = frame;
    if (propeller)
      propeller.rotation.x =
        (((frame.t_s * frame.controls.rpm) / 60) % 1) * 2 * Math.PI;
  };
  const ready = Promise.resolve()
    .then(loadSource)
    .then((loaded) => {
      if (disposed) {
        disposeResources(loaded);
        return;
      }
      source = loaded;
      try {
        const parts = new Map<string, THREE.Object3D>();
        source.traverse((object) => {
          const id: unknown = object.userData.part_id;
          if (typeof id === "string") {
            if (parts.has(id))
              throw new Error(`Duplicate aircraft part: ${id}`);
            parts.set(id, object);
          }
          if (object instanceof THREE.Mesh) {
            object.castShadow = id !== "canopy-glazing";
            object.receiveShadow = true;
          }
        });
        for (const id of [
          "fuselage",
          "cowling",
          "wing-port",
          "wing-starboard",
          "vertical-tail",
          "canopy-glazing",
          "cockpit-coaming",
          "propeller-blade-a",
          "propeller-blade-b",
          "propeller-hub",
          "spinner",
        ])
          if (!parts.has(id)) throw new Error(`Missing aircraft part: ${id}`);
        if (parts.size !== EXTRA300_ASSET.parts)
          throw new Error("Incompatible Extra 300 asset revision");

        const alignment = new THREE.Group();
        alignment.name = "extra-300-body-frame";
        // Source: nose -X, up +Y. Proper rotation: (x,y,z) -> (-x,-z,-y).
        alignment.quaternion.setFromRotationMatrix(
          new THREE.Matrix4().set(
            -1,
            0,
            0,
            0,
            0,
            0,
            -1,
            0,
            0,
            -1,
            0,
            0,
            0,
            0,
            0,
            1,
          ),
        );
        alignment.position.set(2.7, 0, 1.3);

        // Source meshes have baked metre coordinates; attach preserves their rest pose.
        const hub = parts.get("propeller-hub")!;
        source.updateMatrixWorld(true);
        const centre = new THREE.Box3()
          .setFromObject(hub)
          .getCenter(new THREE.Vector3());
        propeller = new THREE.Group();
        propeller.name = "propeller";
        propeller.position.copy(source.worldToLocal(centre));
        source.add(propeller);
        source.updateMatrixWorld(true);
        for (const id of [
          "propeller-blade-a",
          "propeller-blade-b",
          "propeller-hub",
          "spinner",
        ])
          propeller.attach(parts.get(id)!);
        alignment.add(source);
        root.add(alignment);
        if (latestFrame) update(latestFrame);
        root.visible = true;
      } catch (error) {
        disposeResources(source);
        source.removeFromParent();
        source = undefined;
        throw error;
      }
    })
    .catch((cause: unknown) => {
      throw new Error(
        "The Extra 300 model could not load. Reload the page to try again.",
        { cause },
      );
    });
  // Keep failures handled even if the owner is disposed before awaiting readiness.
  void ready.catch(() => undefined);
  return {
    root,
    ready,
    update,
    dispose() {
      if (disposed) return;
      disposed = true;
      if (source) {
        disposeResources(source);
        source.removeFromParent();
        source = undefined;
      }
      root.visible = false;
      // Scene-owned cockpit instruments stay attached for the scene's disposal pass.
    },
  };
}
