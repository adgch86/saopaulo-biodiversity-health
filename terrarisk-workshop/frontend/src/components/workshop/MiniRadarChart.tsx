'use client';

/**
 * Compact radar chart for municipality cards.
 * Uses PlanetaryRadar (wedge-based) internally.
 * Only purchased categories get colored; others show as gray.
 */

import PlanetaryRadar, {
  CANONICAL_ORDER,
  DIMENSION_SEMANTICS,
  type PlanetaryDimension,
} from './PlanetaryRadar';

const SHORT_LABELS: Record<string, string> = {
  governance: 'Gov',
  biodiversity: 'Bio',
  climate: 'Clima',
  health: 'Saúde',
  social: 'Social',
};

interface Props {
  /** Values normalized 0-1 per category */
  values: Record<string, number>;
  /** Categories that have purchased layer data */
  purchasedCategories: Set<string>;
  size?: number;
}

export default function MiniRadarChart({ values, purchasedCategories, size = 130 }: Props) {
  const dimensions: PlanetaryDimension[] = CANONICAL_ORDER.map((key) => ({
    key,
    label: SHORT_LABELS[key] ?? key,
    value: Math.max(0, Math.min(1, values[key] ?? 0)),
    purchased: purchasedCategories.has(key),
    semantics: DIMENSION_SEMANTICS[key] ?? 'risk',
  }));

  return (
    <PlanetaryRadar
      dimensions={dimensions}
      size={size}
      showLabels={size > 100}
      safeZoneFraction={0.25}
    />
  );
}
