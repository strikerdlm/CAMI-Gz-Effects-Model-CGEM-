import { describe, expect, it } from "vitest";
import {
  sampleFlight,
  samplePhysiology,
  exportFramePlan,
  phaseForFrame,
  phaseStartTime,
} from "./timeline";
import { indicatedAltitude, unusualAttitude } from "./instrumentMath";
import type { FlightFrame } from "./types";
import type { CGEMRunResponse } from "../../services/types";

export const frame = (t_s = 0): FlightFrame => ({
  t_s,
  position_m: [t_s * 50, 0, -1828.8],
  velocity_mps: [50, 0, 0],
  quaternion: [0, 0, 0, 1],
  ias_kts: 140,
  tas_kts: 152,
  altitude_ft: 6000,
  vertical_speed_fpm: 0,
  heading_deg: 0,
  pitch_deg: 0,
  roll_deg: 0,
  alpha_deg: 3,
  gz: 1,
  phase: "Entry",
  controls: {
    aileron_deg: 0,
    elevator_deg: 0,
    rudder_deg: 0,
    throttle: 0.5,
    rpm: 2700,
  },
  forces_n: { lift: 8040, drag: 300, thrust: 300, weight: 8040 },
});

describe("one scientific playback timeline", () => {
  it("interpolates positions and heading through north without a 180 degree jump", () => {
    const f = sampleFlight(
      [
        {
          ...frame(),
          heading_deg: 350,
          quaternion: [0, 0, -Math.sin(Math.PI / 36), Math.cos(Math.PI / 36)],
        },
        {
          ...frame(10),
          heading_deg: 10,
          quaternion: [0, 0, Math.sin(Math.PI / 36), Math.cos(Math.PI / 36)],
          gz: 3,
        },
      ],
      5,
    )!;
    expect(f.position_m).toEqual([250, 0, -1828.8]);
    expect(f.heading_deg).toBeCloseTo(0);
    expect(f.gz).toBe(2);
    expect(f.t_s).toBe(5);
  });
  it.each([1, -1])(
    "derives attitude through the %s vertical branch from the quaternion",
    (direction) => {
      const pitchQuaternion = (degrees: number): FlightFrame["quaternion"] => [
        0,
        Math.sin((degrees * Math.PI) / 360),
        0,
        Math.cos((degrees * Math.PI) / 360),
      ];
      const frames = [
        {
          ...frame(),
          quaternion: pitchQuaternion(direction * 89.8),
          pitch_deg: direction * 89.8,
        },
        {
          ...frame(0.01),
          quaternion: pitchQuaternion(direction * 90.1),
          pitch_deg: direction * 89.9,
          roll_deg: 180,
          heading_deg: 180,
        },
      ];
      const beforeVertical = sampleFlight(frames, 0.005)!;
      expect(beforeVertical.pitch_deg).toBeCloseTo(direction * 89.95, 6);
      expect(beforeVertical.roll_deg).toBeCloseTo(0, 6);
      expect(beforeVertical.heading_deg).toBeCloseTo(0, 6);
      const afterVertical = sampleFlight(frames, 0.0075)!;
      expect(afterVertical.pitch_deg).toBeCloseTo(direction * 89.975, 6);
      expect(Math.abs(afterVertical.roll_deg)).toBeCloseTo(180, 6);
      expect(afterVertical.heading_deg).toBeCloseTo(180, 6);
    },
  );
  it("keeps quaternion sign changes on the same rotation and normalizes", () => {
    const f = sampleFlight(
      [frame(), { ...frame(10), quaternion: [0, 0, 0, -1] }],
      3,
    )!;
    expect(Math.hypot(...f.quaternion)).toBeCloseTo(1);
    expect(Math.abs(f.quaternion[3])).toBeCloseTo(1);
  });
  it("seeks deterministically and changes phase only at the new sample", () => {
    const frames = [frame(), { ...frame(10), phase: "Pull" }];
    const first = sampleFlight(frames, 4);
    sampleFlight(frames, 9);
    expect(sampleFlight(frames, 4)).toEqual(first);
    expect(sampleFlight(frames, 9)?.phase).toBe("Entry");
    expect(sampleFlight(frames, 10)?.phase).toBe("Pull");
    expect(sampleFlight(frames, -1)).toEqual(frames[0]);
    expect(sampleFlight([], 1)).toBeNull();
  });
  it("holds reported CGEM samples and preserves loss/recovery codes", () => {
    const result = {
      data: {
        "Time(s)": [1, 1.235, 2, 2.345],
        "HLAP(mmHg)": [70, 30, 35, 65],
        "F_con(dl/min)": [50, 10, 12, 48],
        "c_bank(s)": [7, 0, 0, 3],
        Conscious: [0, 1, 1, 2],
        Greyout: [0, 1, 1, 2],
        Blackout: [0, 1, 1, 2],
      },
    } as CGEMRunResponse;
    expect(samplePhysiology(result, 0.5)).toBeNull();
    expect(samplePhysiology(result, 1.234)?.conscious).toBe(0);
    expect(samplePhysiology(result, 1.235)?.conscious).toBe(1);
    expect(samplePhysiology(result, 2.345)?.conscious).toBe(2);
    expect(samplePhysiology(result, 1.5)?.hlap).toBe(30);
  });
  it("plans exact 30 fps video times independently of simulation playback rate", () => {
    const p = exportFramePlan(2, 6, 0.5);
    expect(p.frameCount).toBe(240);
    expect(p.duration_s).toBe(8);
    expect(p.simulationTime(60)).toBe(3);
    expect(p.simulationTime(239)).toBeLessThan(6);
    expect(() => exportFramePlan(3, 2, 1)).toThrow();
    expect(() => exportFramePlan(0, 3, 0)).toThrow();
    expect(() => exportFramePlan(0, NaN, 1)).toThrow();
  });
});

describe("phase briefings share the sampled flight state", () => {
  const phases = [
    { name: "Entry", start_s: 0, end_s: 2, description: "Entry briefing" },
    { name: "Pull", start_s: 2, end_s: 4, description: "First pull" },
    { name: "Roll", start_s: 4, end_s: 6, description: "Roll briefing" },
    { name: "Pull", start_s: 6, end_s: 8, description: "Second pull" },
  ];
  const frames = [
    frame(),
    frame(2),
    { ...frame(2.01), phase: "Pull" },
    { ...frame(4), phase: "Pull" },
    { ...frame(4.01), phase: "Roll" },
    { ...frame(6), phase: "Roll" },
    { ...frame(6.01), phase: "Pull" },
    { ...frame(8), phase: "Pull" },
  ];

  it("jumps to the first frame of the requested phase and shows its briefing", () => {
    const time = phaseStartTime(frames, phases[1]);
    expect(time).toBe(2.01);
    expect(
      phaseForFrame(phases, sampleFlight(frames, time!))?.description,
    ).toBe("First pull");
  });
  it.each([2, 2.005, 2.01])(
    "holds the matching briefing at boundary time %s",
    (time) => {
      expect(phaseForFrame(phases, sampleFlight(frames, time))?.name).toBe(
        time < 2.01 ? "Entry" : "Pull",
      );
    },
  );
  it("selects the latest matching occurrence for repeated phase names", () => {
    expect(phaseForFrame(phases, sampleFlight(frames, 3))?.description).toBe(
      "First pull",
    );
    expect(
      phaseForFrame(phases, sampleFlight(frames, 6.005))?.description,
    ).toBe("Roll briefing");
    expect(phaseForFrame(phases, sampleFlight(frames, 6.01))?.description).toBe(
      "Second pull",
    );
    expect(phaseStartTime(frames, phases[3])).toBe(6.01);
  });
  it("does not jump to a phase with no matching frame inside its interval", () => {
    expect(
      phaseStartTime(frames, { ...phases[1], start_s: 4.5, end_s: 5 }),
    ).toBeNull();
    expect(phaseForFrame(phases, null)).toBeUndefined();
  });
});

describe("air data and TXi display behavior", () => {
  it("barometric setting changes indicated altitude, with standard pressure unchanged", () => {
    expect(indicatedAltitude(6000, 1013.25)).toBeCloseTo(6000, 4);
    expect(indicatedAltitude(0, 1023.25)).toBeGreaterThan(260);
    expect(indicatedAltitude(0, 1003.25)).toBeLessThan(-260);
  });
  it("declutters at the documented strict attitude thresholds", () => {
    expect(unusualAttitude(30, 65)).toBe(false);
    expect(unusualAttitude(30.1, 0)).toBe(true);
    expect(unusualAttitude(-20.1, 0)).toBe(true);
    expect(unusualAttitude(0, -65.1)).toBe(true);
  });
});
