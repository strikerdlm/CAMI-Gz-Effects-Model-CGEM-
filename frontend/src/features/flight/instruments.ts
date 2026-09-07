import type { FlightFrame } from "./types";
import { indicatedAltitude, unusualAttitude } from "./instrumentMath";

const rad = Math.PI / 180;
const white = "#f4f7ff",
  cyan = "#65e8ef";
function label(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  size = 16,
  color = white,
  align: CanvasTextAlign = "center",
) {
  ctx.font = `500 ${size}px "IBM Plex Sans", sans-serif`;
  ctx.textAlign = align;
  ctx.textBaseline = "middle";
  ctx.fillStyle = color;
  ctx.fillText(text, x, y);
}
function line(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  x2: number,
  y2: number,
  color = white,
  width = 2,
) {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x2, y2);
  ctx.stroke();
}
function box(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  color = "#07101d",
) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = "#76869a";
  ctx.lineWidth = 1;
  ctx.strokeRect(x, y, w, h);
}

/** Reference-informed TXi layout. All telemetry comes from the same flight frame.
 * No autopilot, navigation solution or synthetic terrain database is simulated. */
export function drawPfd(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  f: FlightFrame,
  options: { baroHpa: number },
) {
  ctx.save();
  ctx.setTransform(width / 600, 0, 0, height / 760, 0, 0);
  ctx.fillStyle = "#151b23";
  ctx.fillRect(0, 0, 600, 760);
  label(ctx, "GARMIN", 300, 23, 21, "#e2e5eb");
  const declutter = unusualAttitude(f.pitch_deg, f.roll_deg);
  ctx.save();
  ctx.beginPath();
  ctx.rect(18, 45, 564, 658);
  ctx.clip();
  const sky = ctx.createLinearGradient(0, 45, 0, 480);
  sky.addColorStop(0, "#0632bd");
  sky.addColorStop(1, "#338cff");
  ctx.fillStyle = sky;
  ctx.fillRect(18, 45, 564, 658);
  // Roll about the fixed aircraft symbol; the pitch ladder moves in the earth frame.
  ctx.save();
  ctx.translate(300, 268);
  ctx.rotate(-f.roll_deg * rad);
  ctx.translate(0, f.pitch_deg * 5.2);
  const ground = ctx.createLinearGradient(0, 0, 0, 550);
  ground.addColorStop(0, "#927d38");
  ground.addColorStop(1, "#473c21");
  ctx.fillStyle = ground;
  ctx.fillRect(-1300, 0, 2600, 1800);
  line(ctx, -1300, 0, 1300, 0);
  // Keep the rotating ladder inside the attitude aperture and clear of readouts.
  const earthTransform = ctx.getTransform();
  ctx.setTransform(width / 600, 0, 0, height / 760, 0, 0);
  ctx.beginPath();
  ctx.rect(138, 108, 325, 306);
  ctx.clip();
  ctx.setTransform(earthTransform);
  for (let p = -90; p <= 90; p += 5) {
    if (!p) continue;
    const y = -p * 5.2,
      w = p % 10 === 0 ? 76 : 37;
    line(ctx, -w / 2, y, w / 2, y, white, 1.5);
    if (p % 10 === 0) {
      label(ctx, String(Math.abs(p)), -w / 2 - 19, y, 15);
      label(ctx, String(Math.abs(p)), w / 2 + 19, y, 15);
    }
  }
  // Recovery chevrons at the guide's documented pitch bands, directed to horizon.
  if (declutter) {
    for (const p of [-80, -60, -40, 50, 65, 80]) {
      const y = -p * 5.2,
        towardHorizon = Math.sign(p);
      line(ctx, -48, y, 0, y + towardHorizon * 28, "#ff4238", 7);
      line(ctx, 0, y + towardHorizon * 28, 48, y, "#ff4238", 7);
    }
  }
  ctx.restore();
  // Bank scale and moving bank pointer.
  ctx.save();
  ctx.translate(300, 268);
  for (const b of [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]) {
    const a = b * rad,
      r = 170,
      r2 = r + (b % 30 === 0 ? 15 : 9);
    line(
      ctx,
      Math.sin(a) * r,
      -Math.cos(a) * r,
      Math.sin(a) * r2,
      -Math.cos(a) * r2,
    );
  }
  ctx.rotate(-f.roll_deg * rad);
  ctx.fillStyle = white;
  ctx.beginPath();
  ctx.moveTo(0, -164);
  ctx.lineTo(-8, -147);
  ctx.lineTo(8, -147);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
  // Fixed yellow wings / reference aircraft, without a flight-director command.
  for (const side of [-1, 1]) {
    line(ctx, 300 + side * 22, 278, 300 + side * 86, 263, "#10141a", 8);
    line(ctx, 300 + side * 22, 278, 300 + side * 86, 263, "#ffec38", 4);
  }
  ctx.strokeStyle = "#ffec38";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(300, 268, 8, 0, 2 * Math.PI);
  ctx.stroke();

  const altitude = indicatedAltitude(f.altitude_ft, options.baroHpa);
  // Moving tapes share the reference image's black translucent columns.
  ctx.fillStyle = "#081526dc";
  ctx.fillRect(53, 115, 81, 302);
  ctx.fillRect(468, 115, 82, 302);
  ctx.save();
  ctx.beginPath();
  ctx.rect(53, 115, 81, 302);
  ctx.clip();
  for (
    let speed = Math.floor(f.ias_kts / 10) * 10 - 50;
    speed <= f.ias_kts + 50;
    speed += 10
  ) {
    if (speed < 0) continue;
    const y = 268 - (speed - f.ias_kts) * 3.7;
    line(ctx, 119, y, 131, y, white, 1.5);
    if (speed % 20 === 0) label(ctx, String(speed), 111, y, 22, white, "right");
  }
  for (const [low, high, color] of [
    [60, 158, "#23ed69"],
    [158, 220, "#fff032"],
  ] as const) {
    ctx.fillStyle = color;
    ctx.fillRect(126, 268 - (high - f.ias_kts) * 3.7, 7, (high - low) * 3.7);
  }
  line(
    ctx,
    119,
    268 - (220 - f.ias_kts) * 3.7,
    134,
    268 - (220 - f.ias_kts) * 3.7,
    "#ff3939",
    5,
  );
  ctx.restore();
  ctx.save();
  ctx.beginPath();
  ctx.rect(468, 115, 82, 302);
  ctx.clip();
  for (
    let alt = Math.floor(altitude / 100) * 100 - 400;
    alt <= altitude + 400;
    alt += 100
  ) {
    const y = 268 - (alt - altitude) * 0.48;
    line(ctx, 468, y, 479, y, white, 1.5);
    label(ctx, String(alt), 546, y, 19, white, "right");
  }
  ctx.restore();
  box(ctx, 49, 247, 88, 42);
  label(ctx, Math.round(f.ias_kts).toString(), 92, 269, 31);
  box(ctx, 455, 247, 99, 42);
  label(ctx, String(Math.round(altitude / 10) * 10), 505, 269, 28);
  label(ctx, "IAS · KT", 93, 99, 13, cyan);
  label(ctx, "ALT · FT", 508, 99, 13, cyan);
  box(ctx, 53, 417, 81, 31);
  label(ctx, `TAS ${Math.round(f.tas_kts)}`, 94, 433, 14);
  box(ctx, 458, 417, 98, 31);
  label(ctx, options.baroHpa.toFixed(1), 507, 433, 17, cyan);
  // Vertical-speed scale ±6000 ft/min, off-scale values retained in numeric field.
  line(ctx, 568, 145, 568, 390, "#cad4df", 1);
  for (const v of [-6, -3, 0, 3, 6]) {
    const y = 268 - v * 19;
    line(ctx, 561, y, 574, y, white, 1);
  }
  const vy = 268 - Math.max(-6, Math.min(6, f.vertical_speed_fpm / 1000)) * 19;
  line(ctx, 555, vy, 578, vy, cyan, 4);

  if (!declutter) {
    // Heading-only HSI. No map, CDI, selected heading or guidance is fabricated.
    ctx.fillStyle = "#08111ccd";
    ctx.beginPath();
    ctx.arc(300, 579, 126, 0, 2 * Math.PI);
    ctx.fill();
    ctx.save();
    ctx.translate(300, 579);
    ctx.rotate(-f.heading_deg * rad);
    for (let deg = 0; deg < 360; deg += 5) {
      const a = deg * rad,
        outer = 119,
        inner = deg % 30 === 0 ? 103 : 111;
      line(
        ctx,
        Math.sin(a) * inner,
        -Math.cos(a) * inner,
        Math.sin(a) * outer,
        -Math.cos(a) * outer,
        white,
        deg % 30 === 0 ? 2 : 1,
      );
      if (deg % 30 === 0) {
        ctx.save();
        ctx.translate(Math.sin(a) * 87, -Math.cos(a) * 87);
        ctx.rotate(a);
        label(
          ctx,
          ({ 0: "N", 90: "E", 180: "S", 270: "W" } as Record<number, string>)[
            deg
          ] ?? String(deg / 10),
          0,
          0,
          20,
        );
        ctx.restore();
      }
    }
    ctx.restore();
    line(ctx, 300, 557, 300, 599, white, 3);
    line(ctx, 281, 581, 319, 581, white, 3);
    line(ctx, 292, 597, 308, 597, white, 3);
    ctx.fillStyle = white;
    ctx.beginPath();
    ctx.moveTo(300, 461);
    ctx.lineTo(291, 449);
    ctx.lineTo(309, 449);
    ctx.closePath();
    ctx.fill();
    box(ctx, 258, 421, 84, 32);
    label(
      ctx,
      `${Math.round(f.heading_deg) % 360}`.padStart(3, "0") + "°",
      300,
      439,
      23,
    );
    label(ctx, "TRUE HEADING", 300, 638, 12, "#adbfcd");
    box(ctx, 42, 477, 104, 57);
    label(ctx, "G LOAD", 94, 492, 12, cyan);
    label(ctx, `${f.gz >= 0 ? "+" : ""}${f.gz.toFixed(2)}`, 94, 518, 24);
    box(ctx, 455, 477, 109, 57);
    label(ctx, "VS · FT/MIN", 509, 492, 12, cyan);
    label(
      ctx,
      String(Math.round(f.vertical_speed_fpm / 10) * 10),
      509,
      518,
      22,
    );
  } else {
    box(ctx, 192, 535, 216, 42, "#141c2ae6");
    label(ctx, "UNUSUAL ATTITUDE", 300, 557, 16, "#ffe766");
    label(ctx, `${f.gz >= 0 ? "+" : ""}${f.gz.toFixed(2)} G`, 300, 608, 29);
    label(ctx, "DISPLAY DECLUTTERED", 300, 648, 12, white);
  }
  ctx.restore();
  box(ctx, 18, 704, 564, 35, "#080e15");
  label(ctx, "TXi reference · educational display", 300, 722, 14, "#a5b4c5");
  ctx.restore();
}
