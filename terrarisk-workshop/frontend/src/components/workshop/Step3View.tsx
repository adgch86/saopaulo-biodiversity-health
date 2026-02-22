'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { CATEGORY_CONFIG } from '@/lib/types';
import type { LayerCategory } from '@/lib/types';
import BipartiteNetwork from './BipartiteNetwork';
import PlanetaryRadar, {
  CANONICAL_ORDER,
  DIMENSION_SEMANTICS,
  type PlanetaryDimension,
} from './PlanetaryRadar';

const SHORT_LABELS: Record<string, string> = {
  governance: 'Gov',
  biodiversity: 'Bio',
  climate: 'Clima',
  health: 'Saúde',
  social: 'Social',
};

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
  const dimensions: PlanetaryDimension[] = CANONICAL_ORDER.map((key) => ({
    key,
    label: SHORT_LABELS[key] ?? key,
    value: Math.max(0, Math.min(1, (means[key] ?? 0) / 100)),
    purchased: purchasedCats.has(key),
    semantics: DIMENSION_SEMANTICS[key] ?? 'risk',
  }));

  // Normalize stdDevs from 0-100 to 0-1
  const stdDevNormalized: Record<string, number> = {};
  CANONICAL_ORDER.forEach((key) => {
    stdDevNormalized[key] = (stdDevs[key] ?? 0) / 100;
  });

  return (
    <div className="mt-3 p-3 bg-white rounded-lg border border-gray-200">
      <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2 text-center">
        {title}
      </h4>

      <PlanetaryRadar
        dimensions={dimensions}
        size={320}
        showLabels={true}
        safeZoneFraction={0.28}
        stdDevValues={stdDevNormalized}
      />

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-2 text-[10px] text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-3 h-1.5 rounded-sm bg-emerald-500 inline-block" />
          Média
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-1.5 rounded-sm bg-gray-300 inline-block opacity-50" />
          Desvio padrão (±σ)
        </span>
      </div>

      {/* Score values */}
      <div className="mt-2 space-y-0.5">
        {CANONICAL_ORDER.map((key) => {
          if (!purchasedCats.has(key)) return null;
          const config = CATEGORY_CONFIG[key as LayerCategory];
          if (!config) return null;
          return (
            <div key={key} className="flex items-center justify-between text-xs px-1">
              <span className="flex items-center gap-1.5" style={{ color: config.color }}>
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: config.color }} />
                {config.label}
              </span>
              <span className="text-gray-600">
                {(means[key] ?? 0).toFixed(0)} <span className="text-gray-400">± {(stdDevs[key] ?? 0).toFixed(0)}</span>
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
        <div className="flex-1 min-w-0 overflow-hidden border-r border-gray-200">
          <BipartiteNetwork />
        </div>

        {/* CENTER: Average Radar Chart (replaces map) */}
        {radarStats && (
          <div className="w-[380px] flex-shrink-0 flex flex-col items-center justify-center border-r border-gray-200 bg-gray-50/50 p-4">
            <AverageRadarChart
              means={radarStats.means}
              stdDevs={radarStats.stdDevs}
              purchasedCats={radarStats.purchasedCats}
              title={t('avgRiskDimensions')}
            />
          </div>
        )}

        {/* RIGHT: Actions Selector Panel */}
        <div className="w-[340px] flex-shrink-0 flex flex-col border-l border-gray-200 bg-gray-50">
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
