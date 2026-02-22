'use client';

import { useState, useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { RankingEntry } from '@/lib/types';
import MapViewer from '@/components/map/MapViewer';
import Sidebar from '@/components/layout/Sidebar';
import MiniRadarChart from './MiniRadarChart';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface Props {
  onSubmit: (ranking: RankingEntry[]) => void;
}

// Sortable ranking card with optional radar chart
function SortableRankingCard({
  entry,
  muni,
  onRemove,
  radarValues,
  purchasedCategories,
}: {
  entry: RankingEntry;
  muni: { code: string; name: string };
  onRemove: (code: string) => void;
  radarValues?: Record<string, number>;
  purchasedCategories?: Set<string>;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: entry.code });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 50 : 'auto',
    opacity: isDragging ? 0.8 : 1,
    touchAction: 'none',
  } as React.CSSProperties;

  const showRadar = !!radarValues;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`
        rounded-lg border bg-white cursor-grab active:cursor-grabbing
        ${isDragging ? 'shadow-lg ring-2 ring-purple-400' : 'shadow-sm border-gray-200'}
        transition-shadow
      `}
    >
      {/* Header row: badge + name + controls */}
      <div className="flex items-center gap-3 px-4 py-3 pointer-events-none">
        <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
          {entry.position}
        </div>
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium text-gray-800 truncate block">
            {muni.name}
          </span>
        </div>
        <div className="p-1 text-gray-300 flex-shrink-0">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 8l5-5 5 5M7 16l5 5 5-5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove(entry.code);
          }}
          className="p-1 text-red-400 hover:text-red-600 transition flex-shrink-0 pointer-events-auto"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>

      {/* Radar chart (only in step2) */}
      {showRadar && (
        <div className="px-2 pb-3 pointer-events-none">
          <MiniRadarChart
            values={radarValues!}
            purchasedCategories={purchasedCategories!}
            size={140}
          />
        </div>
      )}
    </div>
  );
}

export default function Step1View({ onSubmit }: Props) {
  const t = useTranslations('workshopFlow');
  const {
    workshopMunicipalities,
    workshopPhase,
    layers,
    group,
    revisedRanking,
    initialRanking,
  } = useWorkshopStore();
  const [ranking, setRanking] = useState<RankingEntry[]>([]);

  const isStep2OrLater = workshopPhase === 'step2' || workshopPhase === 'step2b';

  // DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  // Determine which categories have purchased layers (only from Step 2)
  const purchasedCategories = useMemo(() => {
    if (!isStep2OrLater || !group || !group.purchasedLayers) return new Set<string>();
    const cats = new Set<string>();
    group.purchasedLayers.forEach((layerId) => {
      const layer = layers.find((l) => l.id === layerId);
      if (layer) cats.add(layer.category);
    });
    return cats;
  }, [group, layers, isStep2OrLater]);

  // Compute normalized values (0-1) for each municipality's riskSummary
  // Only from Step 2 onward — Step 1 has no radar charts
  const normalizedValues = useMemo(() => {
    if (!isStep2OrLater || workshopMunicipalities.length === 0) return {};

    const categories = ['governance', 'biodiversity', 'climate', 'health', 'social'];

    // Find min/max per category across all 10 municipalities
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

    // Normalize each municipality
    const result: Record<string, Record<string, number>> = {};
    workshopMunicipalities.forEach((m) => {
      const normalized: Record<string, number> = {};
      categories.forEach((cat) => {
        const val = m.riskSummary[cat as keyof typeof m.riskSummary];
        const range = maxs[cat] - mins[cat];
        normalized[cat] = range > 0 ? (val - mins[cat]) / range : 0.5;
      });
      result[m.code] = normalized;
    });

    return result;
  }, [isStep2OrLater, workshopMunicipalities]);

  const handleAddToRanking = (code: string) => {
    if (ranking.find((r) => r.code === code)) return;
    if (ranking.length < 10) {
      setRanking([...ranking, { code, position: ranking.length + 1 }]);
    }
  };

  const handleRemove = (code: string) => {
    const newRanking = ranking.filter((r) => r.code !== code);
    newRanking.forEach((r, i) => (r.position = i + 1));
    setRanking(newRanking);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = ranking.findIndex((r) => r.code === active.id);
    const newIndex = ranking.findIndex((r) => r.code === over.id);

    const newRanking = arrayMove(ranking, oldIndex, newIndex);
    newRanking.forEach((r, i) => (r.position = i + 1));
    setRanking(newRanking);
  };

  const handleSubmit = () => {
    if (ranking.length === 10) {
      onSubmit(ranking);
    }
  };

  // In step2b, allow keeping the previous ranking (from step2's revised ranking, or initial)
  const isStep2b = workshopPhase === 'step2b';
  const previousRanking = revisedRanking.length > 0 ? revisedRanking : initialRanking;

  const handleKeepRanking = () => {
    if (previousRanking.length === 10) {
      onSubmit(previousRanking);
    }
  };

  const getMunicipalityByCode = (code: string) =>
    workshopMunicipalities.find((m) => m.code === code);

  const isRanked = (code: string) => ranking.some((r) => r.code === code);

  const unrankedMunicipalities = workshopMunicipalities.filter(
    (m) => !isRanked(m.code)
  );

  // Panel width: wider in step2 to fit radar charts
  const panelWidth = isStep2OrLater ? 'w-[400px]' : 'w-[320px]';

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* LEFT: Municipality ranking list */}
        <div className={`${panelWidth} flex flex-col border-r border-gray-200 bg-gray-50`}>
          <div className="px-4 py-3 border-b border-gray-200 bg-white">
            <h2 className="text-base font-bold text-gray-800">{t('yourPriorityList')}</h2>
            <p className="text-sm text-gray-500">
              {ranking.length}/10 {t('ranked')}
            </p>
          </div>

          <ScrollArea className="flex-1">
            <div className="p-3 space-y-2">
              {/* Ranked municipalities - draggable */}
              {ranking.length > 0 && (
                <DndContext
                  sensors={sensors}
                  collisionDetection={closestCenter}
                  onDragEnd={handleDragEnd}
                >
                  <SortableContext
                    items={ranking.map((r) => r.code)}
                    strategy={verticalListSortingStrategy}
                  >
                    <div className="space-y-2">
                      {ranking.map((entry) => {
                        const muni = getMunicipalityByCode(entry.code);
                        if (!muni) return null;
                        return (
                          <SortableRankingCard
                            key={entry.code}
                            entry={entry}
                            muni={muni}
                            onRemove={handleRemove}
                            radarValues={isStep2OrLater ? normalizedValues[entry.code] : undefined}
                            purchasedCategories={isStep2OrLater ? purchasedCategories : undefined}
                          />
                        );
                      })}
                    </div>
                  </SortableContext>
                </DndContext>
              )}

              {ranking.length === 10 && (
                <div className="p-2.5 bg-green-50 border border-green-200 rounded-lg text-center">
                  <p className="text-sm text-green-700 font-medium">{t('allRanked')}</p>
                </div>
              )}

              {/* Unranked municipalities */}
              {unrankedMunicipalities.length > 0 && (
                <>
                  {ranking.length > 0 && (
                    <div className="border-t border-gray-200 pt-2 mt-1">
                      <p className="text-xs text-gray-400 font-medium mb-2 uppercase tracking-wide">
                        {t('available')}
                      </p>
                    </div>
                  )}
                  <div className="space-y-2">
                    {unrankedMunicipalities.map((muni) => (
                      <div
                        key={muni.code}
                        className={`rounded-lg border border-dashed border-gray-300 bg-white cursor-pointer hover:border-purple-400 hover:shadow-sm transition-all`}
                        onClick={() => handleAddToRanking(muni.code)}
                      >
                        <div className="flex items-center gap-3 px-4 py-3">
                          <div className="w-8 h-8 rounded-full bg-gray-100 text-gray-400 border border-dashed border-gray-300 flex items-center justify-center text-sm flex-shrink-0">
                            +
                          </div>
                          <span className="text-sm font-medium text-gray-700 truncate">
                            {muni.name}
                          </span>
                        </div>
                        {/* Show radar for unranked too in step2 */}
                        {isStep2OrLater && normalizedValues[muni.code] && (
                          <div className="px-2 pb-3">
                            <MiniRadarChart
                              values={normalizedValues[muni.code]}
                              purchasedCategories={purchasedCategories}
                              size={140}
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </ScrollArea>
        </div>

        {/* RIGHT: Map + Sidebar */}
        <div className="flex-1 flex overflow-hidden">
          <main className="flex-1 relative">
            <MapViewer />
          </main>
          <Sidebar />
        </div>
      </div>

      {/* BOTTOM BAR: Legend + Continue button (full width) */}
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

        <div className="flex items-center gap-3">
          {isStep2b && previousRanking.length === 10 && (
            <Button
              variant="outline"
              className="px-6"
              onClick={handleKeepRanking}
            >
              {t('keepRanking')}
            </Button>
          )}
          <Button
            className="bg-purple-600 hover:bg-purple-700 px-6"
            disabled={ranking.length !== 10}
            onClick={handleSubmit}
          >
            {t('continueToRevision')}
          </Button>
        </div>
      </div>
    </div>
  );
}
