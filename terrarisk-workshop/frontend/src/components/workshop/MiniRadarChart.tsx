'use client';

/**
 * Compact radar/spider chart for municipality cards.
 * Shows 5 category axes with normalized values (0-1).
 * Only purchased categories get filled; others show as faint guides.
 */

import { CATEGORY_CONFIG, type LayerCategory } from '@/lib/types';

const CATEGORIES: { key: LayerCategory; label: string }[] = [
  { key: 'governance', label: 'Gov' },
  { key: 'biodiversity', label: 'Bio' },
  { key: 'social', label: 'Social' },
  { key: 'health', label: 'Saúde' },
  { key: 'climate', label: 'Clima' },
];

const ANGLE_COUNT = CATEGORIES.length;
const ANGLES = CATEGORIES.map((_, i) => (Math.PI * 2 * i) / ANGLE_COUNT - Math.PI / 2);

function polar(angle: number, r: number, cx: number, cy: number): [number, number] {
  return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
}

interface Props {
  /** Values normalized 0-1 per category */
  values: Record<string, number>;
  /** Categories that have purchased layer data */
  purchasedCategories: Set<string>;
  size?: number;
}

export default function MiniRadarChart({ values, purchasedCategories, size = 130 }: Props) {
  const cx = size / 2;
  const cy = size / 2;
  const maxR = size / 2 - 16;

  // Background ring at 100%
  const ringPts = ANGLES.map((a) => polar(a, maxR, cx, cy));
  const ringPath = ringPts.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ') + 'Z';

  // Mid ring at 50%
  const midPts = ANGLES.map((a) => polar(a, maxR * 0.5, cx, cy));
  const midPath = midPts.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ') + 'Z';

  // Data polygon
  const dataPts = ANGLES.map((a, i) => {
    const cat = CATEGORIES[i].key;
    const val = purchasedCategories.has(cat) ? (values[cat] ?? 0) : 0;
    return polar(a, maxR * Math.max(val, 0.05), cx, cy);
  });
  const dataPath = dataPts.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ') + 'Z';

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="block mx-auto">
      {/* Background rings */}
      <path d={ringPath} fill="none" stroke="#e5e7eb" strokeWidth={0.7} />
      <path d={midPath} fill="none" stroke="#e5e7eb" strokeWidth={0.5} strokeDasharray="2 2" />

      {/* Axis lines + labels */}
      {ANGLES.map((angle, i) => {
        const cat = CATEGORIES[i];
        const isPurchased = purchasedCategories.has(cat.key);
        const [ex, ey] = polar(angle, maxR, cx, cy);
        const [lx, ly] = polar(angle, maxR + 12, cx, cy);
        const catColor = CATEGORY_CONFIG[cat.key]?.color || '#9ca3af';

        return (
          <g key={cat.key}>
            <line
              x1={cx} y1={cy} x2={ex} y2={ey}
              stroke={isPurchased ? '#c4b5fd' : '#e5e7eb'}
              strokeWidth={isPurchased ? 0.8 : 0.5}
            />
            <text
              x={lx} y={ly}
              textAnchor="middle"
              dominantBaseline="middle"
              fill={isPurchased ? catColor : '#d1d5db'}
              className="text-[8px] font-medium"
            >
              {cat.label}
            </text>
          </g>
        );
      })}

      {/* Filled area */}
      <path d={dataPath} fill="rgba(139, 92, 246, 0.25)" stroke="#7c3aed" strokeWidth={1.5} />

      {/* Data dots (only purchased) */}
      {dataPts.map(([px, py], i) => {
        if (!purchasedCategories.has(CATEGORIES[i].key)) return null;
        return <circle key={i} cx={px} cy={py} r={2} fill="#7c3aed" />;
      })}
    </svg>
  );
}
