import * as THREE from "three";
import type { FlightFrame, Quaternion, Vec3 } from "./types";
const basis = new THREE.Quaternion().setFromRotationMatrix(
  new THREE.Matrix4().set(0, 1, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 1),
);
export const nedToWorld = (v: Vec3) => new THREE.Vector3(v[1], -v[2], -v[0]);
export const bodyToWorld = (q: Quaternion) =>
  basis
    .clone()
    .multiply(new THREE.Quaternion(...q))
    .normalize();
/** Reconstructs the exact wind basis used by cgem_ext/flight/physics.py. */
export function forceVectors(frame: FlightFrame) {
  const q = bodyToWorld(frame.quaternion),
    forward = nedToWorld(frame.velocity_mps).normalize(),
    right = new THREE.Vector3(0, 1, 0).applyQuaternion(q);
  right.addScaledVector(forward, -right.dot(forward)).normalize();
  const windDown = new THREE.Vector3().crossVectors(forward, right).normalize();
  return {
    lift: windDown.multiplyScalar(-frame.forces_n.lift),
    drag: forward.multiplyScalar(-frame.forces_n.drag),
    thrust: new THREE.Vector3(1, 0, 0)
      .applyQuaternion(q)
      .multiplyScalar(frame.forces_n.thrust),
    weight: new THREE.Vector3(0, -frame.forces_n.weight, 0),
  };
}
