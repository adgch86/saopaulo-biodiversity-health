// Shared i18n constants - can be used in client and server components

export const locales = ['pt', 'es', 'en'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'pt'; // Default to Portuguese for Brazil

export const localeNames: Record<Locale, string> = {
  pt: 'Português',
  es: 'Español',
  en: 'English',
};

export const localeFlags: Record<Locale, string> = {
  pt: '🇧🇷',
  es: '🇪🇸',
  en: '🇺🇸',
};
