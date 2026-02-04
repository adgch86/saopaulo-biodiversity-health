'use client';

import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import LayerSelector from '@/components/panels/LayerSelector';
import ActiveLayers from '@/components/panels/ActiveLayers';
import MunicipalityInfo from '@/components/panels/MunicipalityInfo';

export default function Sidebar() {
  const t = useTranslations('workshop');
  const { isSidebarOpen, activeTab, setActiveTab } = useWorkshopStore();

  if (!isSidebarOpen) return null;

  return (
    <aside className="w-80 bg-white border-l border-gray-200 flex flex-col overflow-hidden">
      <Tabs
        value={activeTab}
        onValueChange={(v) => setActiveTab(v as typeof activeTab)}
        className="flex-1 flex flex-col"
      >
        <TabsList className="w-full rounded-none border-b bg-gray-50">
          <TabsTrigger value="layers" className="flex-1">
            {t('layers')}
          </TabsTrigger>
          <TabsTrigger value="info" className="flex-1">
            {t('info')}
          </TabsTrigger>
          <TabsTrigger value="strategy" className="flex-1">
            {t('strategy')}
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-hidden">
          <TabsContent value="layers" className="h-full m-0 p-3">
            <div className="space-y-3">
              <LayerSelector />
            </div>
          </TabsContent>

          <TabsContent value="info" className="h-full m-0 p-3">
            <div className="space-y-3">
              <ActiveLayers />
              <MunicipalityInfo />
            </div>
          </TabsContent>

          <TabsContent value="strategy" className="h-full m-0 p-3">
            <StrategyPanel />
          </TabsContent>
        </div>
      </Tabs>
    </aside>
  );
}

function StrategyPanel() {
  const t = useTranslations('strategy');
  const tc = useTranslations('categories');
  const { group, layers } = useWorkshopStore();

  if (!group) return null;

  const purchasedLayers = layers.filter(
    (l) => group.purchasedLayers.includes(l.id) || l.isFree
  );

  // Count by category
  const categoryCounts = purchasedLayers.reduce(
    (acc, layer) => {
      acc[layer.category] = (acc[layer.category] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const totalLayers = layers.length;
  const unlockedLayers = purchasedLayers.length;
  const coverage = Math.round((unlockedLayers / totalLayers) * 100);

  const categories = [
    { key: 'governance', color: 'bg-purple-500' },
    { key: 'biodiversity', color: 'bg-green-500' },
    { key: 'climate', color: 'bg-orange-500' },
    { key: 'health', color: 'bg-red-500' },
    { key: 'social', color: 'bg-blue-500' },
  ];

  return (
    <div className="space-y-4">
      {/* Overall progress */}
      <div className="p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg">
        <h3 className="font-semibold text-gray-800 mb-2">{t('title')}</h3>
        <div className="flex items-end gap-2">
          <span className="text-3xl font-bold text-purple-600">{coverage}%</span>
          <span className="text-sm text-gray-500 mb-1">{t('coverage')}</span>
        </div>
        <div className="w-full h-2 bg-gray-200 rounded-full mt-2">
          <div
            className="h-full bg-gradient-to-r from-purple-400 to-blue-500 rounded-full transition-all"
            style={{ width: `${coverage}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {t('layersUnlocked', { unlocked: unlockedLayers, total: totalLayers })}
        </p>
      </div>

      {/* Category breakdown */}
      <div>
        <h4 className="font-medium text-gray-700 mb-2">{t('byCategory')}</h4>
        <div className="space-y-2">
          {categories.map(({ key, color }) => {
            const count = categoryCounts[key] || 0;
            const total = layers.filter((l) => l.category === key).length;
            const pct = total > 0 ? (count / total) * 100 : 0;

            return (
              <div key={key} className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${color}`} />
                <span className="text-sm text-gray-600 w-24">{tc(key)}</span>
                <div className="flex-1 h-1.5 bg-gray-200 rounded-full">
                  <div
                    className={`h-full rounded-full ${color}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-8">
                  {count}/{total}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tips */}
      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 className="font-medium text-yellow-800 text-sm mb-1">{t('tip')}</h4>
        <p className="text-xs text-yellow-700">{t('tipText')}</p>
      </div>
    </div>
  );
}
