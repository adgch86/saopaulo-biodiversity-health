'use client';

import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import type { WorkshopPhase } from '@/lib/types';

// Map each phase to its visual step (1-7)
const PHASE_TO_STEP: Record<WorkshopPhase, number> = {
  step1: 1,
  step1_results: 1,
  step2: 2,
  step2_results: 2,
  step2b: 3,
  step2b_results: 3,
  step3: 4,
  step4: 5,
  step5: 6,
  survey: 7,
};

export default function WorkshopStepper() {
  const t = useTranslations('workshopFlow');
  const { workshopPhase, setWorkshopPhase, initialRanking } = useWorkshopStore();

  const steps: Array<{ step: number; title: string; phases: WorkshopPhase[] }> = [
    { step: 1, title: t('step1Title'), phases: ['step1', 'step1_results'] },
    { step: 2, title: t('step2Title'), phases: ['step2', 'step2_results'] },
    { step: 3, title: t('step2bTitle'), phases: ['step2b', 'step2b_results'] },
    { step: 4, title: t('step3Title'), phases: ['step3'] },
    { step: 5, title: t('step4Title'), phases: ['step4'] },
    { step: 6, title: t('step5Title'), phases: ['step5'] },
    { step: 7, title: t('surveyTitle'), phases: ['survey'] },
  ];

  const currentStep = PHASE_TO_STEP[workshopPhase];

  const handleStepClick = (step: typeof steps[number]) => {
    if (step.step <= currentStep && initialRanking.length > 0) {
      setWorkshopPhase(step.phases[0]);
    }
  };

  return (
    <div className="h-16 bg-white border-b border-gray-200 flex items-center px-8">
      <div className="flex items-center justify-between w-full max-w-6xl mx-auto">
        {steps.map((step, index) => {
          const isActive = step.step === currentStep;
          const isCompleted = step.step < currentStep;
          const isUpcoming = step.step > currentStep;
          const canClick = step.step <= currentStep && initialRanking.length > 0;

          return (
            <div key={step.step} className="flex items-center flex-1">
              <button
                onClick={() => handleStepClick(step)}
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
                    step.step === 3 ? '2b' : step.step
                  )}
                </div>
                <div className="text-left">
                  <div
                    className={`text-sm font-semibold ${
                      isActive ? 'text-purple-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}
                  >
                    {step.title.split(':')[0]}
                  </div>
                  <div className="text-xs text-gray-500">
                    {step.title.split(':')[1]?.trim()}
                  </div>
                </div>
              </button>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-4 transition-all ${
                    step.step < currentStep ? 'bg-green-600' : 'bg-gray-300'
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
