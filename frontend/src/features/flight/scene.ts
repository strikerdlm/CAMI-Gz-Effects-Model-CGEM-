import * as THREE from "three";
import { createAircraft, EXTRA300_COCKPIT } from "./aircraft";
import { bodyToWorld, forceVectors, nedToWorld } from "./sceneMath";
import { sampleFlight } from "./timeline";
import { drawPfd } from "./instruments";
import type {
  FlightFrame,
  FlightSimulationResponse,
  SceneOptions,
} from "./types";

const FORCE_COLORS = {
  lift: 0x50edda,
  drag: 0xffab66,
  thrust: 0xb7ed76,
  weight: 0xed86dd,
};

/** Synchronous frame rendering after ready, shared by playback, seeking and video. */
export class FlightScene {
  private renderer: THREE.WebGLRenderer;
  private scene = new THREE.Scene();
  private camera = new THREE.PerspectiveCamera(40, 1, 0.04, 100000);
  private aircraft: ReturnType<typeof createAircraft>;
  readonly ready: Promise<void>;
  private simulation: FlightSimulationResponse | null = null;
  private origin = new THREE.Vector3();
  private width = 1100;
  private height = 420;
  private terrain: THREE.Mesh;
  private sky: THREE.Mesh;
  private sun = new THREE.DirectionalLight(0xfff2de, 3.0);
  private trail = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({
      color: 0xcaf5ef,
      transparent: true,
      opacity: 0.67,
    }),
  );
  private trailTimes: number[] = [];
  private arrows = {} as Record<keyof typeof FORCE_COLORS, THREE.ArrowHelper>;
  private panelCanvas = document.createElement("canvas");
  private panelTexture: THREE.CanvasTexture;
  private cockpitPanel = new THREE.Group();
  private panelContext: CanvasRenderingContext2D;
  private hudCanvas = document.createElement("canvas");
  private hudTexture: THREE.CanvasTexture;
  private hudContext: CanvasRenderingContext2D;
  private hudScene = new THREE.Scene();
  private hudCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  private lastTime = 0;
  private lastOptions: SceneOptions | null = null;
  private orbitYaw = 0.8;
  private orbitPitch = 0.32;
  private orbitRadius = 16;
  private dragging: { x: number; y: number; id: number } | null = null;
  private disposed = false;
  private contextLost = false;
  private textures: THREE.Texture[] = [];
  private onError?: (message: string) => void;

  private canvas: HTMLCanvasElement;
  constructor(canvas: HTMLCanvasElement, onError?: (message: string) => void) {
    this.canvas = canvas;
    this.onError = onError;
    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
      powerPreference: "high-performance",
      preserveDrawingBuffer: true,
    });
    this.aircraft = createAircraft();
    this.ready = this.aircraft.ready.then(() => {
      if (!this.disposed && this.lastOptions)
        this.render(this.lastTime, this.lastOptions);
    });
    void this.ready.catch(() => undefined);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.08;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.autoClear = false;
    this.scene.fog = new THREE.Fog(0xb5ccd8, 13000, 57000);
    this.scene.add(new THREE.HemisphereLight(0xc4e5ff, 0x758358, 2.0));
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(1024, 1024);
    Object.assign(this.sun.shadow.camera, {
      left: -9,
      right: 9,
      top: 9,
      bottom: -9,
      near: 1,
      far: 120,
    });
    this.sun.shadow.bias = -0.0005;
    this.sun.shadow.normalBias = 0.06;
    this.scene.add(this.sun, this.sun.target, this.aircraft.root, this.trail);
    this.sky = new THREE.Mesh(
      new THREE.SphereGeometry(80000, 32, 18),
      new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {},
        vertexShader:
          "varying vec3 vDirection; void main(){vDirection=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}",
        fragmentShader:
          "varying vec3 vDirection; void main(){float h=normalize(vDirection).y; vec3 horizon=vec3(0.73,0.83,0.89);vec3 zenith=vec3(0.16,0.42,0.65);vec3 color=mix(horizon,zenith,pow(max(0.0,h),0.55)); gl_FragColor=vec4(color,1.0);}",
      }),
    );
    this.sky.renderOrder = -100;
    this.scene.add(this.sky);
    this.terrain = this.createTerrain();
    this.scene.add(this.terrain);
    for (const key of Object.keys(
      FORCE_COLORS,
    ) as (keyof typeof FORCE_COLORS)[]) {
      const arrow = new THREE.ArrowHelper(
        new THREE.Vector3(0, 1, 0),
        new THREE.Vector3(),
        4,
        FORCE_COLORS[key],
        0.35,
        0.18,
      );
      arrow.traverse((o) => {
        o.renderOrder = 50;
        if (o instanceof THREE.Mesh || o instanceof THREE.Line) {
          const ms = Array.isArray(o.material) ? o.material : [o.material];
          ms.forEach((m) => {
            m.depthTest = false;
            m.depthWrite = false;
          });
        }
      });
      this.arrows[key] = arrow;
      this.scene.add(arrow);
    }
    this.panelCanvas.width = 600;
    this.panelCanvas.height = 760;
    this.panelContext = this.panelCanvas.getContext("2d")!;
    this.panelTexture = new THREE.CanvasTexture(this.panelCanvas);
    this.panelTexture.colorSpace = THREE.SRGBColorSpace;
    this.textures.push(this.panelTexture);
    // Panel local basis: screen right = body right, screen up = body up.
    const panel = new THREE.Mesh(
      new THREE.PlaneGeometry(0.22, 0.28),
      new THREE.MeshBasicMaterial({
        map: this.panelTexture,
        side: THREE.DoubleSide,
        toneMapped: false,
      }),
    );
    panel.name = "live-TXi-panel";
    panel.quaternion.setFromRotationMatrix(
      new THREE.Matrix4().set(0, 0, -1, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 1),
    );
    panel.position.fromArray(EXTRA300_COCKPIT.panel);
    this.cockpitPanel.add(panel);
    const panelBack = new THREE.Mesh(
      new THREE.BoxGeometry(0.04, 0.5, 0.3),
      new THREE.MeshStandardMaterial({ color: 0x151b21, roughness: 0.65 }),
    );
    panelBack.position.copy(panel.position).add(new THREE.Vector3(0.025, 0, 0));
    panelBack.name = "instrument-panel-backing";
    this.cockpitPanel.add(panelBack);
    this.aircraft.root.add(this.cockpitPanel);
    this.hudCanvas.width = 1600;
    this.hudCanvas.height = 640;
    this.hudContext = this.hudCanvas.getContext("2d")!;
    this.hudTexture = new THREE.CanvasTexture(this.hudCanvas);
    this.hudTexture.colorSpace = THREE.SRGBColorSpace;
    this.textures.push(this.hudTexture);
    const overlay = new THREE.Mesh(
      new THREE.PlaneGeometry(2, 2),
      new THREE.MeshBasicMaterial({
        map: this.hudTexture,
        transparent: true,
        depthTest: false,
        depthWrite: false,
        toneMapped: false,
      }),
    );
    this.hudScene.add(overlay);
    canvas.style.touchAction = "none";
    canvas.addEventListener("pointerdown", this.pointerDown);
    canvas.addEventListener("pointermove", this.pointerMove);
    canvas.addEventListener("pointerup", this.pointerUp);
    canvas.addEventListener("pointercancel", this.pointerUp);
    canvas.addEventListener("wheel", this.wheel, { passive: false });
    canvas.addEventListener("webglcontextlost", this.lost);
    canvas.addEventListener("webglcontextrestored", this.restored);
    this.resize(canvas.clientWidth || 1100, canvas.clientHeight || 420);
  }
  private createTerrain() {
    const c = document.createElement("canvas");
    c.width = c.height = 2048;
    const ctx = c.getContext("2d")!;
    ctx.fillStyle = "#78906b";
    ctx.fillRect(0, 0, 2048, 2048);
    // Fixed seed: identical fields for live scene and an independently created exporter.
    let seed = 37421;
    const random = () => {
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
      return seed / 4294967296;
    };
    const shades = [
      "#8d9c73",
      "#a1a477",
      "#6d8765",
      "#8a9463",
      "#b0ab80",
      "#72875b",
      "#9da079",
    ];
    for (let x = 0; x < 2048; x += 64)
      for (let y = 0; y < 2048; y += 64) {
        ctx.fillStyle = shades[Math.floor(random() * shades.length)];
        ctx.fillRect(x + 1, y + 1, 62, 62);
        ctx.globalAlpha = 0.13;
        ctx.strokeStyle = "#e7dfb7";
        for (let j = 6; j < 64; j += 6) {
          ctx.beginPath();
          ctx.moveTo(x + j, y);
          ctx.lineTo(x + j, y + 64);
          ctx.stroke();
        }
        ctx.globalAlpha = 1;
      }
    ctx.lineWidth = 8;
    ctx.strokeStyle = "#b6bdab";
    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.moveTo(i * 480, 0);
      ctx.lineTo(i * 480 + 190, 2048);
      ctx.stroke();
    }
    ctx.beginPath();
    for (let y = 0; y <= 2048; y += 16) {
      const x = 1050 + Math.sin(y / 260) * 155 + Math.sin(y / 73) * 30;
      if (y === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = "#597e83";
    ctx.lineWidth = 26;
    ctx.stroke();
    const texture = new THREE.CanvasTexture(c);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(4, 4);
    texture.anisotropy = Math.min(
      8,
      this.renderer.capabilities.getMaxAnisotropy(),
    );
    this.textures.push(texture);
    const geometry = new THREE.PlaneGeometry(100000, 100000, 180, 180);
    geometry.rotateX(-Math.PI / 2);
    const p = geometry.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i),
        z = p.getZ(i);
      const radius = Math.hypot(x, z);
      const ridge = Math.max(0, Math.min(1, (radius - 4500) / 9000));
      p.setY(
        i,
        ridge *
          (190 +
            150 * Math.sin(x / 2400) * Math.cos(z / 1800) +
            85 * Math.sin((x + z) / 1100)),
      );
    }
    geometry.computeVertexNormals();
    const terrain = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({
        map: texture,
        roughness: 1,
        metalness: 0,
      }),
    );
    terrain.receiveShadow = true;
    return terrain;
  }
  setSimulation(sim: FlightSimulationResponse) {
    this.simulation = sim;
    const first = sim.frames[0];
    this.origin.copy(
      first ? nedToWorld(first.position_m) : new THREE.Vector3(),
    );
    this.origin.y = 0;
    const points: THREE.Vector3[] = [];
    this.trailTimes = [];
    // 10 Hz is sufficient for the displayed path; always retain the terminal point.
    for (let i = 0; i < sim.frames.length; i += 10) {
      points.push(nedToWorld(sim.frames[i].position_m).sub(this.origin));
      this.trailTimes.push(sim.frames[i].t_s);
    }
    const final = sim.frames.at(-1);
    if (final && this.trailTimes.at(-1) !== final.t_s) {
      points.push(nedToWorld(final.position_m).sub(this.origin));
      this.trailTimes.push(final.t_s);
    }
    this.trail.geometry.dispose();
    this.trail.geometry = new THREE.BufferGeometry().setFromPoints(points);
    this.trail.geometry.setDrawRange(0, 0);
    this.orbitYaw = 0.8;
    this.orbitPitch = 0.32;
    this.orbitRadius = 16;
  }
  resize(
    width: number,
    height: number,
    pixelRatio = window.devicePixelRatio || 1,
  ) {
    this.width = Math.max(1, width);
    this.height = Math.max(1, height);
    this.renderer.setPixelRatio(Math.min(2, Math.max(1, pixelRatio)));
    this.renderer.setSize(this.width, this.height, false);
  }
  render(time: number, options: SceneOptions) {
    if (this.disposed || this.contextLost) return;
    this.lastTime = time;
    this.lastOptions = { ...options };
    const frame = this.simulation
      ? sampleFlight(this.simulation.frames, time)
      : null;
    if (!frame) return;
    const aircraft = this.aircraft.root;
    aircraft.position.copy(nedToWorld(frame.position_m).sub(this.origin));
    aircraft.quaternion.copy(bodyToWorld(frame.quaternion));
    this.aircraft.update(frame);
    aircraft.updateMatrixWorld(true);
    this.sky.position.copy(aircraft.position);
    this.sun.position
      .copy(aircraft.position)
      .add(new THREE.Vector3(-35, 55, 25));
    this.sun.target.position.copy(aircraft.position);
    this.sun.target.updateMatrixWorld();
    let count = 0;
    while (count < this.trailTimes.length && this.trailTimes[count] <= time)
      count++;
    this.trail.geometry.setDrawRange(0, count);
    this.trail.visible = options.showTrail;
    const forces = forceVectors(frame);
    for (const key of Object.keys(
      this.arrows,
    ) as (keyof typeof FORCE_COLORS)[]) {
      const a = this.arrows[key],
        f = forces[key],
        magnitude = f.length();
      a.visible = options.showForces && magnitude > 1;
      a.position.copy(aircraft.position);
      if (magnitude > 1) {
        a.setDirection(f.clone().normalize());
        a.setLength(
          THREE.MathUtils.clamp(magnitude / 4000, 0.65, 8),
          0.36,
          0.2,
        );
      }
    }
    drawPfd(this.panelContext, 600, 760, frame, { baroHpa: options.baroHpa });
    this.panelTexture.needsUpdate = true;
    this.renderer.setScissorTest(false);
    this.renderer.setViewport(0, 0, this.width, this.height);
    this.renderer.clear(true, true, true);
    if (options.view === "split") {
      const left = Math.round(this.width * 0.6);
      this.renderer.setScissorTest(true);
      this.drawView(frame, "chase", 0, left);
      this.drawView(frame, "cockpit", left, this.width - left);
      this.renderer.setScissorTest(false);
    } else this.drawView(frame, options.view, 0, this.width);
    this.drawHud(frame, options);
    this.renderer.setViewport(0, 0, this.width, this.height);
    this.renderer.clearDepth();
    this.renderer.render(this.hudScene, this.hudCamera);
  }
  private drawView(
    frame: FlightFrame,
    view: "chase" | "orbit" | "cockpit",
    x: number,
    width: number,
  ) {
    const target = this.aircraft.root.position,
      q = this.aircraft.root.quaternion,
      camera = this.camera;
    camera.aspect = width / this.height;
    camera.up.set(0, 1, 0);
    this.cockpitPanel.visible = view === "cockpit";
    if (view === "cockpit") {
      camera.fov = 67;
      camera.position.copy(
        new THREE.Vector3()
          .fromArray(EXTRA300_COCKPIT.eye)
          .applyQuaternion(q)
          .add(target),
      );
      camera.up.set(0, 0, -1).applyQuaternion(q);
      camera.lookAt(
        new THREE.Vector3()
          .fromArray(EXTRA300_COCKPIT.lookAt)
          .applyQuaternion(q)
          .add(target),
      );
      Object.values(this.arrows).forEach((a) => (a.visible = false));
    } else {
      camera.fov = 38;
      // The aerobatic reference azimuth remains fixed through vertical flight.
      // A projected nose heading would flip the camera 180° at a loop apex.
      const cameraAttitude =
        view === "chase" && this.simulation?.scenario === "coordinated_turn"
          ? q
          : bodyToWorld(this.simulation!.frames[0].quaternion);
      const forward = new THREE.Vector3(1, 0, 0).applyQuaternion(
        cameraAttitude,
      );
      forward.y = 0;
      if (forward.lengthSq() < 0.0001) forward.set(0, 0, -1);
      forward.normalize();
      const right = new THREE.Vector3().crossVectors(
        forward,
        new THREE.Vector3(0, 1, 0),
      );
      const yaw = view === "orbit" ? this.orbitYaw : 0.8,
        pitch = view === "orbit" ? this.orbitPitch : 0.24;
      // Heading follows the state; roll/pitch remain visible against the world horizon.
      const radius =
        (view === "orbit" ? this.orbitRadius : 16) *
        Math.max(1, 1.25 / camera.aspect);
      camera.position
        .copy(target)
        .addScaledVector(forward, -Math.cos(yaw) * Math.cos(pitch) * radius)
        .addScaledVector(right, Math.sin(yaw) * Math.cos(pitch) * radius);
      camera.position.y += Math.sin(pitch) * radius;
      camera.lookAt(target.clone().add(new THREE.Vector3(0, 0.18, 0)));
      for (const key of Object.keys(
        this.arrows,
      ) as (keyof typeof FORCE_COLORS)[])
        this.arrows[key].visible =
          !!this.lastOptions?.showForces && Math.abs(frame.forces_n[key]) > 1;
    }
    camera.updateProjectionMatrix();
    this.renderer.setViewport(x, 0, width, this.height);
    this.renderer.setScissor(x, 0, width, this.height);
    this.renderer.render(this.scene, camera);
  }
  private drawHud(frame: FlightFrame, options: SceneOptions) {
    const ctx = this.hudContext,
      w = this.hudCanvas.width,
      h = this.hudCanvas.height;
    ctx.clearRect(0, 0, w, h);
    const scale = this.width / this.height;
    ctx.font = '500 18px "IBM Plex Mono", monospace';
    if (options.view === "split") {
      ctx.fillStyle = "rgba(210,231,242,.55)";
      ctx.fillRect(w * 0.6 - 1, 0, 2, h);
    }
    // The legend accompanies physical direction arrows and discloses compressed lengths.
    if (options.showForces && options.view !== "cockpit") {
      const keys = Object.keys(FORCE_COLORS) as (keyof typeof FORCE_COLORS)[];
      const legendWidth = Math.min(w - 60, scale > 2 ? 1080 : 1500);
      ctx.fillStyle = "rgba(7,22,34,.80)";
      ctx.fillRect(20, 78, legendWidth, 47);
      ctx.font = '500 17px "IBM Plex Mono", monospace';
      let x = 34;
      for (const key of keys) {
        ctx.fillStyle = `#${FORCE_COLORS[key].toString(16).padStart(6, "0")}`;
        ctx.fillRect(x, 96, 8, 8);
        ctx.fillText(
          `${key.toUpperCase()} ${(frame.forces_n[key] / 1000).toFixed(1)} kN`,
          x + 16,
          105,
        );
        x += 205;
      }
      ctx.fillStyle = "#c1d0d9";
      ctx.font = "14px sans-serif";
      ctx.fillText("arrow lengths capped", x + 5, 105);
    }
    this.hudTexture.needsUpdate = true;
  }
  private pointerDown = (e: PointerEvent) => {
    if (this.lastOptions?.view !== "orbit") return;
    this.dragging = { x: e.clientX, y: e.clientY, id: e.pointerId };
    this.canvas.setPointerCapture(e.pointerId);
  };
  private pointerMove = (e: PointerEvent) => {
    if (!this.dragging) return;
    this.orbitYaw -= (e.clientX - this.dragging.x) * 0.007;
    this.orbitPitch = THREE.MathUtils.clamp(
      this.orbitPitch + (e.clientY - this.dragging.y) * 0.005,
      -1.3,
      1.4,
    );
    this.dragging = { x: e.clientX, y: e.clientY, id: e.pointerId };
    if (this.lastOptions) this.render(this.lastTime, this.lastOptions);
  };
  private pointerUp = (e: PointerEvent) => {
    if (this.dragging && this.canvas.hasPointerCapture(e.pointerId))
      this.canvas.releasePointerCapture(e.pointerId);
    this.dragging = null;
  };
  private wheel = (e: WheelEvent) => {
    if (this.lastOptions?.view !== "orbit") return;
    e.preventDefault();
    this.orbitRadius = THREE.MathUtils.clamp(
      this.orbitRadius * Math.exp(e.deltaY * 0.001),
      9,
      45,
    );
    this.render(this.lastTime, this.lastOptions);
  };
  private lost = (e: Event) => {
    e.preventDefault();
    this.contextLost = true;
    this.onError?.(
      "The 3D graphics context was lost. Reload the page to restore the scene.",
    );
  };
  private restored = () => {
    this.contextLost = false;
    if (this.lastOptions) this.render(this.lastTime, this.lastOptions);
  };
  dispose() {
    if (this.disposed) return;
    this.disposed = true;
    this.canvas.removeEventListener("pointerdown", this.pointerDown);
    this.canvas.removeEventListener("pointermove", this.pointerMove);
    this.canvas.removeEventListener("pointerup", this.pointerUp);
    this.canvas.removeEventListener("pointercancel", this.pointerUp);
    this.canvas.removeEventListener("wheel", this.wheel);
    this.canvas.removeEventListener("webglcontextlost", this.lost);
    this.canvas.removeEventListener("webglcontextrestored", this.restored);
    this.aircraft.dispose();
    const geometries = new Set<THREE.BufferGeometry>(),
      materials = new Set<THREE.Material>();
    for (const scene of [this.scene, this.hudScene])
      scene.traverse((o) => {
        if (o instanceof THREE.Mesh || o instanceof THREE.Line) {
          geometries.add(o.geometry);
          (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) =>
            materials.add(m),
          );
        }
      });
    geometries.forEach((g) => g.dispose());
    materials.forEach((m) => m.dispose());
    this.textures.forEach((t) => t.dispose());
    this.sun.shadow.map?.dispose();
    this.renderer.dispose();
  }
}
