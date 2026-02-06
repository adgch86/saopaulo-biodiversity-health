'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface MunicipalityChange {
  code: string;
  name: string;
  initialPosition: number;
  revisedPosition: number;
  positionChange: number;
  changeType: 'promoted' | 'demoted' | 'unchanged';
}

interface PerspectiveData {
  totalPositionChanges: number;
  averagePositionShift: number;
  maxPositionShift: number;
  unchangedCount: number;
  promotions: number;
  demotions: number;
  topThreeChanges: boolean;
  bottomThreeChanges: boolean;
  initialVsRevisedCorrelation: { spearman: number; kendall: number };
  municipalityChanges: MunicipalityChange[];
  convergenceWithPlatform: {
    initialSpearman: number;
    revisedSpearman: number;
    improvement: number;
  };
  dataLayersUsed: number;
  creditsSpent: number;
}

export default function PerspectiveChange() {
  const t = useTranslations('workshopFlow');
  const { group } = useWorkshopStore();

  const [data, setData] = useState<PerspectiveData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!group?.id) return;

    setLoading(true);
    fetch(`/api/workshop/perspective-change/${group.id}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [group?.id]);

  if (loading) {
    return (
      <Card className="mt-8 animate-pulse">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="h-6 bg-gray-200 rounded w-56" />
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-gray-100 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  // No changes = no perspective shift card
  if (data.totalPositionChanges === 0 && data.convergenceWithPlatform.improvement === 0) {
    return null;
  }

  const improvementPositive = data.convergenceWithPlatform.improvement > 0;

  return (
    <Card className="mt-8 border-2 border-blue-200">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
        <CardTitle className="text-lg flex items-center gap-2">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          {t('perspectiveChange')}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 lg:p-6 space-y-4 lg:space-y-6">
        {/* Summary stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 lg:gap-4">
          <div className="text-center p-2.5 lg:p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl lg:text-3xl font-bold text-blue-600">
              {data.totalPositionChanges}
              <span className="text-sm lg:text-lg text-blue-400">/10</span>
            </div>
            <p className="text-xs text-gray-600 mt-1">{t('positionsChanged')}</p>
          </div>
          <div className="text-center p-2.5 lg:p-3 bg-purple-50 rounded-lg">
            <div className="text-2xl lg:text-3xl font-bold text-purple-600">
              {data.averagePositionShift.toFixed(1)}
            </div>
            <p className="text-xs text-gray-600 mt-1">{t('avgShift')}</p>
          </div>
          <div className="text-center p-2.5 lg:p-3 bg-green-50 rounded-lg">
            <div className="text-2xl lg:text-3xl font-bold text-green-600">
              {data.dataLayersUsed}
            </div>
            <p className="text-xs text-gray-600 mt-1">{t('layersExplored')}</p>
          </div>
          <div className="text-center p-2.5 lg:p-3 bg-orange-50 rounded-lg">
            <div className="text-2xl lg:text-3xl font-bold text-orange-600">
              {data.creditsSpent}
            </div>
            <p className="text-xs text-gray-600 mt-1">{t('creditsInvested')}</p>
          </div>
        </div>

        {/* Convergence indicator */}
        <div className={`p-3 lg:p-4 rounded-lg border ${
          improvementPositive
            ? 'bg-green-50 border-green-200'
            : 'bg-blue-50 border-blue-200'
        }`}>
          <div className="flex items-start gap-2.5 lg:gap-3">
            {improvementPositive ? (
              <svg className="w-6 h-6 lg:w-8 lg:h-8 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 lg:w-8 lg:h-8 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            <div>
              <p className={`text-sm lg:text-base font-semibold ${improvementPositive ? 'text-green-800' : 'text-blue-800'}`}>
                {improvementPositive
                  ? t('convergenceImproved', { pct: Math.abs(data.convergenceWithPlatform.improvement).toFixed(1) })
                  : t('convergenceMaintained')
                }
              </p>
              <p className="text-xs lg:text-sm text-gray-600 mt-0.5">
                {t('correlationDetail', {
                  before: (data.convergenceWithPlatform.initialSpearman * 100).toFixed(0),
                  after: (data.convergenceWithPlatform.revisedSpearman * 100).toFixed(0),
                })}
              </p>
            </div>
          </div>
        </div>

        <Separator />

        {/* Detailed changes */}
        <div>
          <h4 className="font-semibold text-gray-700 mb-2 lg:mb-3 text-sm lg:text-base">{t('detailedChanges')}</h4>
          <div className="space-y-1.5 lg:space-y-2">
            {data.municipalityChanges.map((muni) => (
              <div
                key={muni.code}
                className={`flex items-center justify-between p-2 lg:p-3 rounded-lg transition-colors ${
                  muni.changeType === 'unchanged'
                    ? 'bg-gray-50'
                    : muni.changeType === 'promoted'
                    ? 'bg-green-50'
                    : 'bg-red-50'
                }`}
              >
                <span className="text-xs lg:text-sm font-medium text-gray-800 flex-1 min-w-0 truncate">
                  {muni.name}
                </span>
                <div className="flex items-center gap-1 lg:gap-2 ml-2 lg:ml-3">
                  <Badge variant="outline" className="text-xs tabular-nums w-7 lg:w-8 justify-center px-0">
                    #{muni.initialPosition}
                  </Badge>

                  {muni.changeType === 'unchanged' ? (
                    <span className="text-gray-400 w-4 lg:w-5 text-center text-xs">=</span>
                  ) : muni.changeType === 'promoted' ? (
                    <svg className="w-4 h-4 lg:w-5 lg:h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 lg:w-5 lg:h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  )}

                  <Badge variant="outline" className="text-xs tabular-nums w-7 lg:w-8 justify-center px-0">
                    #{muni.revisedPosition}
                  </Badge>

                  {muni.positionChange !== 0 && (
                    <span className={`text-xs font-semibold w-8 lg:w-12 text-right ${
                      muni.changeType === 'promoted' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {muni.positionChange > 0 ? '+' : ''}{muni.positionChange}
                    </span>
                  )}
                  {muni.positionChange === 0 && (
                    <span className="text-xs text-gray-400 w-8 lg:w-12 text-right">-</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Direction summary */}
        <div className="flex flex-wrap gap-3 lg:gap-4 text-xs lg:text-sm">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-green-500" />
            <span className="text-gray-600">{t('promoted')}: {data.promotions}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-red-500" />
            <span className="text-gray-600">{t('demoted')}: {data.demotions}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-gray-300" />
            <span className="text-gray-600">{t('unchangedLabel')}: {data.unchangedCount}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
