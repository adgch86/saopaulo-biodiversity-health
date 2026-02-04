'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useWorkshopStore } from '@/lib/store';
import { SP_CENTER, SP_BOUNDS } from '@/lib/types';

// Dynamic import to avoid SSR issues with Leaflet
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);
const ImageOverlay = dynamic(
  () => import('react-leaflet').then((mod) => mod.ImageOverlay),
  { ssr: false }
);
const GeoJSON = dynamic(
  () => import('react-leaflet').then((mod) => mod.GeoJSON),
  { ssr: false }
);

import 'leaflet/dist/leaflet.css';

interface GeoJSONFeature {
  type: 'Feature';
  properties: {
    CD_MUN: string;
    NM_MUN: string;
  };
  geometry: object;
}

export default function MapViewer() {
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [isClient, setIsClient] = useState(false);

  const {
    layers,
    activeLayers,
    layerOpacity,
    bivariateMode,
    bivariateImageUrl,
    setHoveredMunicipalityCode,
    setSelectedMunicipality,
    group,
  } = useWorkshopStore();

  useEffect(() => {
    setIsClient(true);
    // Load GeoJSON
    fetch('/geojson/sp_simplified.json')
      .then((res) => res.json())
      .then((data) => setGeoData(data))
      .catch((err) => console.error('Failed to load GeoJSON:', err));
  }, []);

  if (!isClient) {
    return (
      <div className="w-full h-full bg-gray-100 flex items-center justify-center">
        <div className="animate-pulse text-gray-500">Cargando mapa...</div>
      </div>
    );
  }

  const activeLayerData = activeLayers
    .map((id) => layers.find((l) => l.id === id))
    .filter(Boolean);

  const handleFeatureClick = async (feature: GeoJSONFeature) => {
    const code = feature.properties.CD_MUN;
    try {
      const res = await fetch(`/api/municipalities/${code}`);
      const data = await res.json();
      setSelectedMunicipality(data);
    } catch (err) {
      console.error('Failed to fetch municipality:', err);
    }
  };

  const onEachFeature = (feature: GeoJSONFeature, layer: L.Layer) => {
    layer.on({
      mouseover: () => {
        setHoveredMunicipalityCode(feature.properties.CD_MUN);
        (layer as L.Path).setStyle({
          weight: 2,
          color: '#7B1FA2',
          fillOpacity: 0.1,
        });
      },
      mouseout: () => {
        setHoveredMunicipalityCode(null);
        (layer as L.Path).setStyle({
          weight: 0.5,
          color: '#666',
          fillOpacity: 0,
        });
      },
      click: () => handleFeatureClick(feature),
    });

    layer.bindTooltip(feature.properties.NM_MUN, {
      sticky: true,
      className: 'municipality-tooltip',
    });
  };

  const geoJsonStyle = {
    weight: 0.5,
    color: '#666',
    fillOpacity: 0,
    fillColor: 'transparent',
  };

  // Check if layer is unlocked (free or purchased)
  const isLayerUnlocked = (layerId: string) => {
    const layer = layers.find((l) => l.id === layerId);
    if (!layer) return false;
    if (layer.isFree) return true;
    return group?.purchasedLayers.includes(layerId) ?? false;
  };

  return (
    <div className="w-full h-full relative">
      <MapContainer
        center={SP_CENTER}
        zoom={7}
        minZoom={6}
        maxZoom={12}
        className="w-full h-full"
        preferCanvas={true}
        maxBounds={[
          [SP_BOUNDS[0][0] - 1, SP_BOUNDS[0][1] - 1],
          [SP_BOUNDS[1][0] + 1, SP_BOUNDS[1][1] + 1],
        ]}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
        />

        {/* Bivariate overlay */}
        {bivariateMode && bivariateImageUrl && (
          <ImageOverlay url={bivariateImageUrl} bounds={SP_BOUNDS} opacity={0.85} />
        )}

        {/* Layer overlays */}
        {!bivariateMode &&
          activeLayerData.map(
            (layer) =>
              layer &&
              isLayerUnlocked(layer.id) && (
                <ImageOverlay
                  key={layer.id}
                  url={layer.imageUrl}
                  bounds={SP_BOUNDS}
                  opacity={layerOpacity[layer.id] ?? 0.75}
                />
              )
          )}

        {/* GeoJSON for interactivity */}
        {geoData && (
          <GeoJSON
            data={geoData}
            style={geoJsonStyle}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            onEachFeature={onEachFeature as any}
          />
        )}

        {/* Labels layer on top */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png"
          pane="shadowPane"
        />
      </MapContainer>

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
