'use client';

import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Separator } from '@/components/ui/separator';

export default function ActiveLayers() {
  const t = useTranslations('layers');
  const {
    layers,
    activeLayers,
    toggleLayer,
    layerOpacity,
    setLayerOpacity,
    bivariateMode,
    setBivariateMode,
    setBivariateImageUrl,
  } = useWorkshopStore();

  const activeLayerData = activeLayers
    .map((id) => layers.find((l) => l.id === id))
    .filter(Boolean);

  const handleGenerateBivariate = async () => {
    if (activeLayers.length !== 2) return;

    setBivariateMode(true);
    try {
      const res = await fetch('/api/bivariate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          layer1Id: activeLayers[0],
          layer2Id: activeLayers[1],
        }),
      });
      const data = await res.json();
      setBivariateImageUrl(data.imageUrl);
    } catch (err) {
      console.error('Failed to generate bivariate:', err);
      setBivariateMode(false);
    }
  };

  const handleExitBivariate = () => {
    setBivariateMode(false);
    setBivariateImageUrl(null);
  };

  if (activeLayerData.length === 0) {
    return (
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm">{t('active')}</CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <p className="text-sm text-gray-500 text-center py-4">
            {t('selectLayers')}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <span>{t('activeCount', { count: activeLayerData.length })}</span>
          {bivariateMode && (
            <Button size="sm" variant="outline" onClick={handleExitBivariate}>
              {t('exitBivariate')}
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="py-2 space-y-3">
        {activeLayerData.map((layer) => {
          if (!layer) return null;
          const opacity = layerOpacity[layer.id] ?? 0.75;

          return (
            <div key={layer.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{layer.name}</span>
                <button
                  onClick={() => toggleLayer(layer.id)}
                  className="text-gray-400 hover:text-red-500 transition"
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
              {!bivariateMode && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 w-16">{t('opacity')}</span>
                  <Slider
                    value={[opacity * 100]}
                    onValueChange={([value]) =>
                      setLayerOpacity(layer.id, value / 100)
                    }
                    min={10}
                    max={100}
                    step={5}
                    className="flex-1"
                  />
                  <span className="text-xs text-gray-500 w-8">
                    {Math.round(opacity * 100)}%
                  </span>
                </div>
              )}
            </div>
          );
        })}

        {activeLayerData.length === 2 && !bivariateMode && (
          <>
            <Separator />
            <Button
              className="w-full"
              onClick={handleGenerateBivariate}
              variant="default"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"
                />
              </svg>
              {t('generateBivariate')}
            </Button>
          </>
        )}

        {bivariateMode && (
          <div className="p-3 bg-purple-50 rounded-lg">
            <h4 className="text-sm font-medium text-purple-700 mb-2">
              {t('bivariateMap')}
            </h4>
            <div className="grid grid-cols-2 gap-1 text-xs">
              <div className="flex items-center gap-1">
                <span
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: '#e8e8e8' }}
                />
                {t('lowLow')}
              </div>
              <div className="flex items-center gap-1">
                <span
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: '#73ae80' }}
                />
                {t('lowHigh')}
              </div>
              <div className="flex items-center gap-1">
                <span
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: '#6c83b5' }}
                />
                {t('highLow')}
              </div>
              <div className="flex items-center gap-1">
                <span
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: '#2a5a5b' }}
                />
                {t('highHigh')}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
