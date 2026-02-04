'use client';

import { useRouter } from 'next/navigation';
import { useTransition } from 'react';
import { locales, localeNames, localeFlags, type Locale } from '@/i18n/config';

interface LanguageSelectorProps {
  currentLocale: Locale;
}

export default function LanguageSelector({ currentLocale }: LanguageSelectorProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const handleChange = (newLocale: Locale) => {
    // Set cookie and refresh
    document.cookie = `locale=${newLocale};path=/;max-age=31536000`;
    startTransition(() => {
      router.refresh();
    });
  };

  return (
    <div className="flex items-center gap-1">
      {locales.map((locale) => (
        <button
          key={locale}
          onClick={() => handleChange(locale)}
          disabled={isPending}
          className={`
            px-2 py-1 rounded text-sm transition-all
            ${currentLocale === locale
              ? 'bg-purple-100 text-purple-700 font-medium'
              : 'hover:bg-gray-100 text-gray-600'
            }
            ${isPending ? 'opacity-50 cursor-wait' : ''}
          `}
          title={localeNames[locale]}
        >
          <span className="mr-1">{localeFlags[locale]}</span>
          <span className="hidden sm:inline">{locale.toUpperCase()}</span>
        </button>
      ))}
    </div>
  );
}
