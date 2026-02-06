'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import Header from '@/components/layout/Header';
import Sidebar from '@/components/layout/Sidebar';
import MapViewer from '@/components/map/MapViewer';
import WorkshopStepper from '@/components/workshop/WorkshopStepper';
import MunicipalityRanking from '@/components/workshop/MunicipalityRanking';
import ActionsSelector from '@/components/workshop/ActionsSelector';
import RankingComparison from '@/components/workshop/RankingComparison';
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
  } = useWorkshopStore();
  const [isLoading, setIsLoading] = useState(true);
  const [showPhaseTransition, setShowPhaseTransition] = useState(false);

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

  const handleInitialRanking = async (ranking: RankingEntry[]) => {
    if (!group) return;

    try {
      const response = await fetch('/api/workshop/ranking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groupId: group.id, phase: 'initial', ranking }),
      });

      if (response.ok) {
        setInitialRanking(ranking);
        setShowPhaseTransition(true);
      }
    } catch (error) {
      console.error('Error saving initial ranking:', error);
    }
  };

  const handleRevisedRanking = async (ranking: RankingEntry[]) => {
    if (!group) return;

    try {
      const response = await fetch('/api/workshop/ranking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groupId: group.id, phase: 'revised', ranking }),
      });

      if (response.ok) {
        setRevisedRanking(ranking);
      }
    } catch (error) {
      console.error('Error saving revised ranking:', error);
    }
  };

  const handleActionsSubmit = async (actionIds: string[]) => {
    if (!group) return;

    try {
      // Save selected actions
      await fetch('/api/workshop/actions/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groupId: group.id, selectedActions: actionIds }),
      });

      // Get comparison results
      const compResponse = await fetch(`/api/workshop/comparison/${group.id}`);
      if (compResponse.ok) {
        const comparisonData = await compResponse.json();
        setComparison(comparisonData);
        setWorkshopPhase('results');
      }
    } catch (error) {
      console.error('Error submitting actions:', error);
    }
  };

  const handleContinueToExploration = () => {
    setShowPhaseTransition(false);
    setWorkshopPhase('explore');
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

  if (showPhaseTransition) {
    return (
      <div className="h-screen w-screen flex flex-col overflow-hidden bg-gradient-to-br from-purple-50 to-blue-50">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="max-w-2xl mx-auto text-center p-8">
            <div className="w-20 h-20 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              {tf('phase1Title')}
            </h2>
            <p className="text-gray-600 mb-8">
              {tf('phase2Desc')}
            </p>
            <Button
              size="lg"
              className="bg-purple-600 hover:bg-purple-700"
              onClick={handleContinueToExploration}
            >
              {tf('continueToExploration')}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      <Header />
      <WorkshopStepper />

      {workshopPhase === 'ranking' && (
        <MunicipalityRanking phase="initial" onSubmit={handleInitialRanking} />
      )}

      {workshopPhase === 'explore' && (
        <>
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 relative">
              <MapViewer />
            </main>
            <Sidebar />
          </div>

          <footer className="h-16 bg-white border-t border-gray-200 flex items-center justify-between px-8">
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{t('legend')}:</span>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded" style={{ backgroundColor: '#2E7D32' }} />
                <span className="text-sm text-gray-600">{t('lowRisk')}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded" style={{ backgroundColor: '#FFC107' }} />
                <span className="text-sm text-gray-600">{t('medium')}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded" style={{ backgroundColor: '#C62828' }} />
                <span className="text-sm text-gray-600">{t('highRisk')}</span>
              </div>
            </div>
            <Button
              className="bg-purple-600 hover:bg-purple-700"
              onClick={() => setWorkshopPhase('revised')}
            >
              {tf('continueToRevision')}
            </Button>
          </footer>
        </>
      )}

      {workshopPhase === 'revised' && (
        <div className="flex-1 flex overflow-hidden">
          <div className="w-1/2 overflow-auto">
            <MunicipalityRanking phase="revised" onSubmit={handleRevisedRanking} />
          </div>
          <div className="w-1/2 overflow-auto border-l">
            <ActionsSelector onSubmit={handleActionsSubmit} />
          </div>
        </div>
      )}

      {workshopPhase === 'results' && (
        <div className="flex-1 overflow-auto">
          <RankingComparison />
        </div>
      )}
    </div>
  );
}
