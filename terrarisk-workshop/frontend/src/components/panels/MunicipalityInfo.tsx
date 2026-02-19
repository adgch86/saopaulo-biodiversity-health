'use client';

import { useState, useEffect, useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import RadarChart from '@/components/workshop/RadarChart';
import type { RadarProfile } from '@/components/workshop/RadarChart';

// Variable categories for organized display
const VARIABLE_GROUPS = {
  governance: {
    label: 'Governança',
    variables: ['UAI_Crisk', 'gobernanza_100', 'UAI', 'pol_def'],
  },
  biodiversity: {
    label: 'Biodiversidade',
    variables: ['mean_species_richness', 'forest_cover', 'pollination_deficit', 'idx_biodiv'],
  },
  climate: {
    label: 'Risco Climático',
    variables: ['fire_risk_index', 'flooding_risk', 'hydric_stress_r'],
  },
  health: {
    label: 'Saúde',
    variables: [
      'dengue',
      'incidence_diarr',
      'death_circ_mean',
      'hosp_resp_mean',
    ],
  },
  social: {
    label: 'Social',
    variables: ['vulnerabilidad', 'pct_pobreza', 'pct_rural', 'pct_urbana', 'population'],
  },
};

// Human-readable labels
const VARIABLE_LABELS: Record<string, string> = {
  UAI_Crisk: 'Índice UAI Risco Climático',
  gobernanza_100: 'Índice de Governança',
  UAI: 'UAI Geral',
  pol_def: 'Políticas Definidas',
  biodiversity: 'Riqueza de Espécies',
  forest_cover: 'Cobertura Florestal',
  mean_species_richness: 'Riqueza Média de Espécies',
  idx_biodiv: 'Índice Composto Biodiversidade',
  pollination_deficit: 'Déficit de Polinização',
  fire_risk_index: 'Índice de Risco de Incêndio',
  flooding_risk: 'Risco de Inundação',
  hydric_stress_r: 'Estresse Hídrico',
  dengue: 'Incidência de Dengue',
  idx_carga_enfermedad: 'Índice Composto Saúde',
  idx_clima: 'Índice Composto Clima',
  pct_urbana: 'Percentual Urbano',
  population: 'População',
  incidence_diarr: 'Incidência de Diarreia',
  death_circ_mean: 'Mortalidade Cardiovascular',
  hosp_resp_mean: 'Hospitalização Respiratória',
  vulnerabilidad: 'Índice de Vulnerabilidade',
  pct_pobreza: 'Percentual de Pobreza',
  pct_rural: 'Percentual Rural',
  pct_preta: 'Percentual População Negra',
};

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'number') {
    if (Number.isInteger(value)) return value.toLocaleString();
    return value.toFixed(2);
  }
  return String(value);
}

function getValueColor(variable: string, value: number | null): string {
  if (value === null) return 'text-gray-400';

  // Variables where higher is worse
  const negativeVars = [
    'fire_risk_index',
    'flooding_risk',
    'hydric_stress_r',
    'dengue',
    'leishmaniose',
    'incidence_diarr',
    'death_circ_mean',
    'hosp_resp_mean',
    'vulnerabilidad',
    'pct_pobreza',
    'pollination_deficit',
  ];

  // Simplified color logic based on terciles (assuming 0-1 scale normalized)
  const isNegative = negativeVars.includes(variable);

  if (value > 0.66) {
    return isNegative ? 'text-red-600' : 'text-green-600';
  } else if (value > 0.33) {
    return 'text-yellow-600';
  } else {
    return isNegative ? 'text-green-600' : 'text-red-600';
  }
}

export default function MunicipalityInfo() {
  const t = useTranslations('municipality');
  const { selectedMunicipality, setSelectedMunicipality, layers, activeLayers, group } =
    useWorkshopStore();
  const [radarProfile, setRadarProfile] = useState<RadarProfile | null>(null);

  // Variables the group has access to (from purchased + free layers)
  const purchasedVariables = useMemo(() => {
    const vars = new Set<string>();
    // Free layers are always visible
    layers.filter((l) => l.isFree).forEach((l) => vars.add(l.variable));
    // Purchased layers
    if (group?.purchasedLayers) {
      group.purchasedLayers.forEach((layerId) => {
        const layer = layers.find((l) => l.id === layerId);
        if (layer) vars.add(layer.variable);
      });
    }
    return vars;
  }, [group?.purchasedLayers, layers]);

  // Categories that have at least one purchased/free layer
  const purchasedCategories = useMemo(() => {
    const cats = new Set<string>();
    layers.filter((l) => l.isFree).forEach((l) => cats.add(l.category));
    if (group?.purchasedLayers) {
      group.purchasedLayers.forEach((layerId) => {
        const layer = layers.find((l) => l.id === layerId);
        if (layer) cats.add(layer.category);
      });
    }
    return cats;
  }, [group?.purchasedLayers, layers]);

  // Fetch radar data when municipality changes
  useEffect(() => {
    if (!selectedMunicipality || !group?.id) {
      setRadarProfile(null);
      return;
    }

    fetch(`/api/workshop/radar?codes=${selectedMunicipality.code}&group_id=${encodeURIComponent(group.id)}`)
      .then((res) => res.json())
      .then((data: RadarProfile[]) => {
        if (data.length > 0) {
          setRadarProfile(data[0]);
        }
      })
      .catch(() => setRadarProfile(null));
  }, [selectedMunicipality, group?.id]);

  // Filter radar profile to only show purchased categories
  const filteredRadarProfile = useMemo(() => {
    if (!radarProfile || purchasedCategories.size === 0) return null;
    return {
      ...radarProfile,
      scores: Object.fromEntries(
        Object.entries(radarProfile.scores).map(([cat, score]) => [
          cat,
          purchasedCategories.has(cat) ? score : 0,
        ])
      ),
    };
  }, [radarProfile, purchasedCategories]);

  if (!selectedMunicipality || !selectedMunicipality.data) {
    return (
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm">{t('title')}</CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <p className="text-sm text-gray-500 text-center py-4">
            {t('clickToSelect')}
          </p>
        </CardContent>
      </Card>
    );
  }

  // Only show active layer variables that are also purchased
  const activeLayerVariables = activeLayers
    .map((id) => layers.find((l) => l.id === id)?.variable)
    .filter((v): v is string => Boolean(v) && purchasedVariables.has(v!));

  const hasPurchases = purchasedVariables.size > 0;

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <span>{selectedMunicipality.name}</span>
          <button
            onClick={() => setSelectedMunicipality(null)}
            className="text-gray-400 hover:text-gray-600"
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
        </CardTitle>
      </CardHeader>
      <CardContent className="py-0">
        <ScrollArea className="h-[350px]">
          <div className="space-y-3 pr-4">
            {!hasPurchases && (
              <p className="text-xs text-gray-400 text-center py-6">
                {t('purchaseLayersToSeeData')}
              </p>
            )}

            {/* Radar chart - only if there are purchased categories */}
            {filteredRadarProfile && (
              <div className="pb-2">
                <RadarChart profiles={[filteredRadarProfile]} size={240} />
                <Separator className="mt-2" />
              </div>
            )}

            {/* Active layer variables first (only purchased) */}
            {activeLayerVariables.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-purple-600 mb-2">
                  {t('activeVariables')}
                </h4>
                {activeLayerVariables.map((variable) => {
                  const value = selectedMunicipality.data[variable] as number | null;
                  return (
                    <div
                      key={variable}
                      className="flex justify-between items-center py-1 bg-purple-50 px-2 rounded mb-1"
                    >
                      <span className="text-xs">
                        {VARIABLE_LABELS[variable] || variable}
                      </span>
                      <Badge
                        variant="outline"
                        className={getValueColor(variable, value)}
                      >
                        {formatValue(value)}
                      </Badge>
                    </div>
                  );
                })}
                <Separator className="my-2" />
              </div>
            )}

            {/* Variable groups - only show purchased variables */}
            {hasPurchases &&
              Object.entries(VARIABLE_GROUPS).map(([key, varGroup]) => {
                // Filter to only purchased variables not already shown as active
                const visibleVars = varGroup.variables.filter(
                  (v) => purchasedVariables.has(v) && !activeLayerVariables.includes(v)
                );
                if (visibleVars.length === 0) return null;

                return (
                  <div key={key}>
                    <h4 className="text-xs font-semibold text-gray-600 mb-1">
                      {varGroup.label}
                    </h4>
                    {visibleVars.map((variable) => {
                      const value = selectedMunicipality.data[variable] as number | null;
                      return (
                        <div
                          key={variable}
                          className="flex justify-between items-center py-0.5"
                        >
                          <span className="text-xs text-gray-600">
                            {VARIABLE_LABELS[variable] || variable}
                          </span>
                          <span
                            className={`text-xs font-medium ${getValueColor(variable, value)}`}
                          >
                            {formatValue(value)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
