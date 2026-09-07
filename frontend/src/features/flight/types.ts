import type { CGEMRunResponse, PilotConfigRequest } from "../../services/types";

export type Vec3 = [number, number, number];
export type Quaternion = [number, number, number, number];
export type ScenarioId =
  | "coordinated_turn"
  | "loop"
  | "aileron_roll"
  | "immelmann"
  | "split_s"
  | "cuban_eight";
export interface FlightFrame {
  t_s: number;
  position_m: Vec3;
  velocity_mps: Vec3;
  quaternion: Quaternion;
  ias_kts: number;
  tas_kts: number;
  altitude_ft: number;
  vertical_speed_fpm: number;
  heading_deg: number;
  pitch_deg: number;
  roll_deg: number;
  alpha_deg: number;
  gz: number;
  phase: string;
  controls: {
    aileron_deg: number;
    elevator_deg: number;
    rudder_deg: number;
    throttle: number;
    rpm: number;
  };
  forces_n: { lift: number; drag: number; thrust: number; weight: number };
}
export interface FlightSimulationRequest {
  scenario: ScenarioId;
  entry_ias_kts: number | null;
  altitude_ft: number;
  loading: "solo" | "dual";
  intensity_g: number;
  pilot: PilotConfigRequest;
}
export interface FlightSimulationResponse {
  scenario: ScenarioId;
  duration_s: number;
  status: "complete" | "stopped";
  frames: FlightFrame[];
  phases: {
    name: string;
    start_s: number;
    end_s: number;
    description: string;
  }[];
  events: { time_s: number; kind: string; message: string }[];
  aircraft: {
    name: string;
    mass_kg: number;
    g_limit: number;
    vne_kias: number;
    va_kias: number;
  };
  provenance: {
    model_version: string;
    flight_model: string;
    source_urls: string[];
    assumptions: string[];
    parameter_sha256: string;
    trace_sha256: string;
  };
  physiology: {
    status: "available" | "unavailable";
    reason: string | null;
    binary_sha256: string | null;
    result: CGEMRunResponse | null;
  };
}
export interface SceneOptions {
  view: "chase" | "orbit" | "cockpit" | "split";
  showForces: boolean;
  showTrail: boolean;
  baroHpa: number;
}
export interface PhysiologySample {
  time_s: number;
  hlap: number;
  flow: number;
  reserve: number;
  conscious: number;
  greyout: number;
  blackout: number;
}
