// TerraRisk Workshop - Zustand Store
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Group, Layer, Municipality, MunicipalityBasic, WorkshopPhase, WorkshopMunicipality, RankingEntry, PEARCAction, RankingComparison, GroupComparisonData, ITECSResponses } from './types';

interface WorkshopState {
  // Group state
  group: Group | null;
  setGroup: (group: Group | null) => void;

  // Layers
  layers: Layer[];
  setLayers: (layers: Layer[]) => void;
  activeLayers: string[];
  toggleLayer: (layerId: string) => void;
  setActiveLayers: (layerIds: string[]) => void;

  // Selected municipality
  selectedMunicipality: Municipality | null;
  setSelectedMunicipality: (municipality: Municipality | null) => void;
  hoveredMunicipalityCode: string | null;
  setHoveredMunicipalityCode: (code: string | null) => void;

  // Municipalities list
  municipalities: MunicipalityBasic[];
  setMunicipalities: (municipalities: MunicipalityBasic[]) => void;

  // UI state
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  activeTab: 'layers' | 'info' | 'strategy';
  setActiveTab: (tab: 'layers' | 'info' | 'strategy') => void;

  // Bivariate mode
  bivariateMode: boolean;
  setBivariateMode: (mode: boolean) => void;
  bivariateImageUrl: string | null;
  setBivariateImageUrl: (url: string | null) => void;
  bivariateData: {
    values: Record<string, [number | null, number | null]>;
    terciles1: [number, number];
    terciles2: [number, number];
    layer1Name: string;
    layer2Name: string;
  } | null;
  setBivariateData: (data: WorkshopState['bivariateData']) => void;

  // Credits animation
  creditAnimation: boolean;
  triggerCreditAnimation: () => void;

  // Layer opacity
  layerOpacity: Record<string, number>;
  setLayerOpacity: (layerId: string, opacity: number) => void;

  // Workshop Flow state
  workshopPhase: WorkshopPhase;
  setWorkshopPhase: (phase: WorkshopPhase) => void;
  workshopMunicipalities: WorkshopMunicipality[];
  setWorkshopMunicipalities: (municipalities: WorkshopMunicipality[]) => void;
  initialRanking: RankingEntry[];
  setInitialRanking: (ranking: RankingEntry[]) => void;
  revisedRanking: RankingEntry[];
  setRevisedRanking: (ranking: RankingEntry[]) => void;
  exchangeRanking: RankingEntry[];
  setExchangeRanking: (ranking: RankingEntry[]) => void;
  pearcActions: PEARCAction[];
  setPearcActions: (actions: PEARCAction[]) => void;
  selectedActions: string[];
  setSelectedActions: (actions: string[]) => void;
  toggleAction: (actionId: string) => void;
  comparison: RankingComparison | null;
  setComparison: (comparison: RankingComparison | null) => void;
  groupComparison: GroupComparisonData | null;
  setGroupComparison: (data: GroupComparisonData | null) => void;

  // ITECS Survey
  surveySubmitted: boolean;
  setSurveySubmitted: (submitted: boolean) => void;
  surveyParticipantId: string | null;
  setSurveyParticipantId: (id: string) => void;
  surveyResponses: ITECSResponses | null;
  setSurveyResponses: (responses: ITECSResponses | null) => void;

  // Actions
  purchaseLayer: (layerId: string) => Promise<boolean>;
  resetGroup: () => void;
}

export const useWorkshopStore = create<WorkshopState>()(
  persist(
    (set, get) => ({
      // Initial state
      group: null,
      layers: [],
      activeLayers: [],
      selectedMunicipality: null,
      hoveredMunicipalityCode: null,
      municipalities: [],
      isSidebarOpen: true,
      activeTab: 'layers',
      bivariateMode: false,
      bivariateImageUrl: null,
      bivariateData: null,
      creditAnimation: false,
      layerOpacity: {},
      workshopPhase: 'step1',
      workshopMunicipalities: [],
      initialRanking: [],
      revisedRanking: [],
      exchangeRanking: [],
      pearcActions: [],
      selectedActions: [],
      comparison: null,
      groupComparison: null,
      surveySubmitted: false,
      surveyParticipantId: null,
      surveyResponses: null,

      // Setters
      setGroup: (group) => set({ group }),
      setLayers: (layers) => set({ layers }),
      setSelectedMunicipality: (municipality) => set({ selectedMunicipality: municipality }),
      setHoveredMunicipalityCode: (code) => set({ hoveredMunicipalityCode: code }),
      setMunicipalities: (municipalities) => set({ municipalities }),
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setBivariateMode: (mode) => set({ bivariateMode: mode }),
      setBivariateImageUrl: (url) => set({ bivariateImageUrl: url }),
      setBivariateData: (data) => set({ bivariateData: data }),

      toggleLayer: (layerId) => set((state) => {
        const isActive = state.activeLayers.includes(layerId);
        if (isActive) {
          return { activeLayers: state.activeLayers.filter(id => id !== layerId) };
        }
        // Max 2 layers for bivariate
        if (state.activeLayers.length >= 2) {
          return { activeLayers: [...state.activeLayers.slice(1), layerId] };
        }
        return { activeLayers: [...state.activeLayers, layerId] };
      }),

      setActiveLayers: (layerIds) => set({ activeLayers: layerIds }),

      triggerCreditAnimation: () => {
        set({ creditAnimation: true });
        setTimeout(() => set({ creditAnimation: false }), 600);
      },

      setLayerOpacity: (layerId, opacity) => set((state) => ({
        layerOpacity: { ...state.layerOpacity, [layerId]: opacity }
      })),

      setWorkshopPhase: (phase) => set({ workshopPhase: phase }),
      setWorkshopMunicipalities: (municipalities) => set({ workshopMunicipalities: municipalities }),
      setInitialRanking: (ranking) => set({ initialRanking: ranking }),
      setRevisedRanking: (ranking) => set({ revisedRanking: ranking }),
      setExchangeRanking: (ranking) => set({ exchangeRanking: ranking }),
      setPearcActions: (actions) => set({ pearcActions: actions }),
      setSelectedActions: (actions) => set({ selectedActions: actions }),
      toggleAction: (actionId) => set((state) => {
        const isSelected = state.selectedActions.includes(actionId);
        return {
          selectedActions: isSelected
            ? state.selectedActions.filter(id => id !== actionId)
            : [...state.selectedActions, actionId]
        };
      }),
      setComparison: (comparison) => set({ comparison }),
      setGroupComparison: (data) => set({ groupComparison: data }),
      setSurveySubmitted: (submitted) => set({ surveySubmitted: submitted }),
      setSurveyParticipantId: (id) => set({ surveyParticipantId: id }),
      setSurveyResponses: (responses) => set({ surveyResponses: responses }),

      // Purchase layer
      purchaseLayer: async (layerId) => {
        const state = get();
        if (!state.group) return false;

        const layer = state.layers.find(l => l.id === layerId);
        if (!layer || layer.isFree) return false;

        if (state.group.credits < layer.cost) return false;
        if (state.group.purchasedLayers?.includes(layerId)) return false;

        try {
          const response = await fetch(`/api/groups/${state.group.id}/purchase`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ layerId }),
          });

          if (!response.ok) {
            // Group was deleted from server — clear local state
            if (response.status === 404) {
              get().resetGroup();
            }
            return false;
          }

          const updatedGroup = await response.json();
          set({ group: updatedGroup });
          get().triggerCreditAnimation();
          return true;
        } catch {
          return false;
        }
      },

      resetGroup: () => set({
        group: null,
        activeLayers: [],
        selectedMunicipality: null,
        bivariateMode: false,
        bivariateImageUrl: null,
        bivariateData: null,
        workshopPhase: 'step1',
        initialRanking: [],
        revisedRanking: [],
        exchangeRanking: [],
        selectedActions: [],
        comparison: null,
        groupComparison: null,
      }),
    }),
    {
      name: 'terrarisk-workshop',
      partialize: (state) => ({
        group: state.group,
        layerOpacity: state.layerOpacity,
        workshopPhase: state.workshopPhase,
        initialRanking: state.initialRanking,
        revisedRanking: state.revisedRanking,
        exchangeRanking: state.exchangeRanking,
        selectedActions: state.selectedActions,
        groupComparison: state.groupComparison,
        surveySubmitted: state.surveySubmitted,
        surveyParticipantId: state.surveyParticipantId,
      }),
    }
  )
);
