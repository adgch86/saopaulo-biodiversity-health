// TerraRisk Workshop - Types

export interface Layer {
  id: string;
  name: string;
  category: LayerCategory;
  description: string;
  source?: string;
  formula?: string;
  cost: number;
  imageUrl: string;
  variable: string;
  colorScale: 'positive' | 'negative' | 'neutral' | 'categorical';
  popularity: number;
  isFree?: boolean;
  hidden?: boolean;
  background?: boolean;
}

export type LayerCategory =
  | 'governance'
  | 'biodiversity'
  | 'climate'
  | 'coringa'
  | 'health'
  | 'social'
  | 'background';

export interface Group {
  id: string;
  name: string;
  credits: number;
  purchasedLayers: string[];
  professionalArea?: string;
  environmentalExperience?: string;
  numParticipants?: number;
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
  professionalArea?: string;
  environmentalExperience?: string;
  numParticipants?: number;
}

// Map bounds for São Paulo state
export const SP_BOUNDS: [[number, number], [number, number]] = [
  [-25.5, -53.5], // Southwest
  [-19.5, -44.0]  // Northeast
];

export const SP_CENTER: [number, number] = [-22.5, -48.5];

// Category colors and labels
export const CATEGORY_CONFIG: Record<LayerCategory, { label: string; color: string; bgColor: string }> = {
  governance: { label: 'Governança', color: '#7B1FA2', bgColor: 'bg-purple-100' },
  biodiversity: { label: 'Biodiversidade', color: '#2E7D32', bgColor: 'bg-green-100' },
  climate: { label: 'Clima', color: '#E65100', bgColor: 'bg-orange-100' },
  health: { label: 'Saúde', color: '#C62828', bgColor: 'bg-red-100' },
  social: { label: 'Social', color: '#1565C0', bgColor: 'bg-blue-100' },
  coringa: { label: 'Coringa', color: '#FF6F00', bgColor: 'bg-amber-100' },
  background: { label: 'Fundo', color: '#455A64', bgColor: 'bg-gray-100' },
};

// Workshop Flow Types

export type WorkshopPhase = 'step1' | 'step1_results' | 'step2' | 'step2_results' | 'step2b' | 'step2b_results' | 'step3' | 'step4' | 'step5' | 'survey';

// ITECS v1.2 — Instrumento de Avaliação de Coerência Sistêmica
export interface ITECSCollaborator {
  nameOrInstitution: string;
  topic: string;
  frequency: 'monthly' | 'more_than_monthly' | 'yearly' | 'sporadic';
}

export interface ITECSResponses {
  // Bloco I — Transformação Cognitiva (1-7)
  tc1: number; tc2: number; tc3: number; tc4: number; tc5: number;
  // Bloco II — Robustez Analítica (1-7)
  ra6: number; ra7: number; ra8: number;
  // Bloco III — Potencial da Ferramenta (1-7)
  pf9: number; pf10: number; pf11: number; pf12: number;
  // Bloco IV — Coerência Sistêmica Percebida (1-7)
  csp13: number; csp14: number; csp15: number; csp16: number;
  // Bloco V — Intenção de Aplicação (1-7)
  ia17: number; ia18: number; ia19: number; ia20: number;
  // Bloco VI — Ativação Proativa (1-7)
  ap21: number; ap22: number; ap23: number; ap24: number; ap25: number;
  // Bloco VII — Coprodução e Uso de Evidência (texto)
  q26: string; q27: string;
  // Bloco VIII — Rede de Colaboradores (tabela)
  q28: ITECSCollaborator[];
  // Bloco IX — Próximos Passos (texto)
  q29: string; q30: string;
}

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
  step1: { step: 1, icon: '1' },
  step1_results: { step: 1, icon: '1' },
  step2: { step: 2, icon: '2' },
  step2_results: { step: 2, icon: '2' },
  step2b: { step: 2.5, icon: '2b' },
  step2b_results: { step: 2.5, icon: '2b' },
  step3: { step: 3, icon: '3' },
  step4: { step: 4, icon: '4' },
  step5: { step: 5, icon: '5' },
  survey: { step: 6, icon: '6' },
};

export interface GroupComparisonData {
  groups: Array<{
    id: string;
    name: string;
    credits: number;
    creditsSpent: number;
    purchasedLayers: string[];
    layersByCategory: Record<string, number>;
    ranking: Array<{code: string; position: number; name: string}> | null;
    revisedRanking: Array<{code: string; position: number; name: string}> | null;
    exchangeRanking: Array<{code: string; position: number; name: string}> | null;
    averageValues: Record<string, number>;
  }>;
  totalGroups: number;
}
