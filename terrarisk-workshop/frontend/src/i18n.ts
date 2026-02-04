import { getRequestConfig } from 'next-intl/server';
import { cookies } from 'next/headers';
import { locales, defaultLocale, type Locale } from './i18n/config';

export default getRequestConfig(async () => {
  // Get locale from cookie or use default
  const cookieStore = await cookies();
  const localeCookie = cookieStore.get('locale')?.value;
  const locale = (locales.includes(localeCookie as Locale) ? localeCookie : defaultLocale) as Locale;

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});

// Re-export from config for convenience
export { locales, defaultLocale, localeNames, localeFlags, type Locale } from './i18n/config';
