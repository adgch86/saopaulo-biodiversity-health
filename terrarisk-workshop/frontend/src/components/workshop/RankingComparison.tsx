'use client';

import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

export default function RankingComparison() {
  const t = useTranslations('workshopFlow');
  const tActions = useTranslations('actionNames');
  const { comparison, setWorkshopPhase } = useWorkshopStore();

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
      <div className="max-w-7xl mx-auto p-8 space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">{t('phase4Title')}</h1>
          <p className="text-gray-600">{t('phase4Desc')}</p>
        </div>

        <Card className="border-2 border-purple-200">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
            <CardTitle className="text-lg">{t('rankingCorrelation')}</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <div
                  className={`text-5xl font-bold mb-2 ${getCorrelationColor(
                    comparison.rankingCorrelation.spearman
                  )}`}
                >
                  {agreementPercentage}%
                </div>
                <p className="text-sm text-gray-600">
                  Spearman Correlation
                </p>
              </div>
              <div className="text-center border-l border-r border-gray-200">
                <div
                  className={`text-5xl font-bold mb-2 ${getCorrelationColor(
                    comparison.rankingCorrelation.kendall
                  )}`}
                >
                  {Math.round(comparison.rankingCorrelation.kendall * 100)}%
                </div>
                <p className="text-sm text-gray-600">
                  Kendall Tau
                </p>
              </div>
              <div className="text-center">
                <div
                  className={`text-3xl font-bold mb-2 px-4 py-2 rounded-lg inline-block ${getCorrelationBg(
                    comparison.rankingCorrelation.spearman
                  )} ${getCorrelationColor(comparison.rankingCorrelation.spearman)}`}
                >
                  {comparison.rankingCorrelation.spearman > 0.7
                    ? 'High Agreement'
                    : comparison.rankingCorrelation.spearman > 0.4
                    ? 'Moderate Agreement'
                    : 'Low Agreement'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader className="bg-blue-50">
              <CardTitle className="text-lg flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {t('yourRanking')}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-gray-200">
                {comparison.userRanking.map((entry) => (
                  <div key={entry.code} className="flex items-center gap-3 p-4 hover:bg-gray-50">
                    <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                      {entry.position}
                    </div>
                    <span className="text-sm font-medium text-gray-800">{entry.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="bg-purple-50">
              <CardTitle className="text-lg flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                {t('platformRanking')}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-gray-200">
                {comparison.platformRanking.map((entry) => (
                  <div key={entry.code} className="flex items-center gap-3 p-4 hover:bg-gray-50">
                    <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                      {entry.position}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-800">{entry.name}</div>
                      <div className="text-xs text-gray-500">Score: {entry.compositeScore.toFixed(2)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">{t('positionDiff')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {comparison.positionDifferences.map((diff) => (
                <div
                  key={diff.code}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-sm font-medium text-gray-800">{diff.name}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      You: #{diff.userPosition}
                    </Badge>
                    <span className={`font-bold text-lg ${getDiffColor(diff.difference)}`}>
                      {getDiffArrow(diff.difference)}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      Platform: #{diff.platformPosition}
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
            <CardTitle className="text-lg">{t('actionsComparison')}</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">{t('actionOverlap')}</span>
                <span className="text-2xl font-bold text-purple-600">
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

            <div className="grid grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-700 mb-3">{t('yourActions')}</h4>
                <div className="space-y-2">
                  {comparison.userActions.map((actionId) => {
                    const isRecommended = comparison.suggestedActions.some((a) => a.id === actionId);
                    return (
                      <div
                        key={actionId}
                        className={`p-2 rounded-lg text-sm ${
                          isRecommended ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          {isRecommended && (
                            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                <h4 className="font-semibold text-gray-700 mb-3">{t('recommendedActions')}</h4>
                <div className="space-y-2">
                  {comparison.suggestedActions.map((action) => {
                    const isSelected = comparison.userActions.includes(action.id);
                    return (
                      <div
                        key={action.id}
                        className={`p-2 rounded-lg text-sm ${
                          isSelected ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {isSelected && (
                              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                            <span>{tActions(action.id)}</span>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {Math.round(action.relevanceScore * 100)}%
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

        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={() => setWorkshopPhase('explore')}
          >
            {t('backToExploration')}
          </Button>
        </div>
      </div>
    </ScrollArea>
  );
}
