'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import Header from '@/components/layout/Header';
import Sidebar from '@/components/layout/Sidebar';
import MapViewer from '@/components/map/MapViewer';

export default function WorkshopPage() {
  const t = useTranslations('workshop');
  const router = useRouter();
  const { group, setLayers, setMunicipalities } = useWorkshopStore();
  const [isLoading, setIsLoading] = useState(true);

  // Redirect if no group
  useEffect(() => {
    if (!group) {
      router.push('/');
      return;
    }
    setIsLoading(false);
  }, [group, router]);

  // Load layers and municipalities
  useEffect(() => {
    if (!group) return;

    Promise.all([
      fetch('/api/layers').then((res) => res.json()),
      fetch('/api/municipalities').then((res) => res.json()),
    ])
      .then(([layersData, municipalitiesData]) => {
        setLayers(layersData);
        setMunicipalities(municipalitiesData);
      })
      .catch(console.error);
  }, [group, setLayers, setMunicipalities]);

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
      <div className="flex-1 flex overflow-hidden">
        <main className="flex-1 relative">
          <MapViewer />
        </main>
        <Sidebar />
      </div>

      {/* Footer legend */}
      <footer className="h-8 bg-white border-t border-gray-200 flex items-center justify-between px-4 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>{t('legend')}:</span>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded" style={{ backgroundColor: '#2E7D32' }} />
            <span>{t('lowRisk')}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded" style={{ backgroundColor: '#FFC107' }} />
            <span>{t('medium')}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded" style={{ backgroundColor: '#C62828' }} />
            <span>{t('highRisk')}</span>
          </div>
        </div>
        <div>
          {t('source')} | {t('fullscreenHint')}
        </div>
      </footer>
    </div>
  );
}
