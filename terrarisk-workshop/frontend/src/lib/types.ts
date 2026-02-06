// TerraRisk Workshop - Types

export interface Layer {
  id: string;
  name: string;
  category: LayerCategory;
  description: string;
  cost: number;
  imageUrl: string;
  variable: string;
  colorScale: 'positive' | 'negative' | 'neutral';
  popularity: number;
  isFree?: boolean;
}

export type LayerCategory =
  | 'governance'
  | 'biodiversity'
  | 'climate'
  | 'health'
  | 'social';

export interface Group {
  id: string;
  name: string;
  credits: number;
  purchasedLayers: string[];
  createdAt: string;
}

export interface Municipality {
  code: string;
  name: string;
  region?: string;
  data: Record<string, number | string | null>;
}

export interface MunicipalityBasic {
  code: string;
  name: string;
  region?: string;
}

export interface BivariateMap {
  layer1Id: string;
  layer2Id: string;
  imageUrl: string;
  quadrants: BivariateQuadrant[];
}

export interface BivariateQuadrant {
  id: string;
  label: string;
  description: string;
  color: string;
  count: number;
}

export interface LayerConfig {
  id: string;
  name: string;
  category: LayerCategory;
  description: string;
  cost: number;
  variable: string;
  imageFile: string;
  colorScale: 'positive' | 'negative' | 'neutral';
  isFree?: boolean;
}

export interface AdminStats {
  totalGroups: number;
  totalPurchases: number;
  popularLayers: { layerId: string; count: number }[];
  creditsSpent: number;
  groupStats: GroupStats[];
}

export interface GroupStats {
  id: string;
  name: string;
  credits: number;
  purchasedCount: number;
  lastActivity: string;
}

// Map bounds for São Paulo state
export const SP_BOUNDS: [[number, number], [number, number]] = [
  [-25.5, -53.5], // Southwest
  [-19.5, -44.0]  // Northeast
];

export const SP_CENTER: [number, number] = [-22.5, -48.5];

// Category colors and labels
export const CATEGORY_CONFIG: Record<LayerCategory, { label: string; color: string; bgColor: string }> = {
  governance: { label: 'Gobernanza', color: '#7B1FA2', bgColor: 'bg-purple-100' },
  biodiversity: { label: 'Biodiversidad', color: '#2E7D32', bgColor: 'bg-green-100' },
  climate: { label: 'Clima', color: '#E65100', bgColor: 'bg-orange-100' },
  health: { label: 'Salud', color: '#C62828', bgColor: 'bg-red-100' },
  social: { label: 'Social', color: '#1565C0', bgColor: 'bg-blue-100' },
};

// Workshop Flow Types

export type WorkshopPhase = 'ranking' | 'explore' | 'revised' | 'results';

export interface WorkshopMunicipality {
  code: string;
  name: string;
  quadrant: string;
  description: string;
  riskSummary: {
    governance: number;
    biodiversity: number;
    climate: number;
    health: number;
    social: number;
  };
}

export interface RankingEntry {
  code: string;
  position: number;
}

export interface PEARCAction {
  id: string;
  category: string;
  links: Record<string, number>;
  totalLinks: number;
  avgEvidence: number;
}

export interface RankingComparison {
  userRanking: Array<{code: string; name: string; position: number}>;
  platformRanking: Array<{code: string; name: string; position: number; compositeScore: number}>;
  rankingCorrelation: {spearman: number; kendall: number};
  positionDifferences: Array<{code: string; name: string; userPosition: number; platformPosition: number; difference: number}>;
  userActions: string[];
  suggestedActions: Array<{id: string; relevanceScore: number}>;
  actionOverlap: number;
}

export const QUADRANT_CONFIG: Record<string, {label: string; color: string; bgColor: string}> = {
  Q1: { label: 'Model', color: '#2E7D32', bgColor: 'bg-green-100' },
  Q2: { label: 'Risk', color: '#FFC107', bgColor: 'bg-yellow-100' },
  Q3: { label: 'Critical', color: '#C62828', bgColor: 'bg-red-100' },
  Q4: { label: 'Potential', color: '#E65100', bgColor: 'bg-orange-100' },
};

export const PHASE_CONFIG: Record<WorkshopPhase, {step: number; icon: string}> = {
  ranking: { step: 1, icon: '1' },
  explore: { step: 2, icon: '2' },
  revised: { step: 3, icon: '3' },
  results: { step: 4, icon: '4' },
};
