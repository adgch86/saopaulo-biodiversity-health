'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { CATEGORY_CONFIG } from '@/lib/types';
import type { LayerCategory } from '@/lib/types';
import PlanetaryRadar, {
  CANONICAL_ORDER,
  DIMENSION_SEMANTICS,
} from './PlanetaryRadar';
import VulnerabilityComparison from './VulnerabilityComparison';

export default function RankingComparison() {
  const t = useTranslations('workshopFlow');
  const tActions = useTranslations('actionNames');
  const { comparison, setWorkshopPhase, workshopMunicipalities, group, layers } = useWorkshopStore();

  // Lookup municipality name from store as fallback
  const getMuniName = (code: string, fallbackName: string) => {
    if (fallbackName) return fallbackName;
    const muni = workshopMunicipalities.find((m) => m.code === code);
    return muni ? muni.name : code;
  };

  // Lookup compositeScore from platformRanking by municipality code
  const scoreByCode = useMemo(() => {
    if (!comparison) return new Map<string, number>();
    const map = new Map<string, number>();
    comparison.platformRanking.forEach((entry) => {
      map.set(entry.code, entry.compositeScore);
    });
    return map;
  }, [comparison]);

  // Normalize relevanceScore: find max to scale to 0-100%
  const maxRelevance = useMemo(() => {
    if (!comparison) return 1;
    return Math.max(...comparison.suggestedActions.map((a) => a.relevanceScore), 1);
  }, [comparison]);

  // Compute average radar for group (purchased categories) vs TerraRisk Boundaries (all 5)
  const radarComparison = useMemo(() => {
    if (!group || workshopMunicipalities.length === 0) return null;

    const categories = CANONICAL_ORDER;
    const n = workshopMunicipalities.length;

    // Purchased categories by the group
    const purchasedCats = new Set<string>();
    (group.purchasedLayers || []).forEach((layerId) => {
      const layer = layers.find((l) => l.id === layerId);
      if (layer) purchasedCats.add(layer.category);
    });

    // Min-max per category for normalization to 0-100
    const mins: Record<string, number> = {};
    const maxs: Record<string, number> = {};
    categories.forEach((cat) => {
      let min = Infinity;
      let max = -Infinity;
      workshopMunicipalities.forEach((m) => {
        const val = m.riskSummary[cat as keyof typeof m.riskSummary];
        if (val < min) min = val;
        if (val > max) max = val;
      });
      mins[cat] = min;
      maxs[cat] = max;
    });

    // Normalize all values to 0-100, compute mean and stdDev
    const groupMeans: Record<string, number> = {};
    const groupStdDevs: Record<string, number> = {};
    const fullMeans: Record<string, number> = {};
    const fullStdDevs: Record<string, number> = {};

    categories.forEach((cat) => {
      const range = maxs[cat] - mins[cat];
      const normValues = workshopMunicipalities.map((m) =>
        range > 0 ? ((m.riskSummary[cat as keyof typeof m.riskSummary] - mins[cat]) / range) * 100 : 50
      );
      const mean = normValues.reduce((a, v) => a + v, 0) / n;
      const variance = normValues.reduce((a, v) => a + (v - mean) ** 2, 0) / n;

      // Group uses only purchased categories
      groupMeans[cat] = mean;
      groupStdDevs[cat] = Math.sqrt(variance);

      // TerraRisk Boundaries uses all categories
      fullMeans[cat] = mean;
      fullStdDevs[cat] = Math.sqrt(variance);
    });

    return { groupMeans, groupStdDevs, fullMeans, fullStdDevs, purchasedCats };
  }, [group, workshopMunicipalities, layers]);

  if (!comparison) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-gray-500">Loading results...</p>
      </div>
    );
  }

  const getCorrelationColor = (value: number) => {
    if (value > 0.7) return 'text-green-600';
    if (value > 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCorrelationBg = (value: number) => {
    if (value > 0.7) return 'bg-green-100';
    if (value > 0.4) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getDiffColor = (diff: number) => {
    const absDiff = Math.abs(diff);
    if (absDiff <= 1) return 'text-green-600';
    if (absDiff <= 3) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getDiffArrow = (diff: number) => {
    if (diff === 0) return '=';
    if (diff > 0) return `↓${diff}`;
    return `↑${Math.abs(diff)}`;
  };

  const agreementPercentage = Math.round(comparison.rankingCorrelation.spearman * 100);

  return (
    <ScrollArea className="h-full">
      <div className="max-w-7xl mx-auto p-4 lg:p-8 space-y-6 lg:space-y-8">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-gray-800 mb-1 lg:mb-2">{t('phase4Title')}</h1>
          <p className="text-sm lg:text-base text-gray-600">{t('phase4Desc')}</p>
        </div>

        <Card className="border-2 border-purple-200">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
            <CardTitle className="text-base lg:text-lg">{t('rankingCorrelation')}</CardTitle>
          </CardHeader>
          <CardContent className="p-4 lg:p-6">
            <div className="grid grid-cols-3 gap-3 lg:gap-6">
              <div className="text-center">
                <div
                  className={`text-3xl lg:text-5xl font-bold mb-1 lg:mb-2 ${getCorrelationColor(
                    comparison.rankingCorrelation.spearman
                  )}`}
                >
                  {agreementPercentage}%
                </div>
                <p className="text-xs lg:text-sm text-gray-600">
                  Spearman
                </p>
              </div>
              <div className="text-center border-l border-r border-gray-200">
                <div
                  className={`text-3xl lg:text-5xl font-bold mb-1 lg:mb-2 ${getCorrelationColor(
                    comparison.rankingCorrelation.kendall
                  )}`}
                >
                  {Math.round(comparison.rankingCorrelation.kendall * 100)}%
                </div>
                <p className="text-xs lg:text-sm text-gray-600">
                  Kendall Tau
                </p>
              </div>
              <div className="text-center flex items-center justify-center">
                <div
                  className={`text-lg lg:text-3xl font-bold px-2 lg:px-4 py-1 lg:py-2 rounded-lg inline-block ${getCorrelationBg(
                    comparison.rankingCorrelation.spearman
                  )} ${getCorrelationColor(comparison.rankingCorrelation.spearman)}`}
                >
                  {comparison.rankingCorrelation.spearman > 0.7
                    ? 'High'
                    : comparison.rankingCorrelation.spearman > 0.4
                    ? 'Moderate'
                    : 'Low'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* RADAR COMPARISON: Group average vs TerraRisk Boundaries */}
        {radarComparison && (
          <Card>
            <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
              <CardTitle className="text-base lg:text-lg">{t('radarComparison') || 'Visão Dimensional'}</CardTitle>
            </CardHeader>
            <CardContent className="p-4 lg:p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Group average radar (purchased categories only) */}
                <div className="flex flex-col items-center">
                  <h4 className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-3 text-center">
                    {t('yourGroup') || 'Seu Grupo'}
                  </h4>
                  <PlanetaryRadar
                    dimensions={CANONICAL_ORDER.map((key) => ({
                      key,
                      label: CATEGORY_CONFIG[key as LayerCategory]?.label ?? key,
                      value: Math.max(0, Math.min(1, (radarComparison.groupMeans[key] ?? 0) / 100)),
                      purchased: radarComparison.purchasedCats.has(key),
                      semantics: DIMENSION_SEMANTICS[key] ?? 'risk',
                    }))}
                    size={280}
                    showLabels={true}
                    safeZoneFraction={0.28}
                    stdDevValues={Object.fromEntries(
                      CANONICAL_ORDER.map((key) => [key, (radarComparison.groupStdDevs[key] ?? 0) / 100])
                    )}
                  />
                  <div className="mt-2 space-y-0.5 w-full max-w-[260px]">
                    {CANONICAL_ORDER.map((key) => {
                      if (!radarComparison.purchasedCats.has(key)) return null;
                      const config = CATEGORY_CONFIG[key as LayerCategory];
                      if (!config) return null;
                      return (
                        <div key={key} className="flex items-center justify-between text-xs px-1">
                          <span className="flex items-center gap-1.5" style={{ color: config.color }}>
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: config.color }} />
                            {config.label}
                          </span>
                          <span className="text-gray-600">
                            {(radarComparison.groupMeans[key] ?? 0).toFixed(0)}{' '}
                            <span className="text-gray-400">± {(radarComparison.groupStdDevs[key] ?? 0).toFixed(0)}</span>
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* TerraRisk Boundaries radar (all 5 dimensions) */}
                <div className="flex flex-col items-center">
                  <h4 className="text-xs font-semibold text-purple-600 uppercase tracking-wide mb-3 text-center">
                    TerraRisk Boundaries
                  </h4>
                  <PlanetaryRadar
                    dimensions={CANONICAL_ORDER.map((key) => ({
                      key,
                      label: CATEGORY_CONFIG[key as LayerCategory]?.label ?? key,
                      value: Math.max(0, Math.min(1, (radarComparison.fullMeans[key] ?? 0) / 100)),
                      purchased: true,
                      semantics: DIMENSION_SEMANTICS[key] ?? 'risk',
                    }))}
                    size={280}
                    showLabels={true}
                    safeZoneFraction={0.28}
                    stdDevValues={Object.fromEntries(
                      CANONICAL_ORDER.map((key) => [key, (radarComparison.fullStdDevs[key] ?? 0) / 100])
                    )}
                  />
                  <div className="mt-2 space-y-0.5 w-full max-w-[260px]">
                    {CANONICAL_ORDER.map((key) => {
                      const config = CATEGORY_CONFIG[key as LayerCategory];
                      if (!config) return null;
                      return (
                        <div key={key} className="flex items-center justify-between text-xs px-1">
                          <span className="flex items-center gap-1.5" style={{ color: config.color }}>
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: config.color }} />
                            {config.label}
                          </span>
                          <span className="text-gray-600">
                            {(radarComparison.fullMeans[key] ?? 0).toFixed(0)}{' '}
                            <span className="text-gray-400">± {(radarComparison.fullStdDevs[key] ?? 0).toFixed(0)}</span>
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center gap-6 mt-4 text-[11px] text-gray-500">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-1.5 rounded-sm bg-emerald-500 inline-block" />
                  Média
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-1.5 rounded-sm bg-gray-300 inline-block opacity-50" />
                  Desvio padrão (±σ)
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-1.5 rounded-sm bg-gray-200 inline-block" />
                  Sem dados
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:gap-6">
          <Card>
            <CardHeader className="bg-blue-50 p-3 lg:p-6">
              <CardTitle className="text-base lg:text-lg flex items-center gap-2">
                <svg className="w-4 h-4 lg:w-5 lg:h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {t('yourRanking')}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-gray-200">
                {comparison.userRanking.map((entry) => {
                  const score = scoreByCode.get(entry.code);
                  return (
                    <div key={entry.code} className="flex items-center gap-2 lg:gap-3 p-2.5 lg:p-4 hover:bg-gray-50">
                      <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs lg:text-sm flex-shrink-0">
                        {entry.position}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs lg:text-sm font-medium text-gray-800 truncate">
                          {getMuniName(entry.code, entry.name)}
                        </div>
                      </div>
                      {score !== undefined && (
                        <Badge variant="outline" className="text-xs font-semibold text-blue-700 border-blue-300 flex-shrink-0">
                          {score.toFixed(2)}
                        </Badge>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="bg-purple-50 p-3 lg:p-6">
              <CardTitle className="text-base lg:text-lg flex items-center gap-2">
                <svg className="w-4 h-4 lg:w-5 lg:h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                {t('platformRanking')}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-gray-200">
                {comparison.platformRanking.map((entry) => (
                  <div key={entry.code} className="flex items-center gap-2 lg:gap-3 p-2.5 lg:p-4 hover:bg-gray-50">
                    <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-xs lg:text-sm flex-shrink-0">
                      {entry.position}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs lg:text-sm font-medium text-gray-800 truncate">
                        {getMuniName(entry.code, entry.name)}
                      </div>
                    </div>
                    <Badge variant="outline" className="text-xs font-semibold text-purple-700 border-purple-300 flex-shrink-0">
                      {entry.compositeScore.toFixed(2)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base lg:text-lg">{t('positionDiff')}</CardTitle>
          </CardHeader>
          <CardContent className="p-3 lg:p-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 lg:gap-4">
              {comparison.positionDifferences.map((diff) => (
                <div
                  key={diff.code}
                  className="flex items-center justify-between p-2.5 lg:p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-xs lg:text-sm font-medium text-gray-800 truncate flex-1 min-w-0 mr-2">
                    {getMuniName(diff.code, diff.name)}
                  </span>
                  <div className="flex items-center gap-1 lg:gap-2 flex-shrink-0">
                    <Badge variant="outline" className="text-xs">
                      #{diff.userPosition}
                    </Badge>
                    <span className={`font-bold text-base lg:text-lg ${getDiffColor(diff.difference)}`}>
                      {getDiffArrow(diff.difference)}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      #{diff.platformPosition}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Separator />

        <Card>
          <CardHeader className="bg-gradient-to-r from-green-50 to-blue-50">
            <CardTitle className="text-base lg:text-lg">{t('actionsComparison')}</CardTitle>
          </CardHeader>
          <CardContent className="p-4 lg:p-6">
            <div className="mb-4 lg:mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">{t('actionOverlap')}</span>
                <span className="text-xl lg:text-2xl font-bold text-purple-600">
                  {Math.round(comparison.actionOverlap)}%
                </span>
              </div>
              <div className="w-full h-3 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full transition-all"
                  style={{ width: `${comparison.actionOverlap}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:gap-6">
              <div>
                <h4 className="font-semibold text-gray-700 mb-2 lg:mb-3 text-sm lg:text-base">{t('yourActions')}</h4>
                <div className="space-y-1.5 lg:space-y-2">
                  {comparison.userActions.map((actionId) => {
                    const isRecommended = comparison.suggestedActions.some((a) => a.id === actionId);
                    return (
                      <div
                        key={actionId}
                        className={`p-2 rounded-lg text-xs lg:text-sm ${
                          isRecommended ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          {isRecommended && (
                            <svg className="w-3.5 h-3.5 lg:w-4 lg:h-4 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                          <span>{tActions(actionId)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-700 mb-2 lg:mb-3 text-sm lg:text-base">{t('recommendedActions')}</h4>
                <div className="space-y-1.5 lg:space-y-2">
                  {comparison.suggestedActions.map((action) => {
                    const isSelected = comparison.userActions.includes(action.id);
                    return (
                      <div
                        key={action.id}
                        className={`p-2 rounded-lg text-xs lg:text-sm ${
                          isSelected ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 min-w-0 flex-1">
                            {isSelected && (
                              <svg className="w-3.5 h-3.5 lg:w-4 lg:h-4 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                            <span className="truncate">{tActions(action.id)}</span>
                          </div>
                          <Badge variant="outline" className="text-xs ml-2 flex-shrink-0">
                            {Math.round((action.relevanceScore / maxRelevance) * 100)}%
                          </Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Separator />

        <VulnerabilityComparison />

        <div className="flex justify-center gap-4 pt-4">
          <Button
            variant="outline"
            onClick={() => setWorkshopPhase('step2')}
          >
            {t('backToExploration')}
          </Button>
          <Button
            className="bg-purple-600 hover:bg-purple-700"
            onClick={() => setWorkshopPhase('step5')}
          >
            {t('continueToStep5')}
          </Button>
        </div>
      </div>
    </ScrollArea>
  );
}
