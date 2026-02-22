'use client';

/**
 * PlanetaryRadar — Wedge-based radar chart inspired by
 * Stockholm Resilience Centre's Planetary Boundaries diagram.
 *
 * Each dimension is a radial sector (wedge). Color encodes semantics:
 * - 'risk' dimensions (climate, health, social): yellow → orange → red as value grows
 * - 'protective' dimensions (governance, biodiversity): green scale as value grows
 * - Unpurchased dimensions: muted gray
 *
 * A central circle represents the "safe operating space".
 */

// ---------------------------------------------------------------------------
// Types & constants
// ---------------------------------------------------------------------------

export interface PlanetaryDimension {
  key: string;
  label: string;
  /** Normalized 0-1 */
  value: number;
  purchased: boolean;
  semantics: 'risk' | 'protective';
}

export interface PlanetaryRadarProps {
  dimensions: PlanetaryDimension[];
  /** SVG width/height in px (default 280) */
  size?: number;
  /** Fraction of radius used for the central safe zone (default 0.30) */
  safeZoneFraction?: number;
  /** Show category labels outside the chart (default true) */
  showLabels?: boolean;
  /** Normalized 0-1 std-dev per dimension key — renders a translucent band */
  stdDevValues?: Record<string, number>;
}

/** Which categories are risk vs protective */
export const DIMENSION_SEMANTICS: Record<string, 'risk' | 'protective'> = {
  governance: 'protective',
  biodiversity: 'protective',
  climate: 'risk',
  health: 'risk',
  social: 'risk',
};

/**
 * Canonical order (clockwise from 12 o'clock):
 * governance, biodiversity, climate, health, social
 * Groups greens on the left, reds on the right.
 */
export const CANONICAL_ORDER = ['governance', 'biodiversity', 'climate', 'health', 'social'];

// ---------------------------------------------------------------------------
// Color helpers
// ---------------------------------------------------------------------------

function riskColor(value: number): string {
  // 0 → hsl(55, 90%, 55%)  yellow
  // 1 → hsl(0, 85%, 48%)   deep red
  const hue = 55 - value * 55; // 55 → 0
  const sat = 85 + value * 5;  // 85 → 90
  const lit = 55 - value * 12; // 55 → 43
  return `hsl(${hue}, ${sat}%, ${lit}%)`;
}

function protectiveColor(value: number): string {
  // 0 → hsl(142, 30%, 70%)  pale green
  // 1 → hsl(142, 70%, 38%)  rich green
  const sat = 30 + value * 40; // 30 → 70
  const lit = 70 - value * 32; // 70 → 38
  return `hsl(142, ${sat}%, ${lit}%)`;
}

function dimensionColor(d: PlanetaryDimension): string {
  if (!d.purchased) return '#d1d5db'; // gray-300
  return d.semantics === 'risk' ? riskColor(d.value) : protectiveColor(d.value);
}

function dimensionOpacity(d: PlanetaryDimension): number {
  if (!d.purchased) return 0.25;
  return 0.75 + d.value * 0.25; // 0.75 → 1.0
}

// ---------------------------------------------------------------------------
// SVG path helpers
// ---------------------------------------------------------------------------

/** Convert degrees to radians */
const deg2rad = (deg: number) => (deg * Math.PI) / 180;

/**
 * Build an SVG arc-wedge path from `innerR` to `outerR`
 * spanning `startAngle` to `endAngle` (in degrees, 0 = 12 o'clock, CW).
 */
function wedgePath(
  cx: number,
  cy: number,
  innerR: number,
  outerR: number,
  startDeg: number,
  endDeg: number,
): string {
  // SVG angles: 0° = 3 o'clock. We want 0° = 12 o'clock, so offset -90°.
  const s = deg2rad(startDeg - 90);
  const e = deg2rad(endDeg - 90);

  const x1 = cx + outerR * Math.cos(s);
  const y1 = cy + outerR * Math.sin(s);
  const x2 = cx + outerR * Math.cos(e);
  const y2 = cy + outerR * Math.sin(e);
  const x3 = cx + innerR * Math.cos(e);
  const y3 = cy + innerR * Math.sin(e);
  const x4 = cx + innerR * Math.cos(s);
  const y4 = cy + innerR * Math.sin(s);

  const largeArc = endDeg - startDeg > 180 ? 1 : 0;

  return [
    `M ${x1.toFixed(2)} ${y1.toFixed(2)}`,
    `A ${outerR} ${outerR} 0 ${largeArc} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`,
    `L ${x3.toFixed(2)} ${y3.toFixed(2)}`,
    `A ${innerR} ${innerR} 0 ${largeArc} 0 ${x4.toFixed(2)} ${y4.toFixed(2)}`,
    'Z',
  ].join(' ');
}

/**
 * Label position: polar coords at mid-angle just outside the chart.
 */
function labelPos(
  cx: number,
  cy: number,
  r: number,
  startDeg: number,
  endDeg: number,
): { x: number; y: number } {
  const midDeg = (startDeg + endDeg) / 2;
  const rad = deg2rad(midDeg - 90);
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function PlanetaryRadar({
  dimensions,
  size = 280,
  safeZoneFraction = 0.30,
  showLabels = true,
  stdDevValues,
}: PlanetaryRadarProps) {
  const cx = size / 2;
  const cy = size / 2;
  const padding = showLabels ? 36 : 12;
  const outerR = size / 2 - padding;
  const safeR = outerR * safeZoneFraction;
  const n = dimensions.length;
  const sectorAngle = 360 / n;

  // Gap between sectors (degrees)
  const gap = 2;

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className="block mx-auto"
    >
      {/* Background: faint ring guides at 50% and 100% */}
      <circle cx={cx} cy={cy} r={outerR} fill="none" stroke="#e5e7eb" strokeWidth={0.5} />
      <circle cx={cx} cy={cy} r={safeR + (outerR - safeR) * 0.5} fill="none" stroke="#e5e7eb" strokeWidth={0.4} strokeDasharray="3 3" />

      {/* Sector wedges */}
      {dimensions.map((d, i) => {
        const startDeg = i * sectorAngle + gap / 2;
        const endDeg = (i + 1) * sectorAngle - gap / 2;

        // Wedge extends from safeR to safeR + value * (outerR - safeR)
        const valueR = safeR + d.value * (outerR - safeR);
        const color = dimensionColor(d);
        const opacity = dimensionOpacity(d);

        return (
          <g key={d.key}>
            {/* Full-extent ghost wedge (shows the max possible area faintly) */}
            <path
              d={wedgePath(cx, cy, safeR, outerR, startDeg, endDeg)}
              fill={d.purchased ? color : '#e5e7eb'}
              opacity={0.08}
            />

            {/* Actual value wedge */}
            <path
              d={wedgePath(cx, cy, safeR, valueR, startDeg, endDeg)}
              fill={color}
              opacity={opacity}
              stroke={d.purchased ? color : '#d1d5db'}
              strokeWidth={d.purchased ? 1 : 0.5}
              strokeOpacity={0.6}
            />

            {/* Std dev band (if provided) */}
            {stdDevValues && stdDevValues[d.key] !== undefined && d.purchased && (
              <path
                d={wedgePath(
                  cx,
                  cy,
                  safeR + Math.max(0, d.value - stdDevValues[d.key]) * (outerR - safeR),
                  safeR + Math.min(1, d.value + stdDevValues[d.key]) * (outerR - safeR),
                  startDeg,
                  endDeg,
                )}
                fill={color}
                opacity={0.15}
                stroke={color}
                strokeWidth={0.5}
                strokeOpacity={0.3}
                strokeDasharray="2 2"
              />
            )}

            {/* Separator lines from center to edge */}
            {(() => {
              const rad = deg2rad(i * sectorAngle - 90);
              const ex = cx + outerR * Math.cos(rad);
              const ey = cy + outerR * Math.sin(rad);
              return (
                <line
                  x1={cx} y1={cy} x2={ex} y2={ey}
                  stroke="#e5e7eb" strokeWidth={0.5}
                />
              );
            })()}
          </g>
        );
      })}

      {/* Central safe zone circle */}
      <circle
        cx={cx}
        cy={cy}
        r={safeR}
        fill="hsl(142, 50%, 92%)"
        stroke="hsl(142, 40%, 70%)"
        strokeWidth={1}
      />
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="middle"
        className="text-[7px] font-medium"
        fill="hsl(142, 40%, 35%)"
      >
        safe
      </text>

      {/* Labels */}
      {showLabels &&
        dimensions.map((d, i) => {
          const startDeg = i * sectorAngle;
          const endDeg = (i + 1) * sectorAngle;
          const pos = labelPos(cx, cy, outerR + 16, startDeg, endDeg);
          return (
            <text
              key={`label-${d.key}`}
              x={pos.x}
              y={pos.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill={d.purchased ? (d.semantics === 'risk' ? '#b91c1c' : '#15803d') : '#9ca3af'}
              className="text-[9px] font-semibold"
            >
              {d.label}
            </text>
          );
        })}
    </svg>
  );
}
