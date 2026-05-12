import React from 'react';

interface AttitudeIndicatorProps {
  roll: number;   // degrees, positive = right wing down
  pitch: number;  // degrees, positive = nose up
  size?: number;
  showLabels?: boolean;
}

const clamp = (v: number, lo: number, hi: number): number =>
  Math.max(lo, Math.min(hi, v));

/**
 * Attitude indicator (artificial horizon). SVG-only.
 * Sky / ground rectangles are clipped to a circle, rotated by roll
 * and translated by pitch on a 2 px-per-degree ladder.
 *
 * NOTE: This is a visual proxy in the CGEM simulator — pitch is
 * integrated from the (Gz − 1) trace; roll is a cosmetic oscillation
 * tuned by maneuver category. NOT a physically faithful attitude.
 */
export const AttitudeIndicator: React.FC<AttitudeIndicatorProps> = ({
  roll,
  pitch,
  size = 240,
  showLabels = true,
}) => {
  const r = clamp(roll, -180, 180);
  const p = clamp(pitch, -45, 45);
  const pitchPx = p * 2;

  return (
    <svg
      viewBox="0 0 240 240"
      width={size}
      height={size}
      style={{ filter: 'drop-shadow(0 0 12px rgba(79,231,115,0.18))' }}
    >
      <defs>
        <clipPath id="adi-clip">
          <circle cx="120" cy="120" r="100" />
        </clipPath>
        <linearGradient id="sky-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0d4a6e" />
          <stop offset="100%" stopColor="#0d2330" />
        </linearGradient>
        <linearGradient id="ground-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#3a2410" />
          <stop offset="100%" stopColor="#1a0e04" />
        </linearGradient>
      </defs>

      {/* Outer ring */}
      <circle cx="120" cy="120" r="100" fill="#0a0e0c" stroke="#2a3530" strokeWidth="1.5" />

      <g clipPath="url(#adi-clip)" transform={`rotate(${-r} 120 120)`}>
        <g transform={`translate(0 ${pitchPx})`}>
          <rect x="-120" y="-320" width="480" height="440" fill="url(#sky-grad)" />
          <rect x="-120" y="120" width="480" height="440" fill="url(#ground-grad)" />
          {/* Horizon */}
          <line x1="-120" y1="120" x2="360" y2="120" stroke="#FFB400" strokeWidth="1.5" />

          {/* Pitch ladder */}
          {[-40, -30, -20, -10, 10, 20, 30, 40].map((deg) => {
            const y = 120 - deg * 2;
            const len = deg % 20 === 0 ? 50 : 30;
            return (
              <g key={deg}>
                <line
                  x1={120 - len}
                  y1={y}
                  x2={120 + len}
                  y2={y}
                  stroke="#4FE773"
                  strokeWidth="1"
                  opacity={0.8}
                />
                {deg % 20 === 0 && (
                  <>
                    <text
                      x={120 - len - 6}
                      y={y + 3}
                      fill="#4FE773"
                      fontSize="9"
                      fontFamily="IBM Plex Mono, monospace"
                      textAnchor="end"
                    >
                      {Math.abs(deg)}
                    </text>
                    <text
                      x={120 + len + 6}
                      y={y + 3}
                      fill="#4FE773"
                      fontSize="9"
                      fontFamily="IBM Plex Mono, monospace"
                    >
                      {Math.abs(deg)}
                    </text>
                  </>
                )}
              </g>
            );
          })}
        </g>
      </g>

      {/* Roll arc markers (fixed) */}
      <g stroke="#FFB400" strokeWidth="1" fill="none">
        {[-60, -45, -30, -10, 0, 10, 30, 45, 60].map((deg) => {
          const a = (deg - 90) * (Math.PI / 180);
          const r1 = 95;
          const r2 = deg === 0 ? 80 : 88;
          return (
            <line
              key={deg}
              x1={120 + Math.cos(a) * r1}
              y1={120 + Math.sin(a) * r1}
              x2={120 + Math.cos(a) * r2}
              y2={120 + Math.sin(a) * r2}
            />
          );
        })}
      </g>

      {/* Roll pointer */}
      <g transform={`rotate(${-r} 120 120)`}>
        <polygon points="120,30 115,42 125,42" fill="#FFB400" />
      </g>

      {/* Aircraft symbol (fixed) */}
      <g stroke="#FFB400" strokeWidth="2.5" fill="none">
        <line x1="86" y1="120" x2="106" y2="120" />
        <line x1="134" y1="120" x2="154" y2="120" />
        <circle cx="120" cy="120" r="3" fill="#FFB400" />
        <line x1="120" y1="103" x2="120" y2="113" />
      </g>

      {/* Inner bezel */}
      <circle cx="120" cy="120" r="101" fill="none" stroke="#000" strokeWidth="3" />

      {showLabels && (
        <text
          x="120"
          y="232"
          fill="#8c9692"
          fontSize="9"
          fontFamily="IBM Plex Mono, monospace"
          textAnchor="middle"
          letterSpacing="2"
        >
          ATT  R {r.toFixed(0).padStart(3, ' ')}°  P {p.toFixed(0).padStart(3, ' ')}°
        </text>
      )}
    </svg>
  );
};
