'use client';

import { useState, useEffect } from 'react';
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
    label: 'Gobernanza',
    variables: ['UAI_Crisk', 'gobernanza_100', 'UAI', 'pol_def'],
  },
  biodiversity: {
    label: 'Biodiversidad',
    variables: ['biodiversity', 'forest_cover', 'natural_habitat', 'pollination_deficit'],
  },
  climate: {
    label: 'Riesgo Climatico',
    variables: ['fire_risk_index', 'flooding_risk', 'hydric_stress_r'],
  },
  health: {
    label: 'Salud',
    variables: [
      'dengue',
      'leishmaniose',
      'incidence_diarr',
      'death_circ_mean',
      'hosp_resp_mean',
    ],
  },
  social: {
    label: 'Social',
    variables: ['vulnerabilidad', 'pct_pobreza', 'pct_rural', 'pct_preta'],
  },
};

// Human-readable labels
const VARIABLE_LABELS: Record<string, string> = {
  UAI_Crisk: 'Indice UAI Riesgo Climatico',
  gobernanza_100: 'Indice de Gobernanza',
  UAI: 'UAI General',
  pol_def: 'Politicas Definidas',
  biodiversity: 'Riqueza de Especies',
  forest_cover: 'Cobertura Forestal',
  natural_habitat: 'Habitat Natural',
  pollination_deficit: 'Deficit de Polinizacion',
  fire_risk_index: 'Indice de Riesgo de Incendio',
  flooding_risk: 'Riesgo de Inundacion',
  hydric_stress_r: 'Estres Hidrico',
  dengue: 'Incidencia de Dengue',
  leishmaniose: 'Incidencia de Leishmaniasis',
  incidence_diarr: 'Incidencia de Diarrea',
  death_circ_mean: 'Mortalidad Cardiovascular',
  hosp_resp_mean: 'Hospitalizacion Respiratoria',
  vulnerabilidad: 'Indice de Vulnerabilidad',
  pct_pobreza: 'Porcentaje de Pobreza',
  pct_rural: 'Porcentaje Rural',
  pct_preta: 'Porcentaje Poblacion Negra',
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
  const { selectedMunicipality, setSelectedMunicipality, layers, activeLayers } =
    useWorkshopStore();
  const [radarProfile, setRadarProfile] = useState<RadarProfile | null>(null);

  // Fetch radar data when municipality changes
  useEffect(() => {
    if (!selectedMunicipality) {
      setRadarProfile(null);
      return;
    }

    fetch(`/api/workshop/radar?codes=${selectedMunicipality.code}`)
      .then((res) => res.json())
      .then((data: RadarProfile[]) => {
        if (data.length > 0) {
          setRadarProfile(data[0]);
        }
      })
      .catch(() => setRadarProfile(null));
  }, [selectedMunicipality]);

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

  const activeLayerVariables = activeLayers
    .map((id) => layers.find((l) => l.id === id)?.variable)
    .filter(Boolean);

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
            {/* Radar chart */}
            {radarProfile && (
              <div className="pb-2">
                <RadarChart profiles={[radarProfile]} size={240} />
                <Separator className="mt-2" />
              </div>
            )}
            {/* Active layer variables first */}
            {activeLayerVariables.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-purple-600 mb-2">
                  {t('activeVariables')}
                </h4>
                {activeLayerVariables.map((variable) => {
                  const value = selectedMunicipality.data[variable!] as number | null;
                  return (
                    <div
                      key={variable}
                      className="flex justify-between items-center py-1 bg-purple-50 px-2 rounded mb-1"
                    >
                      <span className="text-xs">
                        {VARIABLE_LABELS[variable!] || variable}
                      </span>
                      <Badge
                        variant="outline"
                        className={getValueColor(variable!, value)}
                      >
                        {formatValue(value)}
                      </Badge>
                    </div>
                  );
                })}
                <Separator className="my-2" />
              </div>
            )}

            {/* All variable groups */}
            {Object.entries(VARIABLE_GROUPS).map(([key, group]) => (
              <div key={key}>
                <h4 className="text-xs font-semibold text-gray-600 mb-1">
                  {group.label}
                </h4>
                {group.variables.map((variable) => {
                  if (activeLayerVariables.includes(variable)) return null;
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
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
