import { getMessages } from 'next-intl/server';
import { NextIntlClientProvider } from 'next-intl';
import WorkshopClient from './WorkshopClient';

export default async function WorkshopPage() {
  const messages = await getMessages() as Record<string, unknown>;

  // Load common + categories (used by CreditDisplay, Sidebar, RadarChart) + workshop namespaces
  const pageMessages = {
    common: messages.common,
    categories: messages.categories,
    workshop: messages.workshop,
    workshopFlow: messages.workshopFlow,
    layers: messages.layers,
    purchase: messages.purchase,
    municipality: messages.municipality,
    strategy: messages.strategy,
    layerNames: messages.layerNames,
    layerDescriptions: messages.layerDescriptions,
    radarChart: messages.radarChart,
    bipartiteNetwork: messages.bipartiteNetwork,
    actionNames: messages.actionNames,
    actionDescriptions: messages.actionDescriptions,
  };

  return (
    <NextIntlClientProvider messages={pageMessages}>
      <WorkshopClient />
    </NextIntlClientProvider>
  );
}
