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
    new Set(['governance', 'climate', 'coringa'])
  );
  const [purchaseDialogLayer, setPurchaseDialogLayer] = useState<string | null>(
    null
  );
  const [infoDialogLayer, setInfoDialogLayer] = useState<string | null>(null);
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

  const layersByCategory = layers
    .filter(layer => !layer.background)
    .reduce(
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
    return group?.purchasedLayers?.includes(layerId) ?? false;
  };

  const handleLayerClick = (layerId: string) => {
    if (isLayerUnlocked(layerId)) {
      toggleLayer(layerId);
    } else {
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
  const infoLayer_ = layers.find((l) => l.id === infoDialogLayer);

  return (
    <>
      <ScrollArea className="h-[calc(100vh-280px)]">
        <div className="space-y-2 pr-4">
          {(Object.keys(CATEGORY_CONFIG) as LayerCategory[]).filter((c) => c !== 'background').map((category) => {
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
                    {categoryLayers.map((layer, layerIndex) => {
                      const isUnlocked = isLayerUnlocked(layer.id);
                      const isActive = activeLayers.includes(layer.id);
                      const isHidden = layer.hidden && !isUnlocked;
                      const displayName = isHidden
                        ? `Camada Misteriosa ${['I', 'II', 'III', 'IV'][layerIndex] || layerIndex + 1}`
                        : layer.name;
                      const displayDesc = isHidden
                        ? 'Informação desconhecida. Compre esta camada para revelar seu conteúdo.'
                        : layer.description;

                      return (
                        <div
                          key={layer.id}
                          className={`
                            p-2 rounded-md cursor-pointer transition-all
                            ${isActive ? 'bg-purple-100 ring-2 ring-purple-400' : 'hover:bg-gray-50'}
                            ${!isUnlocked ? 'opacity-75' : ''}
                            ${isHidden ? 'border border-dashed border-amber-400' : ''}
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
                              ) : isHidden ? (
                                <span className="text-base">?</span>
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
                              <span className={`text-sm font-medium ${isHidden ? 'italic text-amber-700' : ''}`}>
                                {displayName}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              {!isHidden && (
                                <button
                                  className="w-5 h-5 rounded-full border border-gray-300 flex items-center justify-center text-[10px] font-bold text-gray-500 hover:bg-gray-200 hover:text-gray-700 transition shrink-0"
                                  title="Informações da camada"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setInfoDialogLayer(layer.id);
                                  }}
                                >
                                  i
                                </button>
                              )}
                              {layer.isFree ? (
                                <Badge variant="outline" className="text-xs text-green-600">
                                  Grátis
                                </Badge>
                              ) : !isUnlocked ? (
                                <Badge variant="outline" className="text-xs">
                                  {layer.cost} cr
                                </Badge>
                              ) : null}
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1 ml-6">
                            {displayDesc}
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
      <Dialog
        open={!!purchaseDialogLayer}
        onOpenChange={(open) => {
          if (!open) setPurchaseDialogLayer(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{purchaseLayer_?.hidden ? 'Revelar Camada Misteriosa' : 'Desbloquear Camada'}</DialogTitle>
            <DialogDescription>
              {purchaseLayer_ && (
                <>
                  {purchaseLayer_.hidden ? (
                    <>
                      Deseja revelar esta <strong>Camada Misteriosa</strong> por{' '}
                      <strong>{purchaseLayer_.cost} créditos</strong>?
                      A informação será revelada ao comprar.
                    </>
                  ) : (
                    <>
                      Deseja desbloquear <strong>{purchaseLayer_.name}</strong> por{' '}
                      <strong>{purchaseLayer_.cost} créditos</strong>?
                    </>
                  )}
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {purchaseLayer_ && (
              <div className="text-sm text-gray-600">
                <p>{purchaseLayer_.hidden ? 'Conteúdo desconhecido — será revelado ao comprar.' : purchaseLayer_.description}</p>
                <p className="mt-2">
                  Créditos atuais:{' '}
                  <strong>{group?.credits ?? 0}</strong>
                </p>
                {group && group.credits < purchaseLayer_.cost && (
                  <p className="mt-2 text-red-500">
                    Você não tem créditos suficientes
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

      {/* Layer Info Dialog */}
      <Dialog
        open={!!infoDialogLayer}
        onOpenChange={(open) => {
          if (!open) setInfoDialogLayer(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{infoLayer_?.name}</DialogTitle>
            <DialogDescription>{infoLayer_?.description}</DialogDescription>
          </DialogHeader>
          {infoLayer_ && (
            <div className="space-y-3 text-sm">
              <div>
                <h4 className="font-semibold text-gray-700 mb-1">Fonte dos dados</h4>
                <p className="text-gray-600">{infoLayer_.source || 'Não informada'}</p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-1">Fórmula / Metodologia</h4>
                <p className="text-gray-600">{infoLayer_.formula || 'Não informada'}</p>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-400 pt-2 border-t">
                <span>Variável: <code className="bg-gray-100 px-1 rounded">{infoLayer_.variable}</code></span>
                <span>Escala: {infoLayer_.colorScale === 'positive' ? 'Positiva (maior = melhor)' : infoLayer_.colorScale === 'negative' ? 'Negativa (maior = pior)' : 'Neutra'}</span>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setInfoDialogLayer(null)}>
              Fechar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
