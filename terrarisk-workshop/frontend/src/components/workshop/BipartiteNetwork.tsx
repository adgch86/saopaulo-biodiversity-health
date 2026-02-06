'use client';

import { useState, useMemo, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { CATEGORY_CONFIG } from '@/lib/types';
import type { LayerCategory } from '@/lib/types';

// Map risk dimension IDs to their category for coloring
const RISK_CATEGORY_MAP: Record<string, LayerCategory> = {
  governance_general: 'governance',
  governance_climatic: 'governance',
  biodiversity: 'biodiversity',
  natural_habitat: 'biodiversity',
  pollination: 'biodiversity',
  flooding: 'climate',
  fire_risk: 'climate',
  hydric_stress: 'climate',
  dengue: 'health',
  diarrhea: 'health',
  cv_mortality: 'health',
  resp_hosp: 'health',
  leishmaniasis: 'health',
  poverty: 'social',
  vulnerability: 'social',
  rural: 'social',
};

// Layout constants
const SVG_WIDTH = 900;
const NODE_RADIUS = 10;
const LEFT_X = 180;
const RIGHT_X = SVG_WIDTH - 180;
const TOP_PADDING = 40;
const LABEL_OFFSET = 14;

export default function BipartiteNetwork() {
  const tActions = useTranslations('actionNames');
  const tLayers = useTranslations('layerNames');
  const tNetwork = useTranslations('bipartiteNetwork');
  const { pearcActions, selectedActions, toggleAction } = useWorkshopStore();

  const [hoveredAction, setHoveredAction] = useState<string | null>(null);
  const [hoveredRisk, setHoveredRisk] = useState<string | null>(null);

  // Collect all unique risk dimensions from PEARC actions
  const riskDimensions = useMemo(() => {
    const dims = new Set<string>();
    pearcActions.forEach((action) => {
      Object.keys(action.links).forEach((dim) => dims.add(dim));
    });
    return Array.from(dims).sort((a, b) => {
      const catA = RISK_CATEGORY_MAP[a] || 'social';
      const catB = RISK_CATEGORY_MAP[b] || 'social';
      if (catA !== catB) return catA.localeCompare(catB);
      return a.localeCompare(b);
    });
  }, [pearcActions]);

  // Sort actions by category
  const sortedActions = useMemo(() => {
    return [...pearcActions].sort((a, b) => {
      if (a.category !== b.category) return a.category.localeCompare(b.category);
      return a.id.localeCompare(b.id);
    });
  }, [pearcActions]);

  // Calculate node positions
  const actionSpacing = useMemo(() => {
    const count = sortedActions.length;
    if (count <= 1) return 40;
    return Math.min(40, (600 - TOP_PADDING * 2) / (count - 1));
  }, [sortedActions.length]);

  const riskSpacing = useMemo(() => {
    const count = riskDimensions.length;
    if (count <= 1) return 40;
    return Math.min(40, (600 - TOP_PADDING * 2) / (count - 1));
  }, [riskDimensions.length]);

  const svgHeight = useMemo(() => {
    const maxNodes = Math.max(sortedActions.length, riskDimensions.length);
    return Math.max(400, TOP_PADDING * 2 + maxNodes * 40 + 20);
  }, [sortedActions.length, riskDimensions.length]);

  const getActionY = useCallback(
    (index: number) => {
      const totalHeight = (sortedActions.length - 1) * actionSpacing;
      const startY = (svgHeight - totalHeight) / 2;
      return startY + index * actionSpacing;
    },
    [sortedActions.length, actionSpacing, svgHeight]
  );

  const getRiskY = useCallback(
    (index: number) => {
      const totalHeight = (riskDimensions.length - 1) * riskSpacing;
      const startY = (svgHeight - totalHeight) / 2;
      return startY + index * riskSpacing;
    },
    [riskDimensions.length, riskSpacing, svgHeight]
  );

  // Determine if an edge should be highlighted
  const isEdgeHighlighted = useCallback(
    (actionId: string, riskId: string) => {
      if (hoveredAction === actionId) return true;
      if (hoveredRisk === riskId) return true;
      return false;
    },
    [hoveredAction, hoveredRisk]
  );

  // Determine if an edge is from a selected action
  const isEdgeSelected = useCallback(
    (actionId: string) => {
      return selectedActions.includes(actionId);
    },
    [selectedActions]
  );

  // Determine if anything is being hovered
  const isAnyHovered = hoveredAction !== null || hoveredRisk !== null;

  // Get connected actions for a risk dimension
  const getConnectedActions = useCallback(
    (riskId: string) => {
      return sortedActions.filter((a) => a.links[riskId] !== undefined).map((a) => a.id);
    },
    [sortedActions]
  );

  // Get connected risks for an action
  const getConnectedRisks = useCallback(
    (actionId: string) => {
      const action = sortedActions.find((a) => a.id === actionId);
      return action ? Object.keys(action.links) : [];
    },
    [sortedActions]
  );

  // Node highlight logic
  const isActionNodeHighlighted = useCallback(
    (actionId: string) => {
      if (hoveredAction === actionId) return true;
      if (hoveredRisk && getConnectedActions(hoveredRisk).includes(actionId)) return true;
      return false;
    },
    [hoveredAction, hoveredRisk, getConnectedActions]
  );

  const isRiskNodeHighlighted = useCallback(
    (riskId: string) => {
      if (hoveredRisk === riskId) return true;
      if (hoveredAction && getConnectedRisks(hoveredAction).includes(riskId)) return true;
      return false;
    },
    [hoveredAction, hoveredRisk, getConnectedRisks]
  );

  return (
    <div className="h-full flex flex-col bg-gray-50 p-4">
      <div className="mb-3">
        <h2 className="text-lg font-bold text-gray-800 mb-1">{tNetwork('title')}</h2>
        <p className="text-xs text-gray-500">{tNetwork('description')}</p>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mb-3 px-2">
        {Object.entries(CATEGORY_CONFIG).map(([key, config]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: config.color }}
            />
            <span className="text-xs text-gray-600">{config.label}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5 ml-2 border-l pl-3 border-gray-300">
          <div className="flex items-center gap-1">
            <div className="w-6 h-[1px] bg-gray-400" />
            <span className="text-xs text-gray-500">1</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-6 h-[2px] bg-gray-400" />
            <span className="text-xs text-gray-500">2</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-6 h-[3px] bg-gray-400" />
            <span className="text-xs text-gray-500">3</span>
          </div>
          <span className="text-xs text-gray-400 ml-1">{tNetwork('evidenceLevel')}</span>
        </div>
      </div>

      {/* SVG Network */}
      <div className="flex-1 overflow-auto rounded-lg border border-gray-200 bg-white">
        <svg
          width="100%"
          height={svgHeight}
          viewBox={`0 0 ${SVG_WIDTH} ${svgHeight}`}
          className="select-none"
        >
          {/* Column headers */}
          <text
            x={LEFT_X}
            y={16}
            textAnchor="middle"
            className="fill-gray-500 text-[11px] font-semibold uppercase tracking-wider"
          >
            {tNetwork('actions')}
          </text>
          <text
            x={RIGHT_X}
            y={16}
            textAnchor="middle"
            className="fill-gray-500 text-[11px] font-semibold uppercase tracking-wider"
          >
            {tNetwork('riskDimensions')}
          </text>

          {/* Edges */}
          <g>
            {sortedActions.map((action, actionIdx) => {
              const ay = getActionY(actionIdx);
              return Object.entries(action.links).map(([riskId, evidence]) => {
                const riskIdx = riskDimensions.indexOf(riskId);
                if (riskIdx === -1) return null;
                const ry = getRiskY(riskIdx);

                const highlighted = isEdgeHighlighted(action.id, riskId);
                const selected = isEdgeSelected(action.id);
                const dimmed = isAnyHovered && !highlighted;
                const category = action.category as LayerCategory;
                const color = CATEGORY_CONFIG[category]?.color || '#6B7280';

                const controlOffset = (RIGHT_X - LEFT_X) * 0.4;

                return (
                  <path
                    key={`${action.id}-${riskId}`}
                    d={`M ${LEFT_X + NODE_RADIUS} ${ay} C ${LEFT_X + controlOffset} ${ay}, ${RIGHT_X - controlOffset} ${ry}, ${RIGHT_X - NODE_RADIUS} ${ry}`}
                    fill="none"
                    stroke={highlighted || selected ? color : '#D1D5DB'}
                    strokeWidth={evidence * (highlighted ? 1.5 : 1)}
                    strokeOpacity={dimmed ? 0.08 : highlighted ? 0.85 : selected ? 0.5 : 0.2}
                    className="transition-all duration-200"
                  />
                );
              });
            })}
          </g>

          {/* Action nodes (left) */}
          <g>
            {sortedActions.map((action, idx) => {
              const y = getActionY(idx);
              const category = action.category as LayerCategory;
              const color = CATEGORY_CONFIG[category]?.color || '#6B7280';
              const isSelected = selectedActions.includes(action.id);
              const isHighlighted = isActionNodeHighlighted(action.id);
              const isDimmed = isAnyHovered && !isHighlighted;

              return (
                <g
                  key={action.id}
                  className="cursor-pointer"
                  onMouseEnter={() => setHoveredAction(action.id)}
                  onMouseLeave={() => setHoveredAction(null)}
                  onClick={() => toggleAction(action.id)}
                >
                  {/* Selection ring */}
                  {isSelected && (
                    <circle
                      cx={LEFT_X}
                      cy={y}
                      r={NODE_RADIUS + 4}
                      fill="none"
                      stroke={color}
                      strokeWidth={2}
                      strokeDasharray="3 2"
                      opacity={isDimmed ? 0.3 : 0.8}
                    />
                  )}
                  {/* Node circle */}
                  <circle
                    cx={LEFT_X}
                    cy={y}
                    r={isHighlighted ? NODE_RADIUS + 2 : NODE_RADIUS}
                    fill={isSelected || isHighlighted ? color : 'white'}
                    stroke={color}
                    strokeWidth={2}
                    opacity={isDimmed ? 0.3 : 1}
                    className="transition-all duration-200"
                  />
                  {/* Checkmark for selected */}
                  {isSelected && (
                    <text
                      x={LEFT_X}
                      y={y + 1}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="fill-white text-[8px] font-bold pointer-events-none"
                    >
                      ✓
                    </text>
                  )}
                  {/* Label */}
                  <text
                    x={LEFT_X - NODE_RADIUS - LABEL_OFFSET}
                    y={y}
                    textAnchor="end"
                    dominantBaseline="middle"
                    className={`text-[10px] pointer-events-none transition-all duration-200 ${
                      isHighlighted || isSelected
                        ? 'fill-gray-900 font-semibold'
                        : isDimmed
                          ? 'fill-gray-300'
                          : 'fill-gray-600'
                    }`}
                  >
                    {tActions(action.id)}
                  </text>
                </g>
              );
            })}
          </g>

          {/* Risk dimension nodes (right) */}
          <g>
            {riskDimensions.map((riskId, idx) => {
              const y = getRiskY(idx);
              const category = RISK_CATEGORY_MAP[riskId] || 'social';
              const color = CATEGORY_CONFIG[category]?.color || '#6B7280';
              const isHighlighted = isRiskNodeHighlighted(riskId);
              const isDimmed = isAnyHovered && !isHighlighted;

              return (
                <g
                  key={riskId}
                  className="cursor-pointer"
                  onMouseEnter={() => setHoveredRisk(riskId)}
                  onMouseLeave={() => setHoveredRisk(null)}
                >
                  {/* Node */}
                  <rect
                    x={RIGHT_X - (isHighlighted ? NODE_RADIUS + 2 : NODE_RADIUS)}
                    y={y - (isHighlighted ? NODE_RADIUS + 2 : NODE_RADIUS)}
                    width={(isHighlighted ? NODE_RADIUS + 2 : NODE_RADIUS) * 2}
                    height={(isHighlighted ? NODE_RADIUS + 2 : NODE_RADIUS) * 2}
                    rx={3}
                    fill={isHighlighted ? color : 'white'}
                    stroke={color}
                    strokeWidth={2}
                    opacity={isDimmed ? 0.3 : 1}
                    className="transition-all duration-200"
                  />
                  {/* Label */}
                  <text
                    x={RIGHT_X + NODE_RADIUS + LABEL_OFFSET}
                    y={y}
                    textAnchor="start"
                    dominantBaseline="middle"
                    className={`text-[10px] pointer-events-none transition-all duration-200 ${
                      isHighlighted
                        ? 'fill-gray-900 font-semibold'
                        : isDimmed
                          ? 'fill-gray-300'
                          : 'fill-gray-600'
                    }`}
                  >
                    {tLayers(riskId)}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      {/* Selected count */}
      <div className="mt-2 text-center">
        <span className="text-xs text-gray-500">
          {selectedActions.length} {tNetwork('actionsSelectedCount')}
        </span>
      </div>
    </div>
  );
}
