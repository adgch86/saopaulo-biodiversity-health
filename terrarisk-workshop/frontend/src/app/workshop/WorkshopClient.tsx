'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import Header from '@/components/layout/Header';
import WorkshopStepper from '@/components/workshop/WorkshopStepper';
import Step1View from '@/components/workshop/Step1View';
import GroupComparison from '@/components/workshop/GroupComparison';
import Step3View from '@/components/workshop/Step3View';
import RankingComparison from '@/components/workshop/RankingComparison';
import PerspectiveChange from '@/components/workshop/PerspectiveChange';
import type { PerspectiveData } from '@/components/workshop/PerspectiveChange';
import { Button } from '@/components/ui/button';
import type { RankingEntry } from '@/lib/types';

export default function WorkshopClient() {
  const t = useTranslations('workshop');
  const tf = useTranslations('workshopFlow');
  const router = useRouter();
  const {
    group,
    setGroup,
    workshopPhase,
    setWorkshopPhase,
    setLayers,
    setMunicipalities,
    setWorkshopMunicipalities,
    setPearcActions,
    setInitialRanking,
    setRevisedRanking,
    setComparison,
    setGroupComparison,
    setExchangeRanking,
  } = useWorkshopStore();
  const [isLoading, setIsLoading] = useState(true);
  const [perspectiveData, setPerspectiveData] = useState<PerspectiveData | null>(null);
  const [perspectiveLoading, setPerspectiveLoading] = useState(false);

  // Redirect if no group
  useEffect(() => {
    if (!group) {
      router.push('/');
      return;
    }
    setIsLoading(false);
  }, [group, router]);

  // Load data on mount
  useEffect(() => {
    if (!group) return;

    const safeFetch = (url: string) =>
      fetch(url).then((res) => {
        if (!res.ok) throw new Error(`${url} returned ${res.status}`);
        return res.json();
      });

    Promise.all([
      safeFetch('/api/layers'),
      safeFetch('/api/municipalities'),
      safeFetch('/api/workshop/municipalities'),
      safeFetch('/api/workshop/actions'),
    ])
      .then(([layersData, municipalitiesData, workshopMunis, actions]) => {
        setLayers(layersData);
        setMunicipalities(municipalitiesData);
        setWorkshopMunicipalities(workshopMunis);
        setPearcActions(actions);
      })
      .catch(console.error);
  }, [group, setLayers, setMunicipalities, setWorkshopMunicipalities, setPearcActions]);

  // Reset credits to 10 when entering step2 so group gets a fresh round
  useEffect(() => {
    if (workshopPhase === 'step2' && group?.id) {
      fetch(`/api/groups/${group.id}/reset-credits`, { method: 'POST' })
        .then((res) => {
          if (!res.ok) throw new Error(`Reset credits failed: ${res.status}`);
          return res.json();
        })
        .then((freshGroup) => {
          if (freshGroup?.id && freshGroup?.purchasedLayers) {
            setGroup(freshGroup);
          }
        })
        .catch(console.error);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workshopPhase, group?.id, setGroup]);

  // Fullscreen shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'f' || e.key === 'F') {
        const map = document.querySelector('.leaflet-container');
        if (map && !document.fullscreenElement) {
          map.requestFullscreen?.();
        } else if (document.fullscreenElement) {
          document.exitFullscreen?.();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Fetch perspective change data when entering step5
  useEffect(() => {
    if (workshopPhase !== 'step5' || !group?.id) return;

    setPerspectiveLoading(true);
    fetch(`/api/workshop/perspective-change/${group.id}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setPerspectiveData)
      .catch(() => setPerspectiveData(null))
      .finally(() => setPerspectiveLoading(false));
  }, [workshopPhase, group?.id]);

  const handleStep1Ranking = async (ranking: RankingEntry[]) => {
    if (!group) return;

    try {
      const response = await fetch('/api/workshop/ranking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groupId: group.id, phase: 'initial', ranking }),
      });

      if (response.ok) {
        setInitialRanking(ranking);

        // Fetch group comparison data
        try {
          const compResponse = await fetch('/api/workshop/group-comparison');
          if (compResponse.ok) {
            const compData = await compResponse.json();
            setGroupComparison(compData);
          }
        } catch (error) {
          console.error('Error fetching group comparison:', error);
        }

        setWorkshopPhase('step1_results');
      }
    } catch (error) {
      console.error('Error saving initial ranking:', error);
    }
  };

  const handleStep2Ranking = async (ranking: RankingEntry[]) => {
    if (!group) return;

    try {
      const response = await fetch('/api/workshop/ranking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groupId: group.id, phase: 'revised', ranking }),
      });

      if (response.ok) {
        setRevisedRanking(ranking);

        // Fetch group comparison data for step2_results
        try {
          const compResponse = await fetch('/api/workshop/group-comparison');
          if (compResponse.ok) {
            const compData = await compResponse.json();
            setGroupComparison(compData);
          }
        } catch (error) {
          console.error('Error fetching group comparison:', error);
        }

        setWorkshopPhase('step2_results');
      }
    } catch (error) {
      console.error('Error saving revised ranking:', error);
    }
  };

  const handleStep2bRanking = async (ranking: RankingEntry[]) => {
    if (!group) return;

    try {
      const response = await fetch('/api/workshop/ranking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groupId: group.id, phase: 'exchange', ranking }),
      });

      if (response.ok) {
        setExchangeRanking(ranking);

        // Fetch group comparison data for step2b_results
        try {
          const compResponse = await fetch('/api/workshop/group-comparison');
          if (compResponse.ok) {
            const compData = await compResponse.json();
            setGroupComparison(compData);
          }
        } catch (error) {
          console.error('Error fetching group comparison:', error);
        }

        setWorkshopPhase('step2b_results');
      }
    } catch (error) {
      console.error('Error saving exchange ranking:', error);
    }
  };

  const handleActionsSubmit = async (actionIds: string[]) => {
    if (!group) return;

    try {
      await fetch('/api/workshop/actions/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groupId: group.id, selectedActions: actionIds }),
      });

      const compResponse = await fetch(`/api/workshop/comparison/${group.id}`);
      if (compResponse.ok) {
        const comparisonData = await compResponse.json();
        setComparison(comparisonData);
        setWorkshopPhase('step4');
      }
    } catch (error) {
      console.error('Error submitting actions:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">{t('loadingWorkshop')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      <Header />
      <WorkshopStepper />

      {/* Step 1: Combined ranking + map */}
      {workshopPhase === 'step1' && (
        <Step1View onSubmit={handleStep1Ranking} />
      )}

      {/* Step 1 Results: Group comparison */}
      {workshopPhase === 'step1_results' && (
        <GroupComparison phase="step1" onContinue={() => setWorkshopPhase('step2')} />
      )}

      {/* Step 2: Second round - same layout as step 1 */}
      {workshopPhase === 'step2' && (
        <Step1View onSubmit={handleStep2Ranking} />
      )}

      {/* Step 2 Results: Group comparison with changes */}
      {workshopPhase === 'step2_results' && (
        <GroupComparison phase="step2" onContinue={() => setWorkshopPhase('step2b')} />
      )}

      {/* Step 2b: Exchange round - same layout, NO credit reset */}
      {workshopPhase === 'step2b' && (
        <Step1View onSubmit={handleStep2bRanking} />
      )}

      {/* Step 2b Results: Group comparison after exchange */}
      {workshopPhase === 'step2b_results' && (
        <GroupComparison phase="step2b" onContinue={() => setWorkshopPhase('step3')} />
      )}

      {/* Step 3: PEARC Network + Map + Actions */}
      {workshopPhase === 'step3' && (
        <Step3View onSubmit={handleActionsSubmit} />
      )}

      {/* Step 4: Ranking TerraRisk + actions comparison */}
      {workshopPhase === 'step4' && (
        <div className="flex-1 overflow-hidden">
          <RankingComparison />
        </div>
      )}

      {/* Step 5: Perspective change — two moments */}
      {workshopPhase === 'step5' && (
        <div className="flex-1 overflow-auto">
          <div className="max-w-4xl mx-auto p-4 lg:p-8 space-y-6 lg:space-y-8">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-800 mb-1 lg:mb-2">{tf('step5Title')}</h1>
              <p className="text-sm lg:text-base text-gray-600">{tf('step5Desc')}</p>
            </div>

            {perspectiveLoading && (
              <div className="animate-pulse space-y-4">
                {[1, 2].map((i) => (
                  <div key={i} className="h-48 bg-gray-100 rounded-lg" />
                ))}
              </div>
            )}

            {!perspectiveLoading && perspectiveData && (
              <>
                {/* 3-point progression summary */}
                <div className="p-4 lg:p-6 rounded-xl bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 border border-blue-200">
                  <h3 className="text-sm font-semibold text-gray-600 mb-3">{tf('progressionTitle') || 'Progressão de Convergência'}</h3>
                  <div className="flex items-center justify-center gap-2 lg:gap-4">
                    {/* Initial */}
                    <div className="text-center">
                      <div className="text-2xl lg:text-3xl font-bold text-gray-500">
                        {(perspectiveData.moment1.convergenceWithPlatform.initialSpearman * 100).toFixed(0)}%
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{tf('progressionInitial') || 'Inicial'}</p>
                    </div>
                    {/* Arrow 1 */}
                    <div className="flex flex-col items-center">
                      <svg className="w-6 h-6 lg:w-8 lg:h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                      <span className="text-xs text-blue-600 font-medium">{tf('progressionAfterData') || 'Dados'}</span>
                    </div>
                    {/* After data */}
                    <div className="text-center">
                      <div className="text-2xl lg:text-3xl font-bold text-blue-600">
                        {(perspectiveData.moment1.convergenceWithPlatform.revisedSpearman * 100).toFixed(0)}%
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{tf('progressionRevised') || 'Pós-dados'}</p>
                    </div>
                    {/* Arrow 2 (only if moment2 exists) */}
                    {perspectiveData.moment2 && (
                      <>
                        <div className="flex flex-col items-center">
                          <svg className="w-6 h-6 lg:w-8 lg:h-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                          </svg>
                          <span className="text-xs text-purple-600 font-medium">{tf('progressionAfterExchange') || 'Troca'}</span>
                        </div>
                        {/* After exchange */}
                        <div className="text-center">
                          <div className={`text-2xl lg:text-3xl font-bold ${
                            perspectiveData.moment2.convergenceWithPlatform.revisedSpearman >= perspectiveData.moment1.convergenceWithPlatform.revisedSpearman
                              ? 'text-green-600' : 'text-orange-600'
                          }`}>
                            {(perspectiveData.moment2.convergenceWithPlatform.revisedSpearman * 100).toFixed(0)}%
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{tf('progressionFinal') || 'Pós-troca'}</p>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Moment 1: Post-data (initial → revised) */}
                <PerspectiveChange
                  data={perspectiveData.moment1}
                  title={tf('moment1Title')}
                  subtitle={tf('moment1Subtitle')}
                  icon="data"
                  extraStats={{
                    layersUsed: perspectiveData.dataLayersUsed,
                    creditsSpent: perspectiveData.creditsSpent,
                  }}
                />

                {/* Moment 2: Post-exchange (revised → exchange) */}
                {perspectiveData.moment2 && (
                  <PerspectiveChange
                    data={perspectiveData.moment2}
                    title={tf('moment2Title')}
                    subtitle={tf('moment2Subtitle')}
                    icon="group"
                  />
                )}
              </>
            )}

            <div className="flex justify-center pt-4 pb-8">
              <Button variant="outline" onClick={() => setWorkshopPhase('step4')}>
                {tf('backToExploration')}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
