'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useWorkshopStore } from '@/lib/store';
import { SP_CENTER, SP_BOUNDS } from '@/lib/types';

interface ChoroplethData {
  variable: string;
  values: Record<string, number | null>;
  terciles: [number, number];
  min: number;
  max: number;
}

// Color scales
const POSITIVE_COLORS = ['#C62828', '#FFC107', '#2E7D32']; // Red -> Yellow -> Green (low is bad)
const NEGATIVE_COLORS = ['#2E7D32', '#FFC107', '#C62828']; // Green -> Yellow -> Red (high is bad)

// Variables where higher values are worse
const NEGATIVE_VARS = [
  'fire_risk_index', 'flooding_risk', 'hydric_stress_r',
  'dengue', 'leishmaniose', 'incidence_diarr',
  'death_circ_mean', 'hosp_resp_mean',
  'vulnerabilidad', 'pct_pobreza', 'pollination_deficit'
];

function getColor(value: number | null, terciles: [number, number], variable: string): string {
  if (value === null) return '#cccccc';

  const colors = NEGATIVE_VARS.includes(variable) ? NEGATIVE_COLORS : POSITIVE_COLORS;

  if (value <= terciles[0]) return colors[0];
  if (value <= terciles[1]) return colors[1];
  return colors[2];
}

export default function MapViewer() {
  const mapRef = useRef<HTMLDivElement>(null);
  const geoJsonLayerRef = useRef<L.GeoJSON | null>(null);
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [choroplethData, setChoroplethData] = useState<ChoroplethData | null>(null);
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);

  const {
    layers,
    activeLayers,
    setHoveredMunicipalityCode,
    setSelectedMunicipality,
    group,
  } = useWorkshopStore();

  // Get the first active and unlocked layer's variable
  const activeVariable = activeLayers
    .map(id => layers.find(l => l.id === id))
    .find(layer => layer && (layer.isFree || group?.purchasedLayers.includes(layer.id)))
    ?.variable || null;

  // Fetch choropleth data when active variable changes
  useEffect(() => {
    console.log('[MapViewer] activeVariable changed:', activeVariable);
    console.log('[MapViewer] activeLayers:', activeLayers);
    console.log('[MapViewer] layers count:', layers.length);
    console.log('[MapViewer] group:', group?.id, 'purchasedLayers:', group?.purchasedLayers);

    if (!activeVariable) {
      setChoroplethData(null);
      return;
    }

    console.log('[MapViewer] Fetching choropleth for:', activeVariable);
    fetch(`/api/municipalities/choropleth/${activeVariable}`)
      .then(res => res.json())
      .then(data => {
        console.log('[MapViewer] Choropleth data received:', data.variable, 'values count:', Object.keys(data.values || {}).length);
        setChoroplethData(data);
      })
      .catch(err => console.error('Failed to fetch choropleth data:', err));
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

      // Base tile layer
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
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

      // Labels layer on top (add after GeoJSON)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
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

    // Create new GeoJSON layer with colors
    const newGeoJsonLayer = L.geoJSON(geoData, {
      style: (feature) => {
        if (!feature || !choroplethData) {
          return {
            weight: 0.5,
            color: '#666',
            fillOpacity: 0,
            fillColor: 'transparent',
          };
        }

        // GeoJSON uses 7-digit codes, API uses 6-digit codes
        const fullCode = feature.properties?.CD_MUN;
        const code = fullCode ? fullCode.substring(0, 6) : null;
        const value = code ? choroplethData.values[code] : null;
        const fillColor = getColor(value, choroplethData.terciles, choroplethData.variable);

        return {
          weight: 0.5,
          color: '#666',
          fillOpacity: 0.7,
          fillColor,
        };
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties;
        // GeoJSON uses 7-digit codes, API uses 6-digit codes
        const code6 = props.CD_MUN ? props.CD_MUN.substring(0, 6) : null;

        layer.on({
          mouseover: () => {
            setHoveredMunicipalityCode(code6);
            (layer as L.Path).setStyle({
              weight: 2,
              color: '#7B1FA2',
              fillOpacity: 0.85,
            });
            (layer as L.Path).bringToFront();
          },
          mouseout: () => {
            setHoveredMunicipalityCode(null);
            const value = choroplethData ? choroplethData.values[code6!] : null;
            const fillColor = choroplethData
              ? getColor(value, choroplethData.terciles, choroplethData.variable)
              : 'transparent';

            (layer as L.Path).setStyle({
              weight: 0.5,
              color: '#666',
              fillOpacity: choroplethData ? 0.7 : 0,
              fillColor,
            });
          },
          click: () => handleMunicipalityClick(code6!),
        });

        // Tooltip with value
        let tooltipContent = props.NM_MUN;
        if (choroplethData && code6) {
          const value = choroplethData.values[code6];
          if (value !== null && value !== undefined) {
            tooltipContent += `<br/><strong>${value.toFixed(2)}</strong>`;
          }
        }

        layer.bindTooltip(tooltipContent, {
          sticky: true,
          className: 'municipality-tooltip',
        });
      },
    }).addTo(mapInstance);

    geoJsonLayerRef.current = newGeoJsonLayer;
  }, [mapInstance, isLoaded, geoData, choroplethData, handleMunicipalityClick, setHoveredMunicipalityCode]);

  return (
    <div className="w-full h-full relative">
      <div ref={mapRef} className="w-full h-full" style={{ background: '#e5e7eb' }} />

      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="animate-pulse text-gray-500">Cargando mapa...</div>
        </div>
      )}

      {/* Legend */}
      {choroplethData && (
        <div className="absolute bottom-4 left-4 z-[1000] bg-white p-3 rounded shadow-lg">
          <div className="text-xs font-semibold mb-2 text-gray-700">
            {layers.find(l => l.variable === choroplethData.variable)?.name || choroplethData.variable}
          </div>
          <div className="space-y-1">
            {(NEGATIVE_VARS.includes(choroplethData.variable) ?
              [
                { color: '#2E7D32', label: `Bajo (≤${choroplethData.terciles[0].toFixed(1)})` },
                { color: '#FFC107', label: `Medio` },
                { color: '#C62828', label: `Alto (>${choroplethData.terciles[1].toFixed(1)})` },
              ] : [
                { color: '#C62828', label: `Bajo (≤${choroplethData.terciles[0].toFixed(1)})` },
                { color: '#FFC107', label: `Medio` },
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
          title="Pantalla completa (F)"
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
          background: #e5e7eb;
        }
      `}</style>
    </div>
  );
}
