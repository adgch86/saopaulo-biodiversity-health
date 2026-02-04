'use client';

import { useTranslations, useLocale } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import CreditDisplay from '@/components/panels/CreditDisplay';
import LanguageSelector from '@/components/LanguageSelector';
import { Button } from '@/components/ui/button';
import type { Locale } from '@/i18n/config';

export default function Header() {
  const t = useTranslations('workshop');
  const locale = useLocale() as Locale;
  const { group, resetGroup, toggleSidebar, isSidebarOpen } = useWorkshopStore();

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 shadow-sm">
      <div className="flex items-center gap-4">
        {/* Logo and title */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-800">TerraRisk</h1>
            <p className="text-xs text-gray-500 -mt-0.5">Workshop SEMIL-USP</p>
          </div>
        </div>

        {/* Toggle sidebar button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleSidebar}
          className="hidden md:flex"
        >
          <svg
            className={`w-5 h-5 transition-transform ${isSidebarOpen ? '' : 'rotate-180'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
            />
          </svg>
        </Button>
      </div>

      {/* Group info, credits, language */}
      <div className="flex items-center gap-4">
        {group && (
          <>
            <div className="hidden sm:flex items-center gap-2">
              <span className="text-sm text-gray-600">{t('group')}:</span>
              <span className="text-sm font-semibold text-gray-800">
                {group.name}
              </span>
            </div>
            <CreditDisplay />
            <Button
              variant="ghost"
              size="sm"
              onClick={resetGroup}
              className="text-gray-500 hover:text-red-500"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </Button>
          </>
        )}
        <div className="border-l pl-4 ml-2">
          <LanguageSelector currentLocale={locale} />
        </div>
      </div>
    </header>
  );
}
