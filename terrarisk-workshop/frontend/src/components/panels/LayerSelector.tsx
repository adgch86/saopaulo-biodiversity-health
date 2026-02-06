'use client';

import { useState } from 'react';
import { useWorkshopStore } from '@/lib/store';
import { CATEGORY_CONFIG, type LayerCategory } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

export default function LayerSelector() {
  const { layers, group, activeLayers, toggleLayer, purchaseLayer } =
    useWorkshopStore();
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(['governance', 'climate'])
  );
  const [purchaseDialogLayer, setPurchaseDialogLayer] = useState<string | null>(
    null
  );
  const [isPurchasing, setIsPurchasing] = useState(false);

  const toggleCategory = (category: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  const layersByCategory = layers.reduce(
    (acc, layer) => {
      if (!acc[layer.category]) {
        acc[layer.category] = [];
      }
      acc[layer.category].push(layer);
      return acc;
    },
    {} as Record<LayerCategory, typeof layers>
  );

  const isLayerUnlocked = (layerId: string) => {
    const layer = layers.find((l) => l.id === layerId);
    if (!layer) return false;
    if (layer.isFree) return true;
    return group?.purchasedLayers.includes(layerId) ?? false;
  };

  const handleLayerClick = (layerId: string) => {
    console.log('[LayerSelector] Click on layer:', layerId);
    console.log('[LayerSelector] isUnlocked:', isLayerUnlocked(layerId));
    if (isLayerUnlocked(layerId)) {
      toggleLayer(layerId);
    } else {
      console.log('[LayerSelector] Opening purchase dialog for:', layerId);
      setPurchaseDialogLayer(layerId);
    }
  };

  const handlePurchase = async () => {
    if (!purchaseDialogLayer) return;
    setIsPurchasing(true);
    const success = await purchaseLayer(purchaseDialogLayer);
    setIsPurchasing(false);
    if (success) {
      setPurchaseDialogLayer(null);
      toggleLayer(purchaseDialogLayer);
    }
  };

  const purchaseLayer_ = layers.find((l) => l.id === purchaseDialogLayer);

  return (
    <>
      <ScrollArea className="h-[calc(100vh-280px)]">
        <div className="space-y-2 pr-4">
          {(Object.keys(CATEGORY_CONFIG) as LayerCategory[]).map((category) => {
            const config = CATEGORY_CONFIG[category];
            const categoryLayers = layersByCategory[category] || [];
            const isExpanded = expandedCategories.has(category);
            const unlockedCount = categoryLayers.filter((l) =>
              isLayerUnlocked(l.id)
            ).length;

            return (
              <Card key={category} className="overflow-hidden">
                <CardHeader
                  className={`py-2 px-3 cursor-pointer ${config.bgColor} hover:opacity-90 transition`}
                  onClick={() => toggleCategory(category)}
                >
                  <CardTitle className="text-sm flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <span
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: config.color }}
                      />
                      {config.label}
                    </span>
                    <span className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {unlockedCount}/{categoryLayers.length}
                      </Badge>
                      <svg
                        className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </span>
                  </CardTitle>
                </CardHeader>
                {isExpanded && (
                  <CardContent className="p-2 space-y-1">
                    {categoryLayers.map((layer) => {
                      const isUnlocked = isLayerUnlocked(layer.id);
                      const isActive = activeLayers.includes(layer.id);

                      return (
                        <div
                          key={layer.id}
                          className={`
                            p-2 rounded-md cursor-pointer transition-all
                            ${isActive ? 'bg-purple-100 ring-2 ring-purple-400' : 'hover:bg-gray-50'}
                            ${!isUnlocked ? 'opacity-75' : ''}
                          `}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleLayerClick(layer.id);
                          }}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {isUnlocked ? (
                                <div
                                  className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                                    isActive
                                      ? 'bg-purple-500 border-purple-500'
                                      : 'border-gray-300'
                                  }`}
                                >
                                  {isActive && (
                                    <svg
                                      className="w-3 h-3 text-white"
                                      fill="none"
                                      stroke="currentColor"
                                      viewBox="0 0 24 24"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={3}
                                        d="M5 13l4 4L19 7"
                                      />
                                    </svg>
                                  )}
                                </div>
                              ) : (
                                <svg
                                  className="w-4 h-4 text-gray-400"
                                  fill="none"
                                  stroke="currentColor"
                                  viewBox="0 0 24 24"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                  />
                                </svg>
                              )}
                              <span className="text-sm font-medium">
                                {layer.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              {layer.isFree ? (
                                <Badge variant="outline" className="text-xs text-green-600">
                                  Gratis
                                </Badge>
                              ) : !isUnlocked ? (
                                <Badge variant="outline" className="text-xs">
                                  {layer.cost} cr
                                </Badge>
                              ) : null}
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1 ml-6">
                            {layer.description}
                          </p>
                        </div>
                      );
                    })}
                  </CardContent>
                )}
              </Card>
            );
          })}
        </div>
      </ScrollArea>

      {/* Purchase Dialog */}
      {console.log('[LayerSelector] Dialog state - purchaseDialogLayer:', purchaseDialogLayer)}
      <Dialog
        open={!!purchaseDialogLayer}
        onOpenChange={(open) => {
          console.log('[LayerSelector] Dialog onOpenChange:', open);
          if (!open) setPurchaseDialogLayer(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Desbloquear Capa</DialogTitle>
            <DialogDescription>
              {purchaseLayer_ && (
                <>
                  Deseas desbloquear <strong>{purchaseLayer_.name}</strong> por{' '}
                  <strong>{purchaseLayer_.cost} creditos</strong>?
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {purchaseLayer_ && (
              <div className="text-sm text-gray-600">
                <p>{purchaseLayer_.description}</p>
                <p className="mt-2">
                  Creditos actuales:{' '}
                  <strong>{group?.credits ?? 0}</strong>
                </p>
                {group && group.credits < purchaseLayer_.cost && (
                  <p className="mt-2 text-red-500">
                    No tienes suficientes creditos
                  </p>
                )}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setPurchaseDialogLayer(null)}
            >
              Cancelar
            </Button>
            <Button
              onClick={handlePurchase}
              disabled={
                isPurchasing ||
                !group ||
                (purchaseLayer_ ? group.credits < purchaseLayer_.cost : true)
              }
            >
              {isPurchasing ? 'Desbloqueando...' : 'Desbloquear'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
