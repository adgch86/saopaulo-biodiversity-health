'use client';

import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';

export default function CreditDisplay() {
  const t = useTranslations('common');
  const { group, creditAnimation } = useWorkshopStore();

  if (!group) return null;

  const maxCredits = 10;
  const percentage = (group.credits / maxCredits) * 100;

  return (
    <div className="flex items-center gap-3">
      {/* Credit icon */}
      <div
        className={`
          relative flex items-center justify-center w-8 h-8
          bg-gradient-to-br from-purple-500 to-purple-700
          rounded-full shadow-lg
          ${creditAnimation ? 'animate-bounce' : ''}
        `}
      >
        <svg
          className="w-5 h-5 text-white"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
        </svg>
        {creditAnimation && (
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-ping" />
        )}
      </div>

      {/* Credit bar and count */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span
            className={`
              text-lg font-bold text-purple-700
              ${creditAnimation ? 'scale-110 transition-transform' : 'transition-transform'}
            `}
          >
            {group.credits}
          </span>
          <span className="text-sm text-gray-500">{t('credits')}</span>
        </div>
        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}
