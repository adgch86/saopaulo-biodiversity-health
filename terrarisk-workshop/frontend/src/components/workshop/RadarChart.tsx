'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { CATEGORY_CONFIG } from '@/lib/types';
import type { LayerCategory } from '@/lib/types';
import PlanetaryRadar, {
  CANONICAL_ORDER,
  DIMENSION_SEMANTICS,
  type PlanetaryDimension,
} from './PlanetaryRadar';

export interface RadarProfile {
  code: string;
  name: string;
  scores: Record<string, number>;
}

interface Props {
  profiles: RadarProfile[];
  size?: number;
}

const CATEGORIES: LayerCategory[] = ['governance', 'biodiversity', 'climate', 'health', 'social'];
const RINGS = [25, 50, 75, 100];

// Assign distinct colors for overlaid profiles
const PROFILE_COLORS = [
  '#7C3AED', // purple
  '#059669', // emerald
  '#DC2626', // red
  '#D97706', // amber
  '#2563EB', // blue
];

export default function RadarChart({ profiles, size = 280 }: Props) {
  const tc = useTranslations('categories');
  const tRadar = useTranslations('radarChart');

  if (profiles.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-gray-400">
        {tRadar('noData')}
      </div>
    );
  }

  // -----------------------------------------------------------------------
  // Single profile → PlanetaryRadar wedges + score table
  // -----------------------------------------------------------------------
  if (profiles.length === 1) {
    const profile = profiles[0];

    const dimensions: PlanetaryDimension[] = CANONICAL_ORDER.map((key) => ({
      key,
      label: tc(key),
      value: Math.max(0, Math.min(1, (profile.scores[key] ?? 0) / 100)),
      purchased: (profile.scores[key] ?? 0) > 0,
      semantics: DIMENSION_SEMANTICS[key] ?? 'risk',
    }));

    return (
      <div className="flex flex-col items-center">
        <PlanetaryRadar
          dimensions={dimensions}
          size={size}
          showLabels={true}
          safeZoneFraction={0.30}
        />

        {/* Score table below */}
        <div className="mt-2 w-full max-w-[260px]">
          {CATEGORIES.map((cat) => {
            const score = profile.scores[cat] ?? 0;
            const color = CATEGORY_CONFIG[cat]?.color || '#6B7280';
            return (
              <div key={cat} className="flex items-center gap-2 py-0.5">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs text-gray-600 flex-1">{tc(cat)}</span>
                <div className="w-16 h-1.5 bg-gray-200 rounded-full">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${score}%`, backgroundColor: color }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-700 w-8 text-right">
                  {Math.round(score)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // -----------------------------------------------------------------------
  // Multiple profiles → classic polygon overlay (wedges don't work well
  // for direct visual comparison)
  // -----------------------------------------------------------------------
  return <MultiProfileRadar profiles={profiles} size={size} />;
}

// ---------------------------------------------------------------------------
// MultiProfileRadar — polygon-based overlay for comparing 2+ municipalities
// ---------------------------------------------------------------------------

function MultiProfileRadar({ profiles, size = 280 }: { profiles: RadarProfile[]; size: number }) {
  const tc = useTranslations('categories');

  const center = size / 2;
  const radius = size / 2 - 50;

  const getPolygonPoints = useMemo(() => {
    return (scores: Record<string, number>) => {
      return CATEGORIES.map((cat, i) => {
        const angle = (Math.PI * 2 * i) / CATEGORIES.length - Math.PI / 2;
        const value = (scores[cat] ?? 0) / 100;
        const r = value * radius;
        return {
          x: center + r * Math.cos(angle),
          y: center + r * Math.sin(angle),
        };
      });
    };
  }, [center, radius]);

  const axisPoints = useMemo(() => {
    return CATEGORIES.map((cat, i) => {
      const angle = (Math.PI * 2 * i) / CATEGORIES.length - Math.PI / 2;
      return {
        category: cat,
        x: center + radius * Math.cos(angle),
        y: center + radius * Math.sin(angle),
        labelX: center + (radius + 20) * Math.cos(angle),
        labelY: center + (radius + 20) * Math.sin(angle),
      };
    });
  }, [center, radius]);

  const ringPolygons = useMemo(() => {
    return RINGS.map((ring) => {
      const r = (ring / 100) * radius;
      const points = CATEGORIES.map((_, i) => {
        const angle = (Math.PI * 2 * i) / CATEGORIES.length - Math.PI / 2;
        return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`;
      });
      return { ring, points: points.join(' ') };
    });
  }, [center, radius]);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="select-none">
        {ringPolygons.map(({ ring, points }) => (
          <polygon
            key={ring}
            points={points}
            fill="none"
            stroke="#E5E7EB"
            strokeWidth={ring === 50 ? 1 : 0.5}
            strokeDasharray={ring === 50 ? 'none' : '2 2'}
          />
        ))}

        {axisPoints.map((axis) => (
          <g key={axis.category}>
            <line
              x1={center} y1={center} x2={axis.x} y2={axis.y}
              stroke="#D1D5DB" strokeWidth={0.5}
            />
            <text
              x={axis.labelX} y={axis.labelY}
              textAnchor="middle" dominantBaseline="middle"
              className="text-[10px] font-medium"
              fill={CATEGORY_CONFIG[axis.category]?.color || '#6B7280'}
            >
              {tc(axis.category)}
            </text>
          </g>
        ))}

        {RINGS.map((ring) => {
          const r = (ring / 100) * radius;
          return (
            <text
              key={ring}
              x={center + 4} y={center - r - 2}
              className="text-[8px] fill-gray-400"
            >
              {ring}
            </text>
          );
        })}

        {profiles.map((profile, idx) => {
          const points = getPolygonPoints(profile.scores);
          const color = PROFILE_COLORS[idx % PROFILE_COLORS.length];
          const pointsStr = points.map((p) => `${p.x},${p.y}`).join(' ');
          return (
            <g key={profile.code}>
              <polygon
                points={pointsStr}
                fill={color}
                fillOpacity={profiles.length === 1 ? 0.2 : 0.12}
                stroke={color}
                strokeWidth={2}
                strokeOpacity={0.8}
              />
              {points.map((p, i) => (
                <circle
                  key={CATEGORIES[i]}
                  cx={p.x} cy={p.y} r={3}
                  fill={color} stroke="white" strokeWidth={1.5}
                />
              ))}
            </g>
          );
        })}
      </svg>

      <div className="flex flex-wrap gap-3 mt-2 justify-center">
        {profiles.map((profile, idx) => (
          <div key={profile.code} className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-sm"
              style={{ backgroundColor: PROFILE_COLORS[idx % PROFILE_COLORS.length] }}
            />
            <span className="text-xs text-gray-600">{profile.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
