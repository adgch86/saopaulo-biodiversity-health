'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CATEGORY_CONFIG } from '@/lib/types';

interface Props {
  phase: 'step1' | 'step2' | 'step2b';
  onContinue: () => void;
}

// Gradient colors for ranking position badges (1=green, 10=orange-red)
const POSITION_COLORS = [
  '#16a34a', '#22c55e', '#65a30d', '#a3e635',
  '#eab308', '#f59e0b', '#f97316', '#ef4444',
  '#dc2626', '#b91c1c',
];

export default function GroupComparison({ phase, onContinue }: Props) {
  const t = useTranslations('workshopFlow');
  const { groupComparison, layers } = useWorkshopStore();

  const isStep2 = phase === 'step2' || phase === 'step2b';

  // Build a map of layer_id -> display name
  const layerNameMap = useMemo(() => {
    const map: Record<string, string> = {};
    layers.forEach((l) => { map[l.id] = l.name; });
    return map;
  }, [layers]);

  // For step2: determine which ranking to show (revised if available, else initial)
  // and build a map of initial positions for computing deltas
  type RankingEntry = { code: string; position: number; name: string };

  const { displayRankings, initialPositionMaps } = useMemo(() => {
    if (!groupComparison) return { displayRankings: new Map<string, RankingEntry[] | null>(), initialPositionMaps: new Map<string, Map<string, number>>() };

    const dr = new Map<string, RankingEntry[] | null>();
    const ipm = new Map<string, Map<string, number>>();

    groupComparison.groups.forEach((group) => {
      if (phase === 'step2b' && group.exchangeRanking) {
        dr.set(group.id, group.exchangeRanking);
        // Build revised position map for delta calculation
        if (group.revisedRanking) {
          const posMap = new Map<string, number>();
          group.revisedRanking.forEach((e) => posMap.set(e.code, e.position));
          ipm.set(group.id, posMap);
        }
      } else if (isStep2 && group.revisedRanking) {
        dr.set(group.id, group.revisedRanking);
        // Build initial position map for delta calculation
        if (group.ranking) {
          const posMap = new Map<string, number>();
          group.ranking.forEach((e) => posMap.set(e.code, e.position));
          ipm.set(group.id, posMap);
        }
      } else {
        dr.set(group.id, group.ranking);
      }
    });

    return { displayRankings: dr, initialPositionMaps: ipm };
  }, [groupComparison, isStep2]);

  // Find positions that match across groups (using displayed ranking)
  const positionMatches = useMemo(() => {
    if (!groupComparison) return new Map<string, number>();

    const counts = new Map<string, number>();
    groupComparison.groups.forEach((group) => {
      const ranking = displayRankings.get(group.id);
      if (!ranking) return;
      ranking.forEach((entry) => {
        const key = `${entry.position}-${entry.code}`;
        counts.set(key, (counts.get(key) || 0) + 1);
      });
    });

    return counts;
  }, [groupComparison, displayRankings]);

  // Collect all unique layer IDs across all groups' averageValues
  const allLayerIds = useMemo(() => {
    if (!groupComparison) return [];
    const ids = new Set<string>();
    groupComparison.groups.forEach((g) => Object.keys(g.averageValues).forEach((id) => ids.add(id)));
    return Array.from(ids);
  }, [groupComparison]);

  if (!groupComparison) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">{t('loadingComparison')}</p>
        </div>
      </div>
    );
  }

  const { groups, totalGroups } = groupComparison;
  const groupsWithRanking = groups.filter((g) => displayRankings.get(g.id) !== null);

  return (
    <div className="flex-1 overflow-auto bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">{t('groupComparison')}</h2>
          <p className="text-gray-600">
            {totalGroups} {totalGroups === 1 ? 'grupo' : 'grupos'} participando
          </p>
        </div>

        {/* Credits summary table */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">{t('creditsSummary')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-3 font-semibold text-gray-700">Grupo</th>
                    <th className="text-center py-2 px-3 font-semibold text-gray-700">{t('creditsSummary')}</th>
                    <th className="text-center py-2 px-3 font-semibold text-gray-700">{t('layersPurchased')}</th>
                    {Object.keys(CATEGORY_CONFIG).map((cat) => (
                      <th key={cat} className="text-center py-2 px-3 font-semibold" style={{ color: CATEGORY_CONFIG[cat as keyof typeof CATEGORY_CONFIG].color }}>
                        {CATEGORY_CONFIG[cat as keyof typeof CATEGORY_CONFIG].label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {groups.map((group) => (
                    <tr key={group.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-2.5 px-3 font-medium text-gray-800">{group.name}</td>
                      <td className="py-2.5 px-3 text-center">
                        <span className="text-gray-600">{group.credits}</span>
                        <span className="text-gray-400 mx-1">/</span>
                        <span className="text-purple-600 font-medium">{group.creditsSpent} gastados</span>
                      </td>
                      <td className="py-2.5 px-3 text-center">
                        <Badge variant="outline">{group.purchasedLayers?.length ?? 0}</Badge>
                      </td>
                      {Object.keys(CATEGORY_CONFIG).map((cat) => (
                        <td key={cat} className="py-2.5 px-3 text-center">
                          <span className={`font-medium ${
                            (group.layersByCategory[cat] || 0) > 0 ? 'text-gray-800' : 'text-gray-300'
                          }`}>
                            {group.layersByCategory[cat] || 0}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Rankings comparison */}
        {groupsWithRanking.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">Rankings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {groupsWithRanking.map((group) => {
                  const ranking = displayRankings.get(group.id);
                  if (!ranking) return null;
                  const initialPosMap = initialPositionMaps.get(group.id);

                  return (
                    <div key={group.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <h4 className="font-semibold text-sm text-gray-800 mb-3">{group.name}</h4>
                      <div className="space-y-1.5">
                        {ranking.map((entry) => {
                          const matchKey = `${entry.position}-${entry.code}`;
                          const matchCount = positionMatches.get(matchKey) || 0;
                          const isHighlighted = matchCount >= 2;

                          // Position change arrow (only in step2 with initial data)
                          let delta = 0;
                          if (isStep2 && initialPosMap) {
                            const oldPos = initialPosMap.get(entry.code);
                            if (oldPos !== undefined) {
                              delta = oldPos - entry.position; // positive = moved up
                            }
                          }

                          return (
                            <div
                              key={entry.code}
                              className={`flex items-center gap-2 text-sm px-2 py-1 rounded-md transition-colors ${
                                isHighlighted
                                  ? 'bg-green-100 border border-green-300'
                                  : ''
                              }`}
                            >
                              <span
                                className="w-6 h-6 rounded-full text-white flex items-center justify-center text-xs font-bold flex-shrink-0"
                                style={{ backgroundColor: POSITION_COLORS[entry.position - 1] || '#7c3aed' }}
                              >
                                {entry.position}
                              </span>
                              <span className={`truncate ${isHighlighted ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
                                {entry.name}
                              </span>
                              {/* Position change indicator (step2 only) */}
                              {isStep2 && delta !== 0 && (
                                <span className={`ml-auto flex items-center gap-0.5 text-xs font-semibold flex-shrink-0 ${
                                  delta > 0 ? 'text-green-600' : 'text-red-500'
                                }`}>
                                  {delta > 0 ? (
                                    <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                                      <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                                    </svg>
                                  ) : (
                                    <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                                    </svg>
                                  )}
                                  {Math.abs(delta)}
                                </span>
                              )}
                              {isHighlighted && (
                                <span className={`${isStep2 && delta !== 0 ? '' : 'ml-auto'} text-[10px] font-medium text-green-700 bg-green-200 px-1.5 py-0.5 rounded-full flex-shrink-0`}>
                                  {matchCount}x
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Average values */}
        {allLayerIds.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">{t('averageValues')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 px-3 font-semibold text-gray-700">Grupo</th>
                      {allLayerIds.map((layerId) => (
                        <th key={layerId} className="text-center py-2 px-2 font-semibold text-gray-600 text-xs">
                          {layerNameMap[layerId] || layerId.replace(/_/g, ' ')}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {groups.map((group) => (
                      <tr key={group.id} className="border-b border-gray-100">
                        <td className="py-2 px-3 font-medium text-gray-800">{group.name}</td>
                        {allLayerIds.map((layerId) => (
                          <td key={layerId} className="py-2 px-2 text-center text-xs text-gray-700">
                            {group.averageValues[layerId] !== undefined
                              ? group.averageValues[layerId].toFixed(1)
                              : ''}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Continue button */}
        <div className="text-center pb-4">
          <Button
            size="lg"
            className="bg-purple-600 hover:bg-purple-700"
            onClick={onContinue}
          >
            {isStep2 ? t('continueToStep3') : t('continueToStep2')}
          </Button>
        </div>
      </div>
    </div>
  );
}
