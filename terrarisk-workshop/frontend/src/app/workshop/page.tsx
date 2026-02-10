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
import { Button } from '@/components/ui/button';
import type { RankingEntry } from '@/lib/types';

export default function WorkshopPage() {
  const t = useTranslations('workshop');
  const tf = useTranslations('workshopFlow');
  const router = useRouter();
  const {
    group,
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
  } = useWorkshopStore();
  const [isLoading, setIsLoading] = useState(true);

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

    Promise.all([
      fetch('/api/layers').then((res) => res.json()),
      fetch('/api/municipalities').then((res) => res.json()),
      fetch('/api/workshop/municipalities').then((res) => res.json()),
      fetch('/api/workshop/actions').then((res) => res.json()),
    ])
      .then(([layersData, municipalitiesData, workshopMunis, actions]) => {
        setLayers(layersData);
        setMunicipalities(municipalitiesData);
        setWorkshopMunicipalities(workshopMunis);
        setPearcActions(actions);
      })
      .catch(console.error);
  }, [group, setLayers, setMunicipalities, setWorkshopMunicipalities, setPearcActions]);

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
        <GroupComparison phase="step2" onContinue={() => setWorkshopPhase('step3')} />
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

      {/* Step 5: Perspective change */}
      {workshopPhase === 'step5' && (
        <div className="flex-1 overflow-auto">
          <div className="max-w-4xl mx-auto p-4 lg:p-8 space-y-6 lg:space-y-8">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-800 mb-1 lg:mb-2">{tf('step5Title')}</h1>
              <p className="text-sm lg:text-base text-gray-600">{tf('step5Desc')}</p>
            </div>
            <PerspectiveChange />
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
