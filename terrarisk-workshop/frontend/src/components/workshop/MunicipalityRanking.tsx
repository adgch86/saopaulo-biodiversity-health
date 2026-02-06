'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { CATEGORY_CONFIG, type RankingEntry } from '@/lib/types';

interface Props {
  phase: 'initial' | 'revised';
  onSubmit: (ranking: RankingEntry[]) => void;
}

export default function MunicipalityRanking({ phase, onSubmit }: Props) {
  const t = useTranslations('workshopFlow');
  const { workshopMunicipalities, initialRanking, layers, group } = useWorkshopStore();
  const [ranking, setRanking] = useState<RankingEntry[]>(
    phase === 'revised' && initialRanking.length > 0 ? [...initialRanking] : []
  );

  const handleMunicipalityClick = (code: string) => {
    const alreadyRanked = ranking.find((r) => r.code === code);
    if (alreadyRanked) {
      setRanking(ranking.filter((r) => r.code !== code));
    } else if (ranking.length < 10) {
      setRanking([...ranking, { code, position: ranking.length + 1 }]);
    }
  };

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const newRanking = [...ranking];
    [newRanking[index - 1], newRanking[index]] = [newRanking[index], newRanking[index - 1]];
    newRanking.forEach((r, i) => (r.position = i + 1));
    setRanking(newRanking);
  };

  const handleMoveDown = (index: number) => {
    if (index === ranking.length - 1) return;
    const newRanking = [...ranking];
    [newRanking[index], newRanking[index + 1]] = [newRanking[index + 1], newRanking[index]];
    newRanking.forEach((r, i) => (r.position = i + 1));
    setRanking(newRanking);
  };

  const handleRemove = (code: string) => {
    const newRanking = ranking.filter((r) => r.code !== code);
    newRanking.forEach((r, i) => (r.position = i + 1));
    setRanking(newRanking);
  };

  const handleKeepInitial = () => {
    setRanking([...initialRanking]);
  };

  const handleSubmit = () => {
    if (ranking.length === 10) {
      onSubmit(ranking);
    }
  };

  const getMunicipalityByCode = (code: string) => {
    return workshopMunicipalities.find((m) => m.code === code);
  };

  const isRanked = (code: string) => ranking.some((r) => r.code === code);
  const getRankPosition = (code: string) => ranking.find((r) => r.code === code)?.position;

  const purchasedLayerVariables = layers
    .filter((l) => group?.purchasedLayers.includes(l.id) || l.isFree)
    .map((l) => l.variable);

  return (
    <div className="h-full flex flex-col lg:flex-row overflow-hidden bg-gray-50">
      <div className="flex-1 p-4 lg:p-6 overflow-auto">
        <div className="max-w-5xl mx-auto">
          <div className="mb-4 lg:mb-6">
            <h2 className="text-xl lg:text-2xl font-bold text-gray-800 mb-1 lg:mb-2">
              {phase === 'initial' ? t('phase1Title') : t('phase3Title')}
            </h2>
            <p className="text-sm lg:text-base text-gray-600">
              {phase === 'initial' ? t('phase1Desc') : t('phase3Desc')}
            </p>
          </div>

          {/* Mobile: ranking summary bar */}
          <div className="lg:hidden mb-3 flex items-center justify-between bg-white rounded-lg border border-gray-200 p-3">
            <span className="text-sm font-medium text-gray-700">
              {t('yourPriorityList')}: {ranking.length}/10
            </span>
            {ranking.length === 10 && (
              <Button
                size="sm"
                className="bg-purple-600 hover:bg-purple-700"
                onClick={handleSubmit}
              >
                {t('submitRanking')}
              </Button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 lg:gap-4">
            {workshopMunicipalities.map((muni) => {
              const ranked = isRanked(muni.code);
              const position = getRankPosition(muni.code);

              return (
                <Card
                  key={muni.code}
                  className={`cursor-pointer transition-all hover:shadow-lg ${
                    ranked ? 'ring-2 ring-purple-400 shadow-lg' : ''
                  }`}
                  onClick={() => handleMunicipalityClick(muni.code)}
                >
                  <CardContent className="p-3 lg:p-4">
                    <div className="flex items-start justify-between mb-2 lg:mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-base lg:text-lg text-gray-800 truncate">{muni.name}</h3>
                      </div>
                      {ranked && (
                        <div className="w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-sm lg:text-lg flex-shrink-0 ml-2">
                          {position}
                        </div>
                      )}
                    </div>

                    <p className="text-xs lg:text-sm text-gray-600 mb-2 lg:mb-3 line-clamp-3">{muni.description}</p>

                    {phase === 'revised' && purchasedLayerVariables.length > 0 && (
                      <div className="pt-2 border-t border-gray-200">
                        <div className="grid grid-cols-2 gap-1.5 lg:gap-2 text-xs">
                          {Object.entries(muni.riskSummary).map(([category, value]) => {
                            const categoryConfig = CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG];
                            return (
                              <div key={category} className="flex items-center justify-between">
                                <span className="text-gray-600">{categoryConfig.label}:</span>
                                <Badge
                                  variant="outline"
                                  className={`text-xs ${
                                    value > 0.66 ? 'text-red-600' : value > 0.33 ? 'text-yellow-600' : 'text-green-600'
                                  }`}
                                >
                                  {value.toFixed(2)}
                                </Badge>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </div>

      <div className="w-full lg:w-96 bg-white border-t lg:border-t-0 lg:border-l border-gray-200 p-4 lg:p-6 flex flex-col max-h-[40vh] lg:max-h-none">
        <div className="mb-3 lg:mb-4">
          <h3 className="text-base lg:text-lg font-bold text-gray-800 mb-1 lg:mb-2">{t('yourPriorityList')}</h3>
          <p className="text-sm text-gray-600">
            {ranking.length}/10 {t('ranked')}
          </p>
        </div>

        {ranking.length === 0 ? (
          <div className="flex-1 flex items-center justify-center py-4 lg:py-0">
            <p className="text-sm text-gray-400 text-center">{t('noRankingYet')}</p>
          </div>
        ) : (
          <ScrollArea className="flex-1 mb-3 lg:mb-4">
            <div className="space-y-1.5 lg:space-y-2">
              {ranking.map((entry, index) => {
                const muni = getMunicipalityByCode(entry.code);
                if (!muni) return null;

                return (
                  <div
                    key={entry.code}
                    className="flex items-center gap-2 p-2 lg:p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-xs lg:text-sm flex-shrink-0">
                      {entry.position}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs lg:text-sm font-medium text-gray-800 truncate">{muni.name}</div>
                    </div>
                    <div className="flex flex-col gap-0.5 lg:gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMoveUp(index);
                        }}
                        disabled={index === 0}
                        className="p-0.5 lg:p-1 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                        title={t('moveUp')}
                      >
                        <svg className="w-3.5 h-3.5 lg:w-4 lg:h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                        </svg>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMoveDown(index);
                        }}
                        disabled={index === ranking.length - 1}
                        className="p-0.5 lg:p-1 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                        title={t('moveDown')}
                      >
                        <svg className="w-3.5 h-3.5 lg:w-4 lg:h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemove(entry.code);
                      }}
                      className="p-0.5 lg:p-1 hover:bg-red-100 rounded text-red-500"
                      title={t('remove')}
                    >
                      <svg className="w-3.5 h-3.5 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        )}

        {ranking.length === 10 && (
          <div className="mb-2 p-2 lg:p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-xs lg:text-sm text-green-700 font-medium text-center">{t('allRanked')}</p>
          </div>
        )}

        <div className="space-y-2">
          {phase === 'revised' && initialRanking.length > 0 && (
            <Button variant="outline" className="w-full" onClick={handleKeepInitial}>
              {t('keepInitialRanking')}
            </Button>
          )}
          <Button
            className="w-full bg-purple-600 hover:bg-purple-700"
            disabled={ranking.length !== 10}
            onClick={handleSubmit}
          >
            {t('submitRanking')}
          </Button>
        </div>
      </div>
    </div>
  );
}
