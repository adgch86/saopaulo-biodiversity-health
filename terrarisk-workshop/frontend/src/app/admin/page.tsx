import { getMessages } from 'next-intl/server';
import { NextIntlClientProvider } from 'next-intl';
import AdminClient from './AdminClient';

export default async function AdminPage() {
  const messages = await getMessages() as Record<string, unknown>;

  // Load common (used by AdminClient) + admin and landing namespaces
  const pageMessages = {
    common: messages.common,
    admin: messages.admin,
    landing: messages.landing,
  };

  return (
    <NextIntlClientProvider messages={pageMessages}>
      <AdminClient />
    </NextIntlClientProvider>
  );
}
