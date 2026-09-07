/** ISA pressure-altitude conversion. QNH is a display setting, not a flight input. */
export function indicatedAltitude(
  pressureAltitudeFt: number,
  qnhHpa: number,
): number {
  const pressure =
    1013.25 * (1 - (pressureAltitudeFt * 0.3048) / 44330.77) ** 5.25588;
  return (44330.77 * (1 - (pressure / qnhHpa) ** (1 / 5.25588))) / 0.3048;
}
/** Garmin TXi Pilot's Guide 190-01717-10 Rev U, unusual-attitude declutter. */
export function unusualAttitude(pitch: number, roll: number): boolean {
  return pitch > 30 || pitch < -20 || Math.abs(roll) > 65;
}
