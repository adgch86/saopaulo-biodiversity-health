'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { CATEGORY_CONFIG } from '@/lib/types';
import type { LayerCategory } from '@/lib/types';

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

  const center = size / 2;
  const radius = (size / 2) - 50; // Leave space for labels

  // Calculate polygon points for a given set of scores
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

  // Axis endpoints
  const axisPoints = useMemo(() => {
    return CATEGORIES.map((cat, i) => {
      const angle = (Math.PI * 2 * i) / CATEGORIES.length - Math.PI / 2;
      return {
        category: cat,
        x: center + radius * Math.cos(angle),
        y: center + radius * Math.sin(angle),
        labelX: center + (radius + 20) * Math.cos(angle),
        labelY: center + (radius + 20) * Math.sin(angle),
        angle,
      };
    });
  }, [center, radius]);

  // Ring polygons
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

  if (profiles.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-gray-400">
        {tRadar('noData')}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="select-none">
        {/* Background rings */}
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

        {/* Axes */}
        {axisPoints.map((axis) => (
          <g key={axis.category}>
            <line
              x1={center}
              y1={center}
              x2={axis.x}
              y2={axis.y}
              stroke="#D1D5DB"
              strokeWidth={0.5}
            />
            {/* Category label */}
            <text
              x={axis.labelX}
              y={axis.labelY}
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-[10px] font-medium"
              fill={CATEGORY_CONFIG[axis.category]?.color || '#6B7280'}
            >
              {tc(axis.category)}
            </text>
          </g>
        ))}

        {/* Ring value labels */}
        {RINGS.map((ring) => {
          const r = (ring / 100) * radius;
          return (
            <text
              key={ring}
              x={center + 4}
              y={center - r - 2}
              className="text-[8px] fill-gray-400"
            >
              {ring}
            </text>
          );
        })}

        {/* Profile polygons */}
        {profiles.map((profile, idx) => {
          const points = getPolygonPoints(profile.scores);
          const color = PROFILE_COLORS[idx % PROFILE_COLORS.length];
          const pointsStr = points.map((p) => `${p.x},${p.y}`).join(' ');

          return (
            <g key={profile.code}>
              {/* Filled area */}
              <polygon
                points={pointsStr}
                fill={color}
                fillOpacity={profiles.length === 1 ? 0.2 : 0.12}
                stroke={color}
                strokeWidth={2}
                strokeOpacity={0.8}
              />
              {/* Value dots */}
              {points.map((p, i) => (
                <circle
                  key={CATEGORIES[i]}
                  cx={p.x}
                  cy={p.y}
                  r={3}
                  fill={color}
                  stroke="white"
                  strokeWidth={1.5}
                />
              ))}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      {profiles.length > 1 && (
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
      )}

      {/* Score table for single profile */}
      {profiles.length === 1 && (
        <div className="mt-2 w-full max-w-[260px]">
          {CATEGORIES.map((cat) => {
            const score = profiles[0].scores[cat] ?? 0;
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
      )}
    </div>
  );
}
