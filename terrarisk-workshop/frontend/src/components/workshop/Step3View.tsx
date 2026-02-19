'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { CATEGORY_CONFIG } from '@/lib/types';
import type { LayerCategory } from '@/lib/types';
import MapViewer from '@/components/map/MapViewer';
import BipartiteNetwork from './BipartiteNetwork';

// Radar chart showing mean ± std dev across 10 municipalities
const RADAR_CATEGORIES: { key: string; label: string }[] = [
  { key: 'governance', label: 'Gov' },
  { key: 'biodiversity', label: 'Bio' },
  { key: 'climate', label: 'Clima' },
  { key: 'health', label: 'Saúde' },
  { key: 'social', label: 'Social' },
];

function AverageRadarChart({
  means,
  stdDevs,
  purchasedCats,
  title,
}: {
  means: Record<string, number>;
  stdDevs: Record<string, number>;
  purchasedCats: Set<string>;
  title: string;
}) {
  const size = 240;
  const cx = size / 2;
  const cy = size / 2;
  const maxR = size / 2 - 30;
  const n = RADAR_CATEGORIES.length;
  const angles = RADAR_CATEGORIES.map((_, i) => (Math.PI * 2 * i) / n - Math.PI / 2);

  const polar = (angle: number, r: number): [number, number] => [
    cx + r * Math.cos(angle),
    cy + r * Math.sin(angle),
  ];

  // Background rings at 25%, 50%, 75%, 100%
  const rings = [25, 50, 75, 100];

  // Std dev band: upper and lower bounds
  const upperPts = angles.map((a, i) => {
    const cat = RADAR_CATEGORIES[i].key;
    if (!purchasedCats.has(cat)) return polar(a, maxR * 0.05);
    const val = Math.min((means[cat] ?? 0) + (stdDevs[cat] ?? 0), 100) / 100;
    return polar(a, maxR * Math.max(val, 0.05));
  });

  const lowerPts = angles.map((a, i) => {
    const cat = RADAR_CATEGORIES[i].key;
    if (!purchasedCats.has(cat)) return polar(a, maxR * 0.05);
    const val = Math.max((means[cat] ?? 0) - (stdDevs[cat] ?? 0), 0) / 100;
    return polar(a, maxR * Math.max(val, 0.05));
  });

  // Mean polygon
  const meanPts = angles.map((a, i) => {
    const cat = RADAR_CATEGORIES[i].key;
    if (!purchasedCats.has(cat)) return polar(a, maxR * 0.05);
    const val = (means[cat] ?? 0) / 100;
    return polar(a, maxR * Math.max(val, 0.05));
  });

  // Band path: upper clockwise + lower counterclockwise
  const bandPath =
    upperPts.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ') +
    ' ' +
    [...lowerPts].reverse().map(([x, y], i) => `${i === 0 ? 'L' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ') +
    'Z';

  return (
    <div className="mt-3 p-3 bg-white rounded-lg border border-gray-200">
      <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2 text-center">
        {title}
      </h4>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="block mx-auto">
        {/* Background rings */}
        {rings.map((ring) => {
          const r = (ring / 100) * maxR;
          const pts = angles.map((a) => polar(a, r));
          return (
            <polygon
              key={ring}
              points={pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ')}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth={ring === 50 ? 1 : 0.5}
              strokeDasharray={ring === 50 ? 'none' : '2 2'}
            />
          );
        })}

        {/* Axes + labels */}
        {angles.map((angle, i) => {
          const cat = RADAR_CATEGORIES[i];
          const isPurchased = purchasedCats.has(cat.key);
          const [ex, ey] = polar(angle, maxR);
          const [lx, ly] = polar(angle, maxR + 18);
          const catColor = CATEGORY_CONFIG[cat.key as LayerCategory]?.color || '#9ca3af';

          return (
            <g key={cat.key}>
              <line x1={cx} y1={cy} x2={ex} y2={ey} stroke={isPurchased ? '#c4b5fd' : '#e5e7eb'} strokeWidth={0.8} />
              <text
                x={lx} y={ly}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={isPurchased ? catColor : '#d1d5db'}
                className="text-[9px] font-medium"
              >
                {cat.label}
              </text>
            </g>
          );
        })}

        {/* Std dev band (gray) */}
        <path d={bandPath} fill="rgba(156, 163, 175, 0.25)" stroke="none" />

        {/* Mean polygon (purple) */}
        <polygon
          points={meanPts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ')}
          fill="rgba(139, 92, 246, 0.2)"
          stroke="#7c3aed"
          strokeWidth={2}
        />

        {/* Mean dots */}
        {meanPts.map(([px, py], i) => {
          if (!purchasedCats.has(RADAR_CATEGORIES[i].key)) return null;
          return <circle key={i} cx={px} cy={py} r={3} fill="#7c3aed" stroke="white" strokeWidth={1.5} />;
        })}

        {/* Ring value labels */}
        {[50, 100].map((ring) => {
          const r = (ring / 100) * maxR;
          return (
            <text key={ring} x={cx + 3} y={cy - r - 2} className="text-[7px] fill-gray-400">
              {ring}
            </text>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-2 text-[10px] text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-3 h-1.5 rounded-sm bg-purple-500 inline-block" />
          Média
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-1.5 rounded-sm bg-gray-300 inline-block" />
          Desvio padrão (±σ)
        </span>
      </div>

      {/* Score values */}
      <div className="mt-2 space-y-0.5">
        {RADAR_CATEGORIES.map((cat) => {
          if (!purchasedCats.has(cat.key)) return null;
          const config = CATEGORY_CONFIG[cat.key as LayerCategory];
          if (!config) return null;
          return (
            <div key={cat.key} className="flex items-center justify-between text-xs px-1">
              <span className="flex items-center gap-1.5" style={{ color: config.color }}>
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: config.color }} />
                {config.label}
              </span>
              <span className="text-gray-600">
                {(means[cat.key] ?? 0).toFixed(0)} <span className="text-gray-400">± {(stdDevs[cat.key] ?? 0).toFixed(0)}</span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface Props {
  onSubmit: (actionIds: string[]) => void;
}

export default function Step3View({ onSubmit }: Props) {
  const t = useTranslations('workshopFlow');
  const tActions = useTranslations('actionNames');
  const tDesc = useTranslations('actionDescriptions');
  const {
    pearcActions,
    selectedActions,
    toggleAction,
    workshopMunicipalities,
    group,
    layers,
  } = useWorkshopStore();

  const handleSubmit = () => {
    if (selectedActions.length > 0) {
      onSubmit(selectedActions);
    }
  };

  // Compute mean + stdDev risk values across 10 municipalities (normalized 0-100)
  const radarStats = useMemo(() => {
    if (!group || workshopMunicipalities.length === 0) return null;

    const categories = ['governance', 'biodiversity', 'climate', 'health', 'social'] as const;
    const purchasedCats = new Set<string>();

    (group.purchasedLayers || []).forEach((layerId) => {
      const layer = layers.find((l) => l.id === layerId);
      if (layer) purchasedCats.add(layer.category);
    });

    if (purchasedCats.size === 0) return null;

    // Min-max per category for normalization to 0-100
    const mins: Record<string, number> = {};
    const maxs: Record<string, number> = {};
    categories.forEach((cat) => {
      let min = Infinity;
      let max = -Infinity;
      workshopMunicipalities.forEach((m) => {
        const val = m.riskSummary[cat];
        if (val < min) min = val;
        if (val > max) max = val;
      });
      mins[cat] = min;
      maxs[cat] = max;
    });

    // Normalize all values to 0-100, compute mean and stdDev
    const means: Record<string, number> = {};
    const stdDevs: Record<string, number> = {};
    const n = workshopMunicipalities.length;

    categories.forEach((cat) => {
      const range = maxs[cat] - mins[cat];
      const normValues = workshopMunicipalities.map((m) =>
        range > 0 ? ((m.riskSummary[cat] - mins[cat]) / range) * 100 : 50
      );
      const mean = normValues.reduce((a, v) => a + v, 0) / n;
      const variance = normValues.reduce((a, v) => a + (v - mean) ** 2, 0) / n;
      means[cat] = mean;
      stdDevs[cat] = Math.sqrt(variance);
    });

    return { means, stdDevs, purchasedCats };
  }, [group, workshopMunicipalities, layers]);

  const getCategoryColor = (category: string) => {
    const config = CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG];
    return config ? config.color : '#6B7280';
  };

  const renderEvidenceStars = (avgEvidence: number) => {
    const stars = Math.round(avgEvidence);
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full ${
              i <= stars ? 'bg-yellow-500' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 flex overflow-hidden">
        {/* LEFT: Bipartite Network */}
        <div className="flex-[6] min-w-[500px] overflow-hidden border-r border-gray-200">
          <BipartiteNetwork />
        </div>

        {/* CENTER: Map */}
        <div className="flex-[3] relative">
          <MapViewer />
        </div>

        {/* RIGHT: Actions Selector Panel */}
        <div className="w-[320px] flex-shrink-0 flex flex-col border-l border-gray-200 bg-gray-50">
          <div className="px-4 py-3 border-b border-gray-200 bg-white">
            <h2 className="text-base font-bold text-gray-800">{t('selectActions')}</h2>
            <p className="text-sm text-gray-500">
              {selectedActions.length} {t('actionsSelected')}
            </p>
          </div>

          <ScrollArea className="flex-1">
            <div className="p-3 space-y-2">
              {pearcActions.map((action) => {
                const isSelected = selectedActions.includes(action.id);
                const linkedDimensions = Object.entries(action.links).filter(([, v]) => v > 0);

                return (
                  <div
                    key={action.id}
                    className={`rounded-lg border bg-white cursor-pointer transition-all hover:shadow-sm ${
                      isSelected ? 'ring-2 ring-purple-400 shadow-md' : 'border-gray-200'
                    }`}
                    onClick={() => toggleAction(action.id)}
                  >
                    <div className="p-3">
                      <div className="flex items-start gap-2.5">
                        {/* Checkbox */}
                        <div
                          className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-all ${
                            isSelected
                              ? 'bg-purple-600 border-purple-600'
                              : 'border-gray-300'
                          }`}
                        >
                          {isSelected && (
                            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <h3 className="font-semibold text-gray-800 text-sm leading-tight">
                              {tActions(action.id)}
                            </h3>
                            <Badge
                              className="text-[10px] flex-shrink-0 border-0"
                              style={{
                                backgroundColor: getCategoryColor(action.category) + '20',
                                color: getCategoryColor(action.category),
                              }}
                            >
                              {action.category}
                            </Badge>
                          </div>

                          <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                            {tDesc(action.id)}
                          </p>

                          {/* Links + Evidence */}
                          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                            <span className="flex items-center gap-1">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                              </svg>
                              {t('linksTo')} {linkedDimensions.length} {t('riskDimensions')}
                            </span>
                            <span className="flex items-center gap-1">
                              {t('evidence')}:
                              {renderEvidenceStars(action.avgEvidence)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Average Radar Chart with Std Dev band */}
              {radarStats && (
                <AverageRadarChart
                  means={radarStats.means}
                  stdDevs={radarStats.stdDevs}
                  purchasedCats={radarStats.purchasedCats}
                  title={t('avgRiskDimensions')}
                />
              )}
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* BOTTOM BAR: Legend + Continue button */}
      <div className="h-14 border-t border-gray-200 bg-white flex items-center justify-between px-6 flex-shrink-0">
        <div className="flex items-center gap-6 text-sm text-gray-600">
          <span className="font-medium">{t('legend')}:</span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-green-600" />
            {t('lowRisk')}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-yellow-500" />
            {t('mediumRisk')}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-600" />
            {t('highRisk')}
          </span>
        </div>

        <Button
          className="bg-purple-600 hover:bg-purple-700 px-6"
          disabled={selectedActions.length === 0}
          onClick={handleSubmit}
        >
          {t('viewResults')}
        </Button>
      </div>
    </div>
  );
}
