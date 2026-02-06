'use client';

import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { PHASE_CONFIG, type WorkshopPhase } from '@/lib/types';

export default function WorkshopStepper() {
  const t = useTranslations('workshopFlow');
  const { workshopPhase, setWorkshopPhase, initialRanking } = useWorkshopStore();

  const phases: Array<{ key: WorkshopPhase; title: string }> = [
    { key: 'ranking', title: t('phase1Title') },
    { key: 'explore', title: t('phase2Title') },
    { key: 'revised', title: t('phase3Title') },
    { key: 'results', title: t('phase4Title') },
  ];

  const currentPhaseIndex = phases.findIndex((p) => p.key === workshopPhase);

  const handlePhaseClick = (phase: WorkshopPhase, index: number) => {
    if (index <= currentPhaseIndex) {
      setWorkshopPhase(phase);
    }
  };

  return (
    <div className="h-16 bg-white border-b border-gray-200 flex items-center px-8">
      <div className="flex items-center justify-between w-full max-w-6xl mx-auto">
        {phases.map((phase, index) => {
          const isActive = phase.key === workshopPhase;
          const isCompleted = index < currentPhaseIndex;
          const isUpcoming = index > currentPhaseIndex;
          const canClick = index <= currentPhaseIndex && initialRanking.length > 0;

          return (
            <div key={phase.key} className="flex items-center flex-1">
              <button
                onClick={() => handlePhaseClick(phase.key, index)}
                disabled={!canClick}
                className={`flex items-center gap-3 transition-all ${
                  canClick ? 'cursor-pointer' : 'cursor-not-allowed'
                }`}
              >
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all
                    ${isActive ? 'bg-purple-600 text-white ring-4 ring-purple-200' : ''}
                    ${isCompleted ? 'bg-green-600 text-white' : ''}
                    ${isUpcoming ? 'bg-gray-200 text-gray-500' : ''}
                  `}
                >
                  {isCompleted ? (
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={3}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    PHASE_CONFIG[phase.key].icon
                  )}
                </div>
                <div className="text-left">
                  <div
                    className={`text-sm font-semibold ${
                      isActive ? 'text-purple-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}
                  >
                    {phase.title.split(':')[0]}
                  </div>
                  <div className="text-xs text-gray-500">
                    {phase.title.split(':')[1]?.trim()}
                  </div>
                </div>
              </button>
              {index < phases.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-4 transition-all ${
                    index < currentPhaseIndex ? 'bg-green-600' : 'bg-gray-300'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
