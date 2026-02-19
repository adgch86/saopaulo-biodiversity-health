import { getMessages } from 'next-intl/server';
import { NextIntlClientProvider } from 'next-intl';
import LandingClient from './LandingClient';

export default async function LandingPage() {
  const messages = await getMessages() as Record<string, unknown>;

  // Only load landing namespace for this page
  const pageMessages = {
    landing: messages.landing,
  };

  return (
    <NextIntlClientProvider messages={pageMessages}>
      <LandingClient />
    </NextIntlClientProvider>
  );
}
