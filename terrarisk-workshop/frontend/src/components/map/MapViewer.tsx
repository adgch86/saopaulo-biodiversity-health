'use client';

import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useWorkshopStore } from '@/lib/store';
import { SP_CENTER, SP_BOUNDS } from '@/lib/types';

interface ChoroplethData {
  variable: string;
  values: Record<string, number | null>;
  terciles: [number, number];
  min: number;
  max: number;
}

interface BackgroundData {
  variable: string;
  values: Record<string, number | string | null>;
}

// PMVA IAA class colors (0.0=lowest, 1.0=highest environmental quality)
const PMVA_CLASS_COLORS: Record<number, string> = {
  0.0: '#ffccbc',   // Orange-red — lowest IAA
  0.25: '#ffe0b2',  // Light orange
  0.5: '#fff9c4',   // Yellow — medium
  0.75: '#c5e1a5',  // Light green
  1.0: '#a5d6a7',   // Green — highest IAA (certified)
};
const PMVA_LEGEND = [
  { value: 0.0, label: 'IAA Muito baixo', color: '#ffccbc' },
  { value: 0.25, label: 'IAA Baixo', color: '#ffe0b2' },
  { value: 0.5, label: 'IAA Médio', color: '#fff9c4' },
  { value: 0.75, label: 'IAA Alto', color: '#c5e1a5' },
  { value: 1.0, label: 'IAA Certificado', color: '#a5d6a7' },
];

function getBackgroundColor(value: number | string | null): string {
  if (value === null) return '#f5f5f5';
  const numVal = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numVal)) return '#f5f5f5';
  // Find closest class
  const classes = [0, 0.25, 0.5, 0.75, 1.0];
  const closest = classes.reduce((prev, curr) =>
    Math.abs(curr - numVal) < Math.abs(prev - numVal) ? curr : prev
  );
  return PMVA_CLASS_COLORS[closest] || '#f5f5f5';
}

// Color scales
const POSITIVE_COLORS = ['#C62828', '#FFC107', '#2E7D32']; // Red -> Yellow -> Green (low is bad)
const NEGATIVE_COLORS = ['#2E7D32', '#FFC107', '#C62828']; // Green -> Yellow -> Red (high is bad)

// Variables where higher values are worse
const NEGATIVE_VARS = [
  'fire_risk_index', 'flooding_risk', 'hydric_stress_r',
  'dengue', 'incidence_diarr', 'death_circ_mean', 'hosp_resp_mean',
  'vulnerabilidad', 'pct_pobreza', 'pollination_deficit',
  'idx_clima', 'idx_carga_enfermedad',
];

function getColor(value: number | null, terciles: [number, number], variable: string): string {
  if (value === null) return '#cccccc';

  const colors = NEGATIVE_VARS.includes(variable) ? NEGATIVE_COLORS : POSITIVE_COLORS;

  if (value <= terciles[0]) return colors[0];
  if (value <= terciles[1]) return colors[1];
  return colors[2];
}

// 3x3 bivariate color matrix (V1 row, V2 column)
// Low-Low is light, High-High is dark
const BIVARIATE_COLORS = [
  ['#e8e8e8', '#b5c0da', '#6c83b5'],  // V1 Low
  ['#b8d6be', '#90b2b3', '#567994'],  // V1 Med
  ['#73ae80', '#5a9178', '#2a5a5b'],  // V1 High
];

function getBivariateColor(
  v1: number | null,
  v2: number | null,
  t1: [number, number],
  t2: [number, number],
): string {
  if (v1 === null || v2 === null) return '#cccccc';

  const row = v1 <= t1[0] ? 0 : v1 <= t1[1] ? 1 : 2;
  const col = v2 <= t2[0] ? 0 : v2 <= t2[1] ? 1 : 2;

  return BIVARIATE_COLORS[row][col];
}

export default function MapViewer() {
  const mapRef = useRef<HTMLDivElement>(null);
  const geoJsonLayerRef = useRef<L.GeoJSON | null>(null);
  const zeeLayerRef = useRef<L.GeoJSON | null>(null);
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [choroplethData, setChoroplethData] = useState<ChoroplethData | null>(null);
  const [backgroundData, setBackgroundData] = useState<BackgroundData | null>(null);
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);

  const {
    layers,
    activeLayers,
    setHoveredMunicipalityCode,
    setSelectedMunicipality,
    group,
    layerOpacity,
    workshopMunicipalities,
    bivariateMode,
    bivariateData,
  } = useWorkshopStore();

  // Find background layer variable
  const backgroundLayer = layers.find(l => l.background);
  const backgroundVariable = backgroundLayer?.variable || null;

  // Fetch background layer data on mount
  useEffect(() => {
    if (!backgroundVariable) return;
    fetch(`/api/municipalities/background/${backgroundVariable}`)
      .then(res => {
        if (!res.ok) return null;
        return res.json();
      })
      .then(data => {
        if (data?.values) setBackgroundData(data);
      })
      .catch(() => setBackgroundData(null));
  }, [backgroundVariable]);

  // Get the first active and unlocked layer
  const activeLayerObj = activeLayers
    .map(id => layers.find(l => l.id === id))
    .find(layer => layer && (layer.isFree || group?.purchasedLayers?.includes(layer.id)));

  const activeVariable = activeLayerObj?.variable || null;
  const activeLayerId = activeLayerObj?.id || null;

  // Workshop municipality codes (6-digit)
  const workshopCodes = useMemo(
    () => new Set(workshopMunicipalities.map(m => m.code)),
    [workshopMunicipalities]
  );

  // Fetch choropleth data when active variable changes
  useEffect(() => {
    if (!activeVariable) {
      setChoroplethData(null);
      return;
    }

    if (!group?.id) {
      setChoroplethData(null);
      return;
    }

    fetch(`/api/municipalities/choropleth/${activeVariable}?group_id=${encodeURIComponent(group.id)}`)
      .then(res => {
        if (!res.ok) {
          console.warn(`[MapViewer] Choropleth returned ${res.status} for ${activeVariable}`);
          setChoroplethData(null);
          return null;
        }
        return res.json();
      })
      .then(data => {
        if (data && data.values) {
          setChoroplethData(data);
        }
      })
      .catch(err => {
        console.error('Failed to fetch choropleth data:', err);
        setChoroplethData(null);
      });
  }, [activeVariable, activeLayers, layers, group]);

  // Initialize map
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current || mapInstance) return;

    const initMap = async () => {
      const L = (await import('leaflet')).default;

      const map = L.map(mapRef.current!, {
        center: SP_CENTER,
        zoom: 7,
        minZoom: 6,
        maxZoom: 12,
        preferCanvas: true,
        maxBounds: [
          [SP_BOUNDS[0][0] - 1, SP_BOUNDS[0][1] - 1],
          [SP_BOUNDS[1][0] + 1, SP_BOUNDS[1][1] + 1],
        ],
      });

      // Base tile layer - supports offline mode via NEXT_PUBLIC_TILE_URL
      const tileBase = process.env.NEXT_PUBLIC_TILE_URL || 'https://{s}.basemaps.cartocdn.com';
      const isOffline = tileBase.includes('localhost') || tileBase.includes('127.0.0.1');
      L.tileLayer(isOffline
        ? `${tileBase}/tiles/light_nolabels/{z}/{x}/{y}.png`
        : `${tileBase}/light_nolabels/{z}/{x}/{y}{r}.png`, {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
      }).addTo(map);

      setMapInstance(map);

      // Load GeoJSON
      try {
        const response = await fetch('/geojson/sp_simplified.json');
        const data = await response.json();
        setGeoData(data);
      } catch (err) {
        console.error('Failed to load GeoJSON:', err);
      }

      // Load ZEE zone borders (always visible as background)
      try {
        const zeeRes = await fetch('/data/zee_zones.geojson');
        const zeeData = await zeeRes.json();
        const zeeLayer = L.geoJSON(zeeData, {
          style: {
            weight: 2,
            color: '#546E7A',
            fillOpacity: 0,
            dashArray: '',
            interactive: false,
          },
          pane: 'overlayPane',
        });
        zeeLayer.addTo(map);
        zeeLayerRef.current = zeeLayer;
      } catch (err) {
        console.error('Failed to load ZEE zones:', err);
      }

      // Labels layer on top (add after GeoJSON)
      L.tileLayer(isOffline
        ? `${tileBase}/tiles/light_only_labels/{z}/{x}/{y}.png`
        : 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
        pane: 'overlayPane',
        zIndex: 1000,
      }).addTo(map);

      setIsLoaded(true);
    };

    initMap();
  }, []);

  // Handle click on municipality
  const handleMunicipalityClick = useCallback(async (code: string) => {
    try {
      const res = await fetch(`/api/municipalities/${code}`);
      const data = await res.json();
      setSelectedMunicipality(data);
    } catch (err) {
      console.error('Failed to fetch municipality:', err);
    }
  }, [setSelectedMunicipality]);

  // Update GeoJSON layer when choropleth data changes
  useEffect(() => {
    if (!mapInstance || !isLoaded || !geoData) return;

    const L = window.L;
    if (!L) return;

    // Remove existing GeoJSON layer
    if (geoJsonLayerRef.current) {
      mapInstance.removeLayer(geoJsonLayerRef.current);
    }

    // Dynamic opacity from store (for the active layer)
    const currentOpacity = activeLayerId
      ? (layerOpacity[activeLayerId] ?? 0.75)
      : 0.7;

    // Create new GeoJSON layer - only color the 10 workshop municipalities
    const newGeoJsonLayer = L.geoJSON(geoData, {
      style: (feature) => {
        const fullCode = feature?.properties?.CD_MUN;
        const code = fullCode ? fullCode.substring(0, 6) : null;
        const isWorkshop = code ? workshopCodes.has(code) : false;

        // Non-workshop municipalities: background layer or light gray
        if (!isWorkshop) {
          if (backgroundData?.values && code) {
            const bgValue = backgroundData.values[code];
            return {
              weight: 0.5,
              color: '#999',
              fillOpacity: 0.25,
              fillColor: getBackgroundColor(bgValue),
            };
          }
          return {
            weight: 0.3,
            color: '#ccc',
            fillOpacity: 0.02,
            fillColor: '#f5f5f5',
          };
        }

        // Workshop municipalities: colored if data available
        if (bivariateMode && bivariateData && code) {
          const pair = bivariateData.values[code];
          const fillColor = pair
            ? getBivariateColor(pair[0], pair[1], bivariateData.terciles1 as [number, number], bivariateData.terciles2 as [number, number])
            : '#cccccc';
          return {
            weight: 1.5,
            color: '#333',
            fillOpacity: currentOpacity,
            fillColor,
          };
        }

        if (!choroplethData) {
          return {
            weight: 1.5,
            color: '#7B1FA2',
            fillOpacity: 0.15,
            fillColor: '#E1BEE7',
          };
        }

        const value = code && choroplethData.values ? choroplethData.values[code] : null;
        const fillColor = choroplethData.values && choroplethData.terciles
          ? getColor(value, choroplethData.terciles, choroplethData.variable)
          : '#cccccc';

        return {
          weight: 1.5,
          color: '#333',
          fillOpacity: currentOpacity,
          fillColor,
        };
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties;
        const code6 = props.CD_MUN ? props.CD_MUN.substring(0, 6) : null;
        const isWorkshop = code6 ? workshopCodes.has(code6) : false;

        // Only add interactivity to workshop municipalities
        if (!isWorkshop) return;

        layer.on({
          mouseover: () => {
            setHoveredMunicipalityCode(code6);
            (layer as L.Path).setStyle({
              weight: 3,
              color: '#7B1FA2',
              fillOpacity: Math.min(currentOpacity + 0.15, 1),
            });
            (layer as L.Path).bringToFront();
          },
          mouseout: () => {
            setHoveredMunicipalityCode(null);
            let fillColor = '#E1BEE7';
            let fillOpacity = 0.15;

            if (bivariateMode && bivariateData && code6) {
              const pair = bivariateData.values[code6];
              fillColor = pair
                ? getBivariateColor(pair[0], pair[1], bivariateData.terciles1 as [number, number], bivariateData.terciles2 as [number, number])
                : '#cccccc';
              fillOpacity = currentOpacity;
            } else if (choroplethData?.values && choroplethData?.terciles) {
              const value = choroplethData.values[code6!];
              fillColor = getColor(value, choroplethData.terciles, choroplethData.variable);
              fillOpacity = currentOpacity;
            }

            (layer as L.Path).setStyle({
              weight: 1.5,
              color: '#333',
              fillOpacity,
              fillColor,
            });
          },
          click: () => handleMunicipalityClick(code6!),
        });

        // Tooltip with value
        let tooltipContent = `<strong>${props.NM_MUN}</strong>`;
        if (choroplethData?.values && code6) {
          const value = choroplethData.values[code6];
          if (value !== null && value !== undefined) {
            tooltipContent += `<br/>${value.toFixed(2)}`;
          }
        }

        layer.bindTooltip(tooltipContent, {
          sticky: true,
          className: 'municipality-tooltip',
        });
      },
    }).addTo(mapInstance);

    geoJsonLayerRef.current = newGeoJsonLayer;

    // Add permanent name labels for the 10 workshop municipalities
    const labelLayerGroup = L.layerGroup();

    geoData.features.forEach((feature: GeoJSON.Feature) => {
      const fullCode = feature.properties?.CD_MUN;
      const code = fullCode ? fullCode.substring(0, 6) : null;
      if (!code || !workshopCodes.has(code)) return;

      // Calculate centroid from polygon
      const coords = feature.geometry;
      let lat = 0, lng = 0, count = 0;

      const processCoords = (ring: number[][]) => {
        ring.forEach(([x, y]) => { lng += x; lat += y; count++; });
      };

      if (coords.type === 'Polygon') {
        processCoords((coords as GeoJSON.Polygon).coordinates[0]);
      } else if (coords.type === 'MultiPolygon') {
        (coords as GeoJSON.MultiPolygon).coordinates.forEach(poly => processCoords(poly[0]));
      }

      if (count > 0) {
        const center: [number, number] = [lat / count, lng / count];
        const name = feature.properties?.NM_MUN || '';

        const label = L.marker(center, {
          icon: L.divIcon({
            className: 'workshop-label',
            html: `<span>${name}</span>`,
            iconSize: [0, 0],
            iconAnchor: [0, 0],
          }),
          interactive: false,
        });

        labelLayerGroup.addLayer(label);
      }
    });

    labelLayerGroup.addTo(mapInstance);

    // Cleanup: store label layer ref to remove it later
    return () => {
      mapInstance.removeLayer(labelLayerGroup);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapInstance, isLoaded, geoData, choroplethData, backgroundData, handleMunicipalityClick, setHoveredMunicipalityCode, workshopCodes, layerOpacity, activeLayerId, bivariateMode, bivariateData]);

  return (
    <div className="w-full h-full relative">
      <div ref={mapRef} className="w-full h-full bg-risk-map-bg" />

      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="animate-pulse text-gray-500">Carregando mapa...</div>
        </div>
      )}

      {/* Legend */}
      {bivariateMode && bivariateData ? (
        <div className="absolute bottom-4 left-4 z-[1000] bg-white p-3 rounded shadow-lg">
          <div className="text-xs font-semibold mb-2 text-gray-700">Mapa Bivariado</div>
          <div className="flex gap-2">
            {/* Y-axis label */}
            <div className="flex flex-col justify-between text-[10px] text-gray-500 pr-1">
              <span>Alto</span>
              <span>Baixo</span>
            </div>
            {/* 3x3 grid */}
            <div>
              <div className="grid grid-cols-3 gap-0.5">
                {[2, 1, 0].map(row => (
                  [0, 1, 2].map(col => (
                    <span
                      key={`${row}-${col}`}
                      className="w-5 h-5 rounded-sm"
                      style={{ backgroundColor: BIVARIATE_COLORS[row][col] }}
                    />
                  ))
                ))}
              </div>
              {/* X-axis label */}
              <div className="flex justify-between text-[10px] text-gray-500 mt-1">
                <span>Baixo</span>
                <span>Alto</span>
              </div>
            </div>
          </div>
          <div className="mt-2 space-y-0.5 text-[10px] text-gray-600">
            <div className="truncate">X: {bivariateData.layer1Name}</div>
            <div className="truncate">Y: {bivariateData.layer2Name}</div>
          </div>
        </div>
      ) : choroplethData?.values && choroplethData?.terciles ? (
        <div className="absolute bottom-4 left-4 z-[1000] bg-white p-3 rounded shadow-lg">
          <div className="text-xs font-semibold mb-2 text-gray-700">
            {layers.find(l => l.variable === choroplethData.variable)?.name || choroplethData.variable}
          </div>
          <div className="space-y-1">
            {(NEGATIVE_VARS.includes(choroplethData.variable) ?
              [
                { color: '#2E7D32', label: `Baixo (≤${choroplethData.terciles[0].toFixed(1)})` },
                { color: '#FFC107', label: `Médio` },
                { color: '#C62828', label: `Alto (>${choroplethData.terciles[1].toFixed(1)})` },
              ] : [
                { color: '#C62828', label: `Baixo (≤${choroplethData.terciles[0].toFixed(1)})` },
                { color: '#FFC107', label: `Médio` },
                { color: '#2E7D32', label: `Alto (>${choroplethData.terciles[1].toFixed(1)})` },
              ]
            ).map(({ color, label }) => (
              <div key={color + label} className="flex items-center gap-2">
                <span className="w-4 h-3 rounded" style={{ backgroundColor: color }} />
                <span className="text-xs text-gray-600">{label}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* PMVA background legend */}
      {backgroundData && (
        <div className="absolute bottom-4 right-4 z-[1000] bg-white/90 p-2 rounded shadow text-[10px]">
          <div className="font-semibold text-gray-600 mb-1">PMVA - Município VerdeAzul</div>
          {PMVA_LEGEND.map(({ label, color }) => (
            <div key={label} className="flex items-center gap-1.5">
              <span className="w-3 h-2.5 rounded-sm border border-black/20" style={{ backgroundColor: color, opacity: 0.5 }} />
              <span className="text-gray-500">{label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Map controls */}
      <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
        <button
          className="bg-white p-2 rounded shadow hover:bg-gray-50 transition"
          onClick={() => {
            const map = document.querySelector('.leaflet-container');
            if (map) {
              map.requestFullscreen?.();
            }
          }}
          title="Tela cheia (F)"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
            />
          </svg>
        </button>
      </div>

      <style jsx global>{`
        .municipality-tooltip {
          background: white;
          border: none;
          border-radius: 4px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          padding: 4px 8px;
          font-size: 12px;
          font-weight: 500;
        }
        .leaflet-container {
          background: var(--risk-map-bg);
        }
        .workshop-label {
          background: none !important;
          border: none !important;
          box-shadow: none !important;
        }
        .workshop-label span {
          display: block;
          white-space: nowrap;
          font-size: 11px;
          font-weight: 600;
          color: var(--risk-label-text);
          text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white;
          pointer-events: none;
        }
      `}</style>
    </div>
  );
}
